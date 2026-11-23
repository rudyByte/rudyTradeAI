from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseStatus:
    status: str
    latency_ms: float | None = None
    detail: str | None = None


def check_database(database_url: str) -> DatabaseStatus:
    if not database_url:
        return DatabaseStatus("NOT_CONFIGURED", detail="DATABASE_URL is not configured")
    started = time.perf_counter()
    try:
        import psycopg
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            connection.execute("SELECT 1").fetchone()
        return DatabaseStatus("CONNECTED", round((time.perf_counter() - started) * 1000, 2))
    except Exception:
        return DatabaseStatus("DISCONNECTED", round((time.perf_counter() - started) * 1000, 2), "database check failed")
