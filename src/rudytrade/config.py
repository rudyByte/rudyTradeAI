from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class SafetyConfigurationError(ValueError):
    """Raised when a configuration would violate the paper-only boundary."""


def load_env_file(path: Path = Path(".env")) -> None:
    """Load KEY=VALUE pairs from a local .env without overriding real env vars."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key.removeprefix("export ").strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    if value.strip().lower() in {"1", "true", "yes", "on"}:
        return True
    if value.strip().lower() in {"0", "false", "no", "off"}:
        return False
    raise SafetyConfigurationError(f"Invalid boolean value: {value!r}")


@dataclass(frozen=True)
class Settings:
    paper_only: bool = True
    initial_capital: float = 5000.0
    db_path: Path = Path("data/rudytrade.sqlite3")
    log_level: str = "INFO"
    timezone: str = "Asia/Kolkata"
    live_trading_enabled: bool = False
    auto_upgrade: bool = False
    auto_paid_resource_creation: bool = False
    monthly_authorised_overage_inr: float = 0.0
    market_data_enabled: bool = False
    order_api_enabled: bool = False

    def __post_init__(self) -> None:
        if not self.paper_only:
            raise SafetyConfigurationError("PAPER_ONLY must remain true in the initial release")
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be positive")
        if self.live_trading_enabled or self.auto_upgrade or self.auto_paid_resource_creation:
            raise SafetyConfigurationError("Live trading, upgrades, and paid resource creation are disabled")
        if self.monthly_authorised_overage_inr != 0:
            raise SafetyConfigurationError("Monthly authorised overage must remain zero")
        if self.order_api_enabled:
            raise SafetyConfigurationError("ORDER_API_ENABLED must remain false")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            paper_only=_bool(os.getenv("PAPER_ONLY"), True),
            initial_capital=float(os.getenv("RUDYTRADE_INITIAL_CAPITAL", "5000")),
            db_path=Path(os.getenv("RUDYTRADE_DB_PATH", "data/rudytrade.sqlite3")),
            log_level=os.getenv("RUDYTRADE_LOG_LEVEL", "INFO").upper(),
            timezone=os.getenv("RUDYTRADE_TIMEZONE", "Asia/Kolkata"),
            live_trading_enabled=_bool(os.getenv("LIVE_TRADING_ENABLED"), False),
            auto_upgrade=_bool(os.getenv("AUTO_UPGRADE"), False),
            auto_paid_resource_creation=_bool(os.getenv("AUTO_PAID_RESOURCE_CREATION"), False),
            monthly_authorised_overage_inr=float(os.getenv("MONTHLY_AUTHORISED_OVERAGE_INR", "0")),
            market_data_enabled=_bool(os.getenv("MARKET_DATA_ENABLED"), False),
            order_api_enabled=_bool(os.getenv("ORDER_API_ENABLED"), False),
        )
