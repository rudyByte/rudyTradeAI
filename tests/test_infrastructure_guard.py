from datetime import datetime, timezone

from rudytrade.infrastructure_guard import GuardAction, InfrastructureGuard, UsageSnapshot


def snapshot(used, quota=100):
    return UsageSnapshot("test", "requests", used, quota, "calls", "test", True,
                         datetime.now(timezone.utc))


def test_thresholds_and_critical_path():
    guard = InfrastructureGuard()
    assert guard.evaluate(snapshot(70)).action == GuardAction.WARN
    assert guard.evaluate(snapshot(85)).action == GuardAction.RESTRICT
    assert guard.evaluate(snapshot(95)).action == GuardAction.BLOCK
    assert guard.evaluate(snapshot(95), critical=True).action == GuardAction.RESTRICT


def test_missing_quota_is_not_reported_as_zero():
    result = InfrastructureGuard().evaluate(UsageSnapshot(
        "x", "billing", 12, None, "INR", "manual", False, datetime.now(timezone.utc)))
    assert result.action == GuardAction.WARN
    assert "unavailable" in result.reason


def test_zero_default_budget_blocks_spend():
    assert InfrastructureGuard().approve_spend(0) is True
    assert InfrastructureGuard().approve_spend(0.01) is False
