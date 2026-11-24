from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BackendSettings:
    app_name: str = "RudyTrade-AI"
    app_env: str = "production"
    port: int = 8000
    database_url: str = ""
    database_url_direct: str = ""
    paper_only: bool = True
    live_trading_enabled: bool = False
    order_api_enabled: bool = False
    market_data_enabled: bool = False
    allowed_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "https://rudytrade-command-centre.vercel.app",
        "https://rudytrade-command-centre.reelpilot-ai-app.workers.dev",
    )

    @staticmethod
    def port_from_env() -> int:
        """Select Vertos port first, then standard PORT, then local fallback."""
        return int(os.getenv("SERVER_PORT") or os.getenv("PORT") or "8000")

    @classmethod
    def from_env(cls) -> "BackendSettings":
        configured_origins = os.getenv("ALLOWED_ORIGINS", "")
        origins = tuple(filter(None, configured_origins.split(","))) if configured_origins else cls.allowed_origins
        settings = cls(
            app_name=os.getenv("APP_NAME", "RudyTrade-AI"), app_env=os.getenv("APP_ENV", "production"),
            port=cls.port_from_env(), database_url=os.getenv("DATABASE_URL", ""),
            database_url_direct=os.getenv("DATABASE_URL_DIRECT", ""),
            paper_only=os.getenv("PAPER_ONLY", "true").lower() == "true",
            live_trading_enabled=os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true",
            order_api_enabled=os.getenv("ORDER_API_ENABLED", "false").lower() == "true",
            market_data_enabled=os.getenv("MARKET_DATA_ENABLED", "false").lower() == "true",
            allowed_origins=origins,
        )
        if not settings.paper_only or settings.live_trading_enabled or settings.order_api_enabled:
            raise ValueError("paper-only safety settings violated")
        return settings
