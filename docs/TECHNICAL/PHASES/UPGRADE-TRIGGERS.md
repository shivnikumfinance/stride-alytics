# StrideAlytics — Free-Tier Limits and Mitigations

**What to do when a free-tier limit gets close**

> **SCOPE (2026-11-14):** Personal use only, free tiers by default. When a limit is near, reduce usage first. If that isn't enough, a paid plan or API is an option (for example a market-data provider); record it in the [cost model](../../BUSINESS/03-FINANCIAL-MODEL.md). There is no PRO subscription tier. Verify limits against each vendor's current pricing page.

---

## 1. Supabase (database)

**Limit:** ~500 MB database. Projects pause after about a week of inactivity. No managed backups on free.

**Watch:** database size above ~400 MB.

**Mitigations:**
- Store only screened candidates and daily aggregates, not full option chains.
- Archive or delete rows older than a retention window (for example 90 days) with a scheduled job.
- Remove unused indexes and test data.
- Run a scheduled `pg_dump` from GitHub Actions as your own backup.
- Regular use (the daily pipeline and dashboard) keeps the project from pausing.

## 2. Render (backend API)

**Limit:** one instance, sleeps after ~15 minutes idle (30–60 s cold start), no autoscaling, no persistent disk, 512 MB memory.

**Mitigations:**
- Accept the cold start. It matters little for a single user.
- Precompute heavy work in the scheduled pipeline and serve stored results, instead of computing on request.
- Cache repeated calculations in the backend.
- Keep memory low: avoid loading large dataframes in the API process.
- Use `plan: free`, with no `numInstances` and no `disk` in `render.yaml`.

## 3. GitHub Actions (scheduler and CI)

**Limit:** 2,000 minutes a month on private repos, unlimited on public repos.

**Mitigations:**
- Run the health check every few hours, not every 30 minutes (every 30 minutes is about 1,440 minutes a month).
- Cache dependencies (`actions/setup-node` and `setup-python` caching, `uv` cache).
- Skip jobs when only docs changed, and run CI only for the module that changed.
- Cron runs in UTC, so market-hours schedules shift by an hour across daylight saving. Scheduled runs can also start late.

## 4. Vercel (frontend)

**Limit:** Hobby plan, non-commercial use, bandwidth cap. Personal use is within the terms.

**Mitigations:** code-split by route, lazy-load components, and keep bundles small.

## 5. Market data APIs

**Limit:** free tiers of Polygon and FMP are rate-limited; yfinance is unofficial and can break.

**Mitigations:**
- Fetch once a day in a batch, for a watchlist-sized universe.
- Cache responses and avoid re-fetching unchanged data.
- Keep a fallback (the local `raw_screener.csv` loader in `alpha/`).

## 6. Notifications

Use a Slack or Discord webhook. Email is not needed for a single user.

---

## Monthly check

- [ ] Supabase database size under ~400 MB
- [ ] GitHub Actions minutes under ~1,500 (private repo)
- [ ] Data API calls within provider rate limits
- [ ] Latest `pg_dump` backup exists
