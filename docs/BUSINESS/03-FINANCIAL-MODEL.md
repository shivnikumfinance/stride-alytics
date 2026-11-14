# StrideAlytics — Cost Model

> **SCOPE (2026-11-14):** Personal use only. There is no revenue and no PRO or subscription tier. The default monthly spend is **$0** on free tiers. A paid API or service (for example a market-data feed) may be added later if needed; record it in the table below when it is. Free-tier limits change, so verify them against each vendor's pricing page.

## 1. Services and Free-Tier Limits

| Service | Use | Free-tier limit to respect |
|---------|-----|----------------------------|
| Supabase | Postgres and auth | ~500 MB database. Projects pause after about a week of inactivity. No managed backups. |
| Render | Backend API (FastAPI) | One instance, sleeps after ~15 min idle (30–60 s cold start), no autoscaling, no persistent disk. |
| Vercel (Hobby) | Frontend hosting | Non-commercial use, bandwidth cap. Fine for one user. |
| Streamlit Community Cloud | `alpha/` dashboard | Free for public repos, resource-limited. |
| GitHub Actions | Scheduler and CI | 2,000 minutes a month on private repos, unlimited on public repos. |
| Market data APIs | yfinance, Polygon, FMP | Rate-limited. Batch daily; yfinance is unofficial and can break without notice. |
| Notifications | Slack or Discord webhook | Free. |

Current total: **$0 per month.**

**Optional paid additions (none today):** record any paid API or service here, with its monthly cost and the free-tier limit that made it necessary.

| Service | Reason | Monthly cost |
|---------|--------|--------------|
| (none) | | |

## 2. Budget Rules

- Prefer free tiers. When a free limit is reached, first reduce usage: store less data, cache results, run fewer scheduled jobs.
- Add a paid API or service only when a free tier can't meet a real need (for example data quality or rate limits), and record it in the table above.
- Store only screened candidates and daily aggregates, not full option chains, and prune old rows on a schedule.
- Keep scheduled workflows within the Actions minute budget (see §3).
- Take your own database backup on a schedule (`pg_dump` in a GitHub Actions workflow), because free Supabase has no managed backups.

## 3. Usage Tracking

Check these monthly, or from a small scheduled script:

- Supabase database size (stay under ~400 MB).
- GitHub Actions minutes used (stay under ~1,500 on a private repo).
- Data API call counts against each provider's rate limit.
