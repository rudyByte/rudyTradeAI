from __future__ import annotations

from fastapi import APIRouter, Request

from .database import check_database
from .services.cost_calculator import status as cost_status
from .services.health_monitor import process_status
from .services.paper_engine import paper_status

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict[str, object]:
    settings = request.app.state.settings
    return {"status": "HEALTHY", "app": settings.app_name, "paper_only": settings.paper_only}


@router.get("/api/status")
def status(request: Request) -> dict[str, object]:
    settings = request.app.state.settings
    return {"status": "HEALTHY", "paper_only": settings.paper_only, "live_trading_enabled": settings.live_trading_enabled, "order_api_enabled": settings.order_api_enabled, "market_data_enabled": settings.market_data_enabled, "process": process_status()}


@router.get("/api/database/health")
def database_health(request: Request) -> dict[str, object]:
    result = check_database(request.app.state.settings.database_url)
    return {"status": result.status, "latency_ms": result.latency_ms, "detail": result.detail}


@router.get("/api/dashboard/summary")
def dashboard_summary(request: Request) -> dict[str, object]:
    db = check_database(request.app.state.settings.database_url)
    return {"status": "CONNECTED" if db.status == "CONNECTED" else "DEGRADED", "source": "neon" if db.status == "CONNECTED" else "unavailable", "paper_only": True, "realized_pnl": None, "unrealized_pnl": None, "net_pnl_after_costs": None, "active_positions": None}


@router.get("/api/paper/status")
def paper_trading_status() -> dict[str, object]:
    return paper_status()


@router.get("/api/infrastructure/status")
def infrastructure_status(request: Request) -> dict[str, object]:
    return {"status": "CONNECTED", "provider_reported_metrics": False, "cpu_percent": None, "memory_percent": None, "message": "Provider resource metrics unavailable; no values fabricated", "database": check_database(request.app.state.settings.database_url).status, "cost_engine": cost_status()}
