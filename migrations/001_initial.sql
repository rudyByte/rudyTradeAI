CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS system_configuration (
    key TEXT PRIMARY KEY,
    value_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS market_instruments (
    id BIGSERIAL PRIMARY KEY, symbol TEXT NOT NULL, exchange TEXT NOT NULL,
    segment TEXT NOT NULL, metadata_json JSONB NOT NULL DEFAULT '{}',
    UNIQUE(exchange, symbol, segment)
);
CREATE TABLE IF NOT EXISTS market_candles (
    id BIGSERIAL PRIMARY KEY, instrument_id BIGINT NOT NULL REFERENCES market_instruments(id),
    timeframe TEXT NOT NULL, candle_at TIMESTAMPTZ NOT NULL, open_price NUMERIC NOT NULL,
    high_price NUMERIC NOT NULL, low_price NUMERIC NOT NULL, close_price NUMERIC NOT NULL,
    volume NUMERIC NOT NULL, UNIQUE(instrument_id, timeframe, candle_at)
);
CREATE INDEX IF NOT EXISTS idx_market_candles_lookup ON market_candles(instrument_id, timeframe, candle_at DESC);
CREATE TABLE IF NOT EXISTS trading_signals (
    id BIGSERIAL PRIMARY KEY, instrument_id BIGINT REFERENCES market_instruments(id),
    strategy TEXT NOT NULL, action TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL,
    reason TEXT NOT NULL, metadata_json JSONB NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS paper_orders (
    id BIGSERIAL PRIMARY KEY, client_order_id TEXT NOT NULL UNIQUE,
    instrument_id BIGINT NOT NULL REFERENCES market_instruments(id), side TEXT NOT NULL,
    order_type TEXT NOT NULL, quantity INTEGER NOT NULL, status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL, rejected_reason TEXT
);
CREATE TABLE IF NOT EXISTS paper_positions (
    id BIGSERIAL PRIMARY KEY, instrument_id BIGINT NOT NULL REFERENCES market_instruments(id),
    quantity INTEGER NOT NULL, average_price NUMERIC NOT NULL, status TEXT NOT NULL DEFAULT 'OPEN',
    opened_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS paper_trades (
    id BIGSERIAL PRIMARY KEY, position_id BIGINT NOT NULL REFERENCES paper_positions(id),
    gross_pnl NUMERIC, net_pnl NUMERIC, exit_reason TEXT, closed_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS news_articles (
    id BIGSERIAL PRIMARY KEY, source_url TEXT NOT NULL, publisher TEXT NOT NULL,
    headline TEXT NOT NULL, published_at TIMESTAMPTZ NOT NULL, raw_json JSONB NOT NULL DEFAULT '{}',
    UNIQUE(source_url, published_at, headline)
);
CREATE TABLE IF NOT EXISTS model_registry (
    id BIGSERIAL PRIMARY KEY, model_name TEXT NOT NULL, version TEXT NOT NULL,
    status TEXT NOT NULL, metrics_json JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMPTZ NOT NULL,
    UNIQUE(model_name, version)
);
CREATE TABLE IF NOT EXISTS daily_account_balances (
    account_date DATE PRIMARY KEY, starting_cash NUMERIC NOT NULL, ending_cash NUMERIC NOT NULL,
    equity NUMERIC NOT NULL, realized_pnl NUMERIC NOT NULL, charges NUMERIC NOT NULL
);
CREATE TABLE IF NOT EXISTS scheduled_job_logs (
    id BIGSERIAL PRIMARY KEY, job_name TEXT NOT NULL, run_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL, started_at TIMESTAMPTZ NOT NULL, finished_at TIMESTAMPTZ,
    details_json JSONB NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS infrastructure_usage (
    id BIGSERIAL PRIMARY KEY, service TEXT NOT NULL, metric TEXT NOT NULL,
    used_value NUMERIC NOT NULL, quota_value NUMERIC, unit TEXT NOT NULL, source TEXT NOT NULL,
    provider_reported BOOLEAN NOT NULL DEFAULT false, updated_at TIMESTAMPTZ NOT NULL,
    UNIQUE(service, metric, updated_at)
);
CREATE TABLE IF NOT EXISTS system_health (
    id BIGSERIAL PRIMARY KEY, component TEXT NOT NULL, status TEXT NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL, details_json JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_system_health_component ON system_health(component, checked_at DESC);
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY, event_type TEXT NOT NULL, event_at TIMESTAMPTZ NOT NULL,
    actor TEXT NOT NULL, details_json JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO system_configuration(key, value_json) VALUES
 ('safety', '{"PAPER_ONLY":true,"LIVE_TRADING_ENABLED":false,"ORDER_API_ENABLED":false,"AUTO_UPGRADE":false,"AUTO_PAID_RESOURCE_CREATION":false,"MONTHLY_AUTHORISED_OVERAGE_INR":0}'::jsonb),
 ('account', '{"initial_capital_inr":5000}'::jsonb)
ON CONFLICT (key) DO NOTHING;
INSERT INTO schema_migrations(version) VALUES (1) ON CONFLICT DO NOTHING;
