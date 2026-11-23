# RudyTrade AI Phase 1 architecture and feasibility baseline

Status: initial local foundation, paper-only. This is an engineering plan, not investment or regulatory advice.

## 1. Detailed architecture

```text
Market adapters (Angel SmartAPI / historical files / mock feed)
        -> normalizer + freshness checks -> feature pipeline
        -> strategy selector -> independent risk/capital engine
        -> paper execution simulator -> fills/positions/trades/charges
        -> SQLite now / PostgreSQL later -> Streamlit dashboard and reports

News adapters -> deduplication -> sentiment/relevance/event-risk features
Research worker (offline) -> walk-forward evaluation -> versioned model registry
Health, audit and recovery services span every component.
```

Boundaries: adapters never place orders in Phase 1; strategies can propose signals but cannot mutate limits; the risk engine can reject every proposal; the simulator records gaps, slippage, spreads, partial fills and rejection reasons; research runs out-of-process and cannot change safeguards.

Recommended deployment: Streamlit or a separate frontend for UI; authenticated API; one always-on Dockerized paper worker; PostgreSQL/Supabase for durable cloud state; object storage for datasets/models; scheduled research worker; GitHub CI. Vercel/Cloudflare Workers are suitable for frontend/API edges, not a persistent Python trading process.

## 2. Dependency list

Phase 1 runtime is intentionally standard-library only: Python 3.10+, SQLite, `logging`, `dataclasses`, and `argparse`.

Planned, isolated dependencies:

| Area | Packages | Purpose |
|---|---|---|
| Broker | `smartapi-python`, `pyotp`, `websocket-client` | Angel authentication, REST/WebSocket market data; paper adapter only |
| Data | `numpy`, `pandas`, `pyarrow` | tabular and columnar market/news datasets |
| Indicators | `pandas-ta` or tested internal implementations | VWAP, EMA, ATR, RSI and volume features |
| Research | `scikit-learn`, `torch`, `stable-baselines3`, `gymnasium`, `optuna` | supervised/RL experiments and tuning |
| UI | `streamlit`, `plotly` | dashboard and charts |
| Cloud DB | `psycopg[binary]` or SQLAlchemy | PostgreSQL migration |
| Testing | `pytest`, property-based tests later | unit, integration and invariant tests |

Pin and audit production dependencies; do not allow research dependencies to block the paper worker.

## 3. Cloud feasibility report

Feasible for paper trading with a small always-on VM/container, managed PostgreSQL, object storage and a separately scheduled research job. Cost and availability are provider- and region-dependent. Oracle Cloud Always Free can be investigated, but capacity, quotas, account verification and uptime are not guaranteed. Free tiers may sleep, throttle, cap egress/storage, or lack support; therefore they are not a reliability guarantee.

No paid infrastructure should be enabled without explicit approval. A production design needs health checks, restart policy, persistent logs, backups, alerting, secrets management, clock/time-zone discipline, market-session scheduling and WebSocket reconnect logic. Paper state must survive process restart. Live trading is a separate future compliance project.

## 4. Angel One integration feasibility report

SmartAPI can be used as a market-data adapter after account/API access, current terms, instrument-token metadata and rate limits are verified. The adapter must normalize timestamps to IST, validate stale data, persist raw/normalized events, reconnect safely, and expose no live-order method to the paper runtime. Credentials belong only in a secret manager/environment and never in logs.

