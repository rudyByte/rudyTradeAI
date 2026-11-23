import { neon } from '@neondatabase/serverless';

export interface Env {
  DATABASE_URL?: string;
  API_AUTH_TOKEN?: string;
  PAPER_ONLY: string;
  LIVE_TRADING_ENABLED: string;
  ORDER_API_ENABLED: string;
}

const headers = { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' };
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers });

function authorized(request: Request, env: Env): boolean {
  return !env.API_AUTH_TOKEN || request.headers.get('authorization') === `Bearer ${env.API_AUTH_TOKEN}`;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === 'OPTIONS') return new Response(null, { headers: { ...headers, 'access-control-allow-methods': 'GET,OPTIONS', 'access-control-allow-headers': 'authorization,content-type' } });
    if (!authorized(request, env)) return json({ error: 'unauthorized' }, 401);
    const url = new URL(request.url);
    if (url.pathname === '/api/health') return json({ status: 'healthy', paperOnly: env.PAPER_ONLY === 'true', liveTradingEnabled: false, checkedAt: new Date().toISOString() });
    if (url.pathname === '/api/overview') {
      if (!env.DATABASE_URL) return json({ available: false, reason: 'DATABASE_URL is not configured' });
      try {
        const sql = neon(env.DATABASE_URL);
        const rows = await sql`SELECT account_date, equity, realized_pnl FROM daily_account_balances ORDER BY account_date DESC LIMIT 1`;
        const positions = await sql`SELECT count(*)::int AS count FROM paper_positions WHERE status = 'OPEN'`;
        return json({ available: true, source: 'neon', updatedAt: new Date().toISOString(), capital: rows[0]?.equity ?? null, dailyPnl: rows[0]?.realized_pnl ?? null, activePositions: positions[0]?.count ?? null, model: null });
      } catch { return json({ available: false, reason: 'database query unavailable' }, 503); }
    }
    if (url.pathname === '/api/usage') {
      if (!env.DATABASE_URL) return json({ available: false, reason: 'DATABASE_URL is not configured' });
      try {
        const sql = neon(env.DATABASE_URL);
        const rows = await sql`SELECT service, metric, used_value, quota_value, unit, source, provider_reported, updated_at FROM infrastructure_usage ORDER BY updated_at DESC LIMIT 100`;
        return json({ available: true, source: 'neon', rows });
      } catch { return json({ available: false, reason: 'usage data unavailable' }, 503); }
    }
    if (url.pathname === '/api/logs') {
      if (!env.DATABASE_URL) return json({ available: false, reason: 'DATABASE_URL is not configured' });
      try {
        const sql = neon(env.DATABASE_URL);
        const rows = await sql`SELECT job_name, run_key, status, started_at, finished_at, details_json FROM scheduled_job_logs ORDER BY started_at DESC LIMIT 50`;
        return json({ available: true, source: 'neon', rows });
      } catch { return json({ available: false, reason: 'log data unavailable' }, 503); }
    }
    return json({ error: 'not_found' }, 404);
  },
  async scheduled(controller: ScheduledController, env: Env, ctx: ExecutionContext): Promise<void> {
    if (!env.DATABASE_URL) return;
    ctx.waitUntil((async () => {
      const sql = neon(env.DATABASE_URL!);
      const runKey = `infrastructure-check:${new Date(controller.scheduledTime).toISOString()}`;
      await sql`INSERT INTO scheduled_job_logs(job_name, run_key, status, started_at, finished_at, details_json) VALUES ('infrastructure-check', ${runKey}, 'completed', now(), now(), ${JSON.stringify({ paperOnly: true })}::jsonb) ON CONFLICT (run_key) DO NOTHING`;
    })());
  },
};
