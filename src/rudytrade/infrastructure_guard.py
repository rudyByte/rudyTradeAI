"""Provider-agnostic quota and spending protection."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class GuardAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    RESTRICT = "restrict"
    BLOCK = "block"


@dataclass(frozen=True)
class UsageSnapshot:
    service: str
    metric: str
    used: float
    quota: float | None
    unit: str
    source: str
    provider_reported: bool
    updated_at: datetime
    estimated_cost_inr: float | None = None

    @property
    def percentage_used(self) -> float | None:
        if self.quota is None or self.quota <= 0:
            return None
        return (self.used / self.quota) * 100

    @property
    def remaining(self) -> float | None:
        return None if self.quota is None else max(self.quota - self.used, 0)


@dataclass(frozen=True)
class GuardDecision:
    action: GuardAction
    reason: str
    critical: bool


class InfrastructureGuard:
    """Enforces local quota policy while preserving critical operations."""

    def __init__(self, monthly_budget_inr: float = 0.0, warning_at: float = 70.0,
                 restrict_at: float = 85.0, block_at: float = 95.0,
                 disable_at: float = 100.0) -> None:
        if monthly_budget_inr < 0:
            raise ValueError("monthly budget cannot be negative")
        self.monthly_budget_inr = monthly_budget_inr
        self.warning_at = warning_at
        self.restrict_at = restrict_at
        self.block_at = block_at
        self.disable_at = disable_at

    def evaluate(self, snapshot: UsageSnapshot, *, critical: bool = False) -> GuardDecision:
        pct = snapshot.percentage_used
        if pct is None:
            return GuardDecision(GuardAction.WARN, "quota unavailable; usage is not inventable", critical)
        if pct >= self.disable_at:
            return GuardDecision(GuardAction.BLOCK, "quota exhausted; optional service disabled", critical)
        if pct >= self.block_at:
            action = GuardAction.RESTRICT if critical else GuardAction.BLOCK
            return GuardDecision(action, "resource protection threshold reached", critical)
        if pct >= self.restrict_at:
            action = GuardAction.ALLOW if critical else GuardAction.RESTRICT
            return GuardDecision(action, "optional work restricted", critical)
        if pct >= self.warning_at:
            return GuardDecision(GuardAction.WARN, "resource usage warning", critical)
        return GuardDecision(GuardAction.ALLOW, "within configured quota", critical)

    def approve_spend(self, estimated_monthly_total_inr: float) -> bool:
        return estimated_monthly_total_inr <= self.monthly_budget_inr

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
