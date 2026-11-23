from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS instruments (id INTEGER PRIMARY KEY, symbol TEXT NOT NULL, exchange TEXT NOT NULL, segment TEXT NOT NULL, metadata_json TEXT NOT NULL DEFAULT '{}', UNIQUE(exchange, symbol, segment));
CREATE TABLE IF NOT EXISTS candles (id INTEGER PRIMARY KEY, instrument_id INTEGER NOT NULL REFERENCES instruments(id), timeframe TEXT NOT NULL, timestamp TEXT NOT NULL, open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL, volume REAL NOT NULL, UNIQUE(instrument_id, timeframe, timestamp));
CREATE TABLE IF NOT EXISTS options_contracts (id INTEGER PRIMARY KEY, instrument_id INTEGER NOT NULL REFERENCES instruments(id), underlying TEXT NOT NULL, expiry TEXT NOT NULL, strike REAL NOT NULL, option_type TEXT NOT NULL, lot_size INTEGER NOT NULL, metadata_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, source_url TEXT NOT NULL, publisher TEXT NOT NULL, headline TEXT NOT NULL, published_at TEXT NOT NULL, event_at TEXT, category TEXT, raw_json TEXT NOT NULL DEFAULT '{}', UNIQUE(source_url, published_at, headline));
CREATE TABLE IF NOT EXISTS news_sentiment (id INTEGER PRIMARY KEY, news_id INTEGER NOT NULL REFERENCES news(id), sentiment TEXT NOT NULL, relevance REAL, importance REAL, confidence REAL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY, instrument_id INTEGER NOT NULL REFERENCES instruments(id), strategy TEXT NOT NULL, action TEXT NOT NULL, created_at TEXT NOT NULL, reason TEXT NOT NULL, metadata_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, client_order_id TEXT NOT NULL UNIQUE, instrument_id INTEGER NOT NULL REFERENCES instruments(id), side TEXT NOT NULL, order_type TEXT NOT NULL, quantity INTEGER NOT NULL, status TEXT NOT NULL, paper_only INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, rejected_reason TEXT);
CREATE TABLE IF NOT EXISTS fills (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id), quantity INTEGER NOT NULL, price REAL NOT NULL, filled_at TEXT NOT NULL, slippage REAL NOT NULL DEFAULT 0, spread_cost REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS positions (id INTEGER PRIMARY KEY, instrument_id INTEGER NOT NULL REFERENCES instruments(id), quantity INTEGER NOT NULL, average_price REAL NOT NULL, opened_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'OPEN');
CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, position_id INTEGER NOT NULL REFERENCES positions(id), entry_fill_id INTEGER NOT NULL REFERENCES fills(id), exit_fill_id INTEGER, stop_loss REAL, take_profit REAL, gross_pnl REAL, net_pnl REAL, exit_reason TEXT, closed_at TEXT);
CREATE TABLE IF NOT EXISTS transaction_charges (id INTEGER PRIMARY KEY, trade_id INTEGER NOT NULL REFERENCES trades(id), charge_type TEXT NOT NULL, amount REAL NOT NULL, estimate INTEGER NOT NULL DEFAULT 1, config_version TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS daily_account_balances (date TEXT PRIMARY KEY, starting_cash REAL NOT NULL, ending_cash REAL NOT NULL, equity REAL NOT NULL, realized_pnl REAL NOT NULL, charges REAL NOT NULL);
CREATE TABLE IF NOT EXISTS strategy_configurations (name TEXT PRIMARY KEY, config_json TEXT NOT NULL, version TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS model_versions (id INTEGER PRIMARY KEY, model_name TEXT NOT NULL, version TEXT NOT NULL, status TEXT NOT NULL, artifact_uri TEXT, metrics_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS training_sessions (id INTEGER PRIMARY KEY, model_version_id INTEGER REFERENCES model_versions(id), started_at TEXT NOT NULL, finished_at TEXT, dataset_version TEXT, config_json TEXT NOT NULL DEFAULT '{}', metrics_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS backtesting_results (id INTEGER PRIMARY KEY, strategy TEXT NOT NULL, dataset_version TEXT NOT NULL, started_at TEXT NOT NULL, metrics_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS system_health (id INTEGER PRIMARY KEY, component TEXT NOT NULL, status TEXT NOT NULL, checked_at TEXT NOT NULL, details_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, event_type TEXT NOT NULL, event_at TEXT NOT NULL, actor TEXT NOT NULL, details_json TEXT NOT NULL DEFAULT '{}');
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(path: Path) -> None:
    with connect(path) as connection:
        connection.executescript(SCHEMA)
        connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (1)")
