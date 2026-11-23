"""Optional cloud connectivity checks for Neon Postgres and Cloudflare R2.

Credentials are read from the environment only. Nothing in this module logs or
returns secret values; any secret that appears in a provider error message is
redacted before the message is surfaced.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlsplit

CLOUDFLARE_API = "https://api.cloudflare.com/client/v4"
R2_BUCKETS_PATH = "/r2/buckets"


class CloudConfigurationError(RuntimeError):
    """Raised when a required cloud setting is missing or unusable."""


@dataclass(frozen=True)
class CloudStatus:
    service: str
    ok: bool
    detail: str


def _setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise CloudConfigurationError(f"{name} is not set")
    return value


def _redact(text: str, *secrets: str) -> str:
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[redacted]")
    return text


def database_url() -> str:
    return _setting("DATABASE_URL")


def _database_secrets(url: str) -> tuple[str, ...]:
    parts = urlsplit(url)
    return (parts.password or "",)


def postgres_connection():
    """Open a psycopg connection to DATABASE_URL (Neon requires TLS)."""
    try:
        import psycopg
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on extras
        raise CloudConfigurationError(
            'psycopg is not installed; run pip install -e ".[cloud]"'
        ) from exc
    return psycopg.connect(database_url())


def check_postgres() -> CloudStatus:
    try:
        url = database_url()
        with postgres_connection() as connection:
            row = connection.execute(
                "select current_database(), current_user, split_part(version(), ',', 1)"
            ).fetchone()
        detail = f"connected as {row[1]} to {row[0]} ({row[2]})"
        return CloudStatus("neon-postgres", True, detail)
    except CloudConfigurationError as exc:
        return CloudStatus("neon-postgres", False, str(exc))
    except Exception as exc:  # noqa: BLE001 - provider errors are reported verbatim
        secrets = ()
        try:
            secrets = _database_secrets(database_url())
        except CloudConfigurationError:
            pass
        return CloudStatus(
            "neon-postgres", False, _redact(f"{type(exc).__name__}: {exc}", *secrets)
        )


def _cloudflare_get(path: str, token: str) -> dict:
    request = urllib.request.Request(
        f"{CLOUDFLARE_API}{path}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def check_cloudflare_r2() -> CloudStatus:
    token = ""
    try:
        token = _setting("CLOUDFLARE_API_TOKEN")
        account_id = _setting("CLOUDFLARE_ACCOUNT_ID")
        accounts = _cloudflare_get("/accounts", token)
        if accounts.get("success") is False:
            return CloudStatus("cloudflare-r2", False, "token was rejected by Cloudflare")
        if account_id not in {a.get("id") for a in accounts.get("result") or []}:
            return CloudStatus(
                "cloudflare-r2", False, "token cannot see CLOUDFLARE_ACCOUNT_ID"
            )
        buckets = _cloudflare_get(f"/accounts/{account_id}{R2_BUCKETS_PATH}", token)
        if not buckets.get("success"):
            errors = buckets.get("errors") or []
            message = errors[0].get("message") if errors else "request failed"
            return CloudStatus("cloudflare-r2", False, str(message))
        names = [bucket.get("name", "?") for bucket in buckets.get("result", [])]
        listed = ", ".join(names) if names else "no buckets created yet"
        return CloudStatus("cloudflare-r2", True, f"account reachable; buckets: {listed}")
    except CloudConfigurationError as exc:
        return CloudStatus("cloudflare-r2", False, str(exc))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            errors = json.loads(body).get("errors") or []
            message = errors[0].get("message") if errors else f"HTTP {exc.code}"
        except json.JSONDecodeError:
            message = f"HTTP {exc.code}"
        return CloudStatus("cloudflare-r2", False, _redact(str(message), token))
    except Exception as exc:  # noqa: BLE001 - network errors are reported verbatim
        return CloudStatus("cloudflare-r2", False, _redact(f"{type(exc).__name__}: {exc}", token))


def check_all() -> list[CloudStatus]:
    return [check_postgres(), check_cloudflare_r2()]
