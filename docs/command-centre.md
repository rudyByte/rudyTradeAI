# Command Centre and Infrastructure Guard extension

The frontend lives in `frontend/` and is a Vite/React/TypeScript shell with responsive dark-mode navigation for all requested modules. It requests `/api/overview`; if that endpoint is unavailable, every metric is explicitly shown as unavailable. No simulated or live values are invented. The UI carries a persistent `PAPER ONLY` marker and does not expose order execution.

`src/rudytrade/infrastructure_guard.py` is independent of the dashboard. It evaluates provider-reported or manually configured usage snapshots at 70%, 85%, 95%, and 100%. Unknown quotas produce a warning rather than a fabricated zero. Critical operations receive a less aggressive decision at the blocking threshold so position-management safety can be preserved. Optional work must be blocked first by the eventual scheduler.

The zero-default spending budget rejects any estimated paid usage. The application cannot prevent charges created directly in a provider console or by another application; provider-side billing caps or disabled pay-as-you-go settings remain required. No automatic plan upgrades, paid resource creation, or live trading are enabled by this extension.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The API adapter and WebSocket transport are intentionally deferred until the backend service contract is implemented. The next integration phase should provide authenticated `/api/overview`, `/api/health`, `/api/usage`, and a WebSocket stream with source, timestamp, and freshness metadata on every value.

## Cloud migration status

Neon migration `001_initial.sql` creates the core paper-trading, market, news, model, scheduled-job, infrastructure, health, and audit tables. The migration is applied idempotently through `rudytrade migrate-neon`. Cloudflare R2 is intentionally not configured. The Worker scaffold in `worker/` exposes only health and read-only overview endpoints; no order endpoint exists.
