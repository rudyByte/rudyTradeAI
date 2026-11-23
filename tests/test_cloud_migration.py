from pathlib import Path


def test_neon_migration_contains_safety_and_core_tables():
    sql = (Path(__file__).parents[1] / "migrations" / "001_initial.sql").read_text()
    assert "paper_positions" in sql
    assert "daily_account_balances" in sql
    assert '"PAPER_ONLY":true' in sql
    assert '"ORDER_API_ENABLED":false' in sql
