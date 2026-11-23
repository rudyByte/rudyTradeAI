# Vertos deployment preparation

Backend entry point: `app.py`.

Requirements file: `requirements.txt`.

Vertos settings:

```text
Git repository: https://github.com/rudyByte/rudyTradeAI.git
Branch: main
App py file: app.py
Requirements file: requirements.txt
Python image: ghcr.io/parkervcp/yolks:python_3.12
RAM: 256 MiB
CPU: 100%
Storage: 4 GiB
```

Startup command:

```text
python app.py
```

`app.py` binds to `0.0.0.0` and uses `PORT` when supplied. It performs no heavy initialization and loads no ML models.

Required environment variables:

```text
APP_NAME=RudyTrade-AI
APP_ENV=production
PORT=8000
DATABASE_URL=<Neon pooled URL>
DATABASE_URL_DIRECT=<Neon direct URL, optional>
ALLOWED_ORIGINS=https://rudytrade-command-centre.vercel.app,https://rudytrade-command-centre.reelpilot-ai-app.workers.dev
PAPER_ONLY=true
LIVE_TRADING_ENABLED=false
ORDER_API_ENABLED=false
MARKET_DATA_ENABLED=false
```

Angel One variables remain blank. Do not add them until market-data requirements are verified.

Endpoints:

- `GET /health`
- `GET /api/status`
- `GET /api/database/health`
- `GET /api/dashboard/summary`
- `GET /api/paper/status`
- `GET /api/infrastructure/status`

No order endpoints exist. CPU, memory, provider billing, and market values report unavailable when not provided by the host; nothing is fabricated. RL training, heavy backtesting, and broker WebSockets do not belong on the 256 MiB instance.