Angel One’s published pricing says equity intraday brokerage is lower of ₹20 or 0.1% per executed order with a ₹5 minimum, and F&O brokerage is ₹20 per executed order after applicable offers; the official tariff is subject to change. Treat web-published values as versioned configuration requiring confirmation before each production release. See [Angel One brokerage charges](https://www.angelone.in/support/charges-and-cashbacks/brokerage-charges) and [Angel One tariff/transaction charges](https://www.angelone.in/exchange-transaction-charges).

Before any live capability, separately verify broker approval, API order restrictions, static-IP requirements, algo tagging, rate limits, exchange registration/operational modalities and account-level permissions. SEBI’s February 4, 2025 circular and NSE operational material indicate the retail-algo framework applies from April 1, 2026; this repository remains paper-only and does not infer compliance from cloud deployment. See [SEBI circular](https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html) and [NSE retail-algo FAQ](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail_Algo_03112025_NSE.pdf).

## 5. Charge-calculation specification

Charges are calculated per execution and stored by `trade_id`, `charge_type`, `amount`, `estimate`, and `config_version`. Entry and exit estimates reserve capital before acceptance; actual partial fills are reconciled after each fill. Net P&L is gross P&L less brokerage, STT, exchange transaction charges, SEBI charges, IPFT where applicable, stamp duty, GST on taxable service components, slippage and spread cost.

Segment-specific configuration is required for NSE equity intraday, delivery, index options and stock options. Do not apply one rate table to all segments. Brokerage is per executed order, not merely a percentage of round-trip turnover; order/contract category and broker plan matter. GST must not be applied to STT or stamp duty. Unknown or stale rates set `estimate=true` and block any “fully verified” label.

The charge engine must be pure and unit-tested against versioned fixtures and later manually reconciled with Angel One contract notes. A daily report totals estimated versus actual charges and flags configuration gaps.

## 6. Negative-balance protection specification

The independent protection engine receives account state, open/outstanding exposure, instrument metadata, proposed quantity/price, estimated entry/exit charges, slippage/spread assumptions and circuit-breaker state. It rejects unless cash remains non-negative, lot size is valid, worst-case exposure fits capital, planned loss fits the 0.5% risk budget, daily loss remains below 1%, open positions/trades/consecutive-loss rules pass, data is fresh and the instrument is permitted.

Hard invariants: no borrowing, no naked option selling, no averaging down, no martingale, one unresolved position maximum, and no new positions after any active circuit breaker. Actual gap/slippage execution may exceed planned loss; the system records planned risk, worst-case estimate, realised risk and actual net P&L separately. Emergency shutdown cancels simulated pending entries and attempts orderly exits in the simulator.

## 7. News-data source plan

Primary connectors: NSE/BSE announcements, RBI publications, government/PIB releases, SEBI/NSE notices, licensed financial-news APIs, and reputable RSS feeds. Store URL, publisher, publication timestamp, event timestamp, category, related instruments, sentiment, relevance, importance, reliability and uncertainty. Use IST for normalized timestamps while preserving source timezone.

Implement URL/headline/time deduplication, freshness limits, source reliability configuration, rate-limit handling and explicit unavailable-data state. Respect terms, API limits, copyright and licensing; do not scrape restricted content or bypass paywalls. News is a filter/regime/volatility feature, never a standalone buy/sell rule. Compare technical-only versus news-filtered results out-of-sample.

## 8. Reinforcement-learning research plan

Create a Gymnasium environment with OHLCV, indicators, volatility, relative volume, regime, news features, position, capital, unrealized P&L, option premium and spread. Actions are HOLD, ENTER_LONG, permitted ENTER_SHORT, EXIT and REDUCE_POSITION. The environment calls the same charge and protection logic as paper execution.

Start with PPO in Stable-Baselines3; use PyTorch and Optuna only in an isolated research worker. Reward net P&L after costs with drawdown, exposure, turnover and overtrading penalties. Use time-based train/validation/test splits, walk-forward validation, leakage checks, seed tracking, baselines and ablations. Promote only a versioned candidate with positive out-of-sample expectancy after costs and paper shadow validation. Keep rollback artifacts. The model cannot alter safeguards, charges, authentication or order validation.

## 9. Phase-wise implementation checklist

- [x] Phase 1: project structure, configuration, logging, SQLite schema, paper-only guard, tests.
- [ ] Phase 2: Angel market-data adapter, instrument metadata, freshness/reconnect tests.
- [ ] Phase 3: indicators, three independent strategies, selector and no-trade outcome.
- [ ] Phase 4: capital protection, sizing, circuit breakers and versioned charge engine.
- [ ] Phase 5: event-driven paper simulator, gaps, partial fills, duplicate prevention and restart recovery.
- [ ] Phase 6: historical equity/options backtesting, walk-forward and net-cost metrics.
- [ ] Phase 7: news adapters, dedupe, sentiment/event-risk features and audit UI.
- [ ] Phase 8: isolated supervised/RL lab, model registry and rollback.
- [ ] Phase 9: authenticated Streamlit dashboard and reports.
- [ ] Phase 10: Docker/cloud deployment, health, backup, monitoring and cost gates.
- [ ] Phase 11: automated paper trading across market sessions.
- [ ] Phase 12: reliability, load, recovery, security and performance validation.

External prerequisites: Angel One account and permitted API access; verified instrument/option metadata; licensed or permitted data/news sources; historical option quotes with actual premiums and spreads; cloud account and storage; domain/authentication/secrets; and explicit approval before any paid resource. Free tiers do not guarantee continuous operation.

## 10. Acceptance gates

No live order code is enabled by this baseline. Extended paper trading requires all requested invariants, restart persistence, net-cost accounting, stale-data rejection, news auditability, model versioning, recovery tests, and positive out-of-sample expectancy after realistic costs. A 95% win rate is never promised.
