# RudyTrade Worker

Paper-only API scaffold. No order routes exist.

```powershell
npm install
npm run typecheck
npx wrangler dev
```

Production secrets:

```powershell
npx wrangler secret put DATABASE_URL
npx wrangler secret put API_AUTH_TOKEN
```

Do not put secrets in frontend code. `DATABASE_URL` must point to Neon. Run SQL migration from repository root before using `/api/overview`.
