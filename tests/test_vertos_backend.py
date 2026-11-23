import os

from backend.config import BackendSettings
from backend.database import check_database


def test_vertos_safety_defaults_are_locked(monkeypatch):
    for key in ("PAPER_ONLY", "LIVE_TRADING_ENABLED", "ORDER_API_ENABLED", "MARKET_DATA_ENABLED"):
        monkeypatch.delenv(key, raising=False)
    settings = BackendSettings.from_env()
    assert settings.paper_only is True
    assert settings.live_trading_enabled is False
    assert settings.order_api_enabled is False
    assert settings.market_data_enabled is False


def test_database_missing_is_explicit():
    status = check_database("")
    assert status.status == "NOT_CONFIGURED"


def test_no_order_routes_exposed():
    from app import create_app
    paths = {route.path for route in create_app().routes}
    assert "/health" in paths
    assert "/api/status" in paths
    assert not any("order" in path.lower() for path in paths)
