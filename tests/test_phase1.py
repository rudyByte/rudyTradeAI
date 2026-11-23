import sqlite3

import pytest

from rudytrade.config import SafetyConfigurationError, Settings
from rudytrade.db import initialize, connect


def test_default_is_paper_only():
    assert Settings().paper_only is True


def test_live_mode_is_rejected(monkeypatch):
    monkeypatch.setenv("PAPER_ONLY", "false")
    with pytest.raises(SafetyConfigurationError):
        Settings.from_env()


def test_invalid_capital_is_rejected():
    with pytest.raises(ValueError):
        Settings(initial_capital=0)


def test_database_schema_and_foreign_keys(tmp_path):
    path = tmp_path / "nested" / "paper.sqlite3"
    initialize(path)
    with connect(path) as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"orders", "fills", "positions", "trades", "transaction_charges", "audit_logs"} <= tables
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO fills(order_id, quantity, price, filled_at) VALUES (999, 1, 1, 'x')")


def test_schema_initialization_is_idempotent(tmp_path):
    path = tmp_path / "paper.sqlite3"
    initialize(path)
    initialize(path)
    with connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 1
