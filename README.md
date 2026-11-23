# RudyTrade AI

Paper-only, event-driven intraday trading research and simulation platform.

## Safety boundary

This repository does not place broker orders. `PAPER_ONLY=true` is mandatory in the initial release; any attempt to disable it raises an error. Broker authentication, live execution, and production self-modification are intentionally out of scope until separately approved and reviewed.

## Phase 1 quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
pytest
python -m rudytrade.cli init-db
```

See `docs/architecture.md` for the full architecture, feasibility reports, charge and protection specifications, data-source plan, RL plan, and implementation checklist.

## Current deployed endpoints

- API Worker: https://rudytrade-api.reelpilot-ai-app.workers.dev
- Frontend: https://rudytrade-command-centre.reelpilot-ai-app.workers.dev

Neon is the structured-data store. R2 is disabled. Angel One integration remains disabled until market-data credentials and broker requirements are verified.
