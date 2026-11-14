# Pending items

Priority: **P1** = do next, **P2** = soon, **P3** = when convenient.
Delete an item when it is done and validated (see [README](README.md)).

---

## P1

### 1. Commit the current work
- Several changes are uncommitted: scope docs, `subscription_plan` removal (migration 006), auth/trade fixes, JWT audience, data-source labelling, alpha pipeline, workflow, mock-page banners, `AdminPage` deletion.
- Suggested commits: docs scope · plan removal · security + trade bugs · labelling · alpha + workflow · frontend demo banners.
- Done when: committed on a branch and CI is green.

### 2. Apply migrations 006 and 007 to Supabase
- `006_drop_subscription_plan.sql` and `007_persistence_logs.sql` (each with a `_down` file) are written but **not applied**. Apply 006 first, then 007, with `database/scripts/apply_migrations.{sh,ps1}`.
- Try them on a throwaway project first (see item 3).
- Done when: both are applied, login/portfolio/trades still work, and the smoke test passes (Validation V3, V13).

### 3. Validate persistence on real PostgreSQL
- Code is done (Phase 1): portfolios, trades, watchlists, settings and the append-only logs are stored through `backend/app/repositories/sql.py`; unit tests run on SQLite.
- **Render must have `DATABASE_URL` set.** Without it the backend silently uses in-memory SQLite and loses everything on restart (a warning is logged).
- Run `backend/scripts/smoke_db.py --disposable` against a throwaway Supabase project with migrations 007 applied; it proves the Postgres triggers make `signal_log` / `audit_events` append-only (SQLite cannot).
- Done when: the smoke test passes, and a trade survives a backend restart on the deployed API (Validation V2, V13).

### 4. Verify the daily workflow on GitHub
- `daily_run.yml` was fixed (`uv run`, secrets as env vars, failure alert) but never run from here.
- Add repo secrets: `SUPABASE_URL`, `SUPABASE_KEY`; optional `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEETS_SPREADSHEET_ID`, `SLACK_WEBHOOK_URL`, `DISCORD_WEBHOOK_URL`.
- Done when: a manual "Run workflow" succeeds and a forced failure produces an alert.

### 5. Test a real Supabase login end to end
- The JWT audience fix is unit-tested only. Confirm with a real token against the deployed API.
- If the project uses asymmetric JWT signing keys (not the HS256 secret), the verifier must change (JWKS).
- Done when: login in the frontend, then `/auth/me` and portfolio calls return 200.

## P2

### 6. Real data ingestion for alpha
- Nothing fetches fresh data: the run uses today's Supabase rows, then `alpha/raw_screener.csv`. `app/ingest.py` is not called anywhere.
- `ingest.py` also needs work: it targets up to 2000 tickers (not possible on free API tiers), `historicalVolatility` does not exist in yfinance so `hv_30d` is always null, it connects to Supabase at import time, and it pushes NaN values.
- Decide: a small watchlist universe, or a paid data API (record it in `../BUSINESS/03-FINANCIAL-MODEL.md`).
- Done when: the scheduled run produces today's rows without a manually updated CSV.

### 7. Clean up old duplicate rows in Supabase
- Earlier runs on the CSV/demo path stored timestamped dates and accumulated duplicates; only today's rows are replaced now.
- Options: run `alpha/reset_and_run.py` (clears everything) or delete rows older than today by hand.
- Done when: each table has one snapshot per day.

### 8. Protect the Streamlit dashboard
- It uses the service-role key and has no login, so anyone with the URL can see the data.
- Options: make the Streamlit app private (viewer auth), or use the anon key with a read-only RLS policy.
- Done when: an unauthenticated visitor cannot read the data.

### 9. Decide the fate of the demo pages
- Static pages with a "Demo data" banner: Exit Alerts, Active Holdings, Strategy Matrix, Watchlist, Active Trades, Weekly Picks, Heat Dashboard, Signal Log, Option Chain, Sizing (button does nothing), Scenarios.
- For each: build it on real data, or delete the page, route and sidebar link.
- Done when: no page shows static sample content.

### 10. Frontend auth gaps
- After a page reload the token is restored but `user` is not (`auth.store.ts` `hydrate`), so the sidebar email and Settings are empty. Call `/auth/me` on load.
- The refresh token is never used, so the session ends after about an hour.
- Token is kept in `localStorage`.
- `new URL(apiUrl)` in `api/client.ts` throws at import time on a bad `VITE_API_URL`.
- Done when: reload keeps the user and the session renews.

### 11. Backend hardening
- CORS defaults to `*` together with `allow_credentials=True` (`app/main.py`); set explicit origins.
- `/auth/refresh` takes the refresh token as a query parameter; move it to the request body.
- `market.py` uses Yahoo's v7 quote endpoint, which likely needs a crumb and so always returns the fallback values; switch the source or accept the label.
- Done when: each is fixed or consciously accepted and noted here.

### 17. Close the doc-vs-code gaps
- See [DOC-CODE-GAPS.md](DOC-CODE-GAPS.md). The stale facts were fixed; what remains is documented-but-unbuilt functionality (DNT gate, regime score, sizing, exit alerts, audit logs, watchlists, home hub).
- For each row decide: build it, or change the doc to match; then delete the row.
- Done when: `DOC-CODE-GAPS.md` is empty.

### 18. Table-name collisions between alpha and backend
- `alpha/app/supabase_schema.sql` defines `trades` and `audit_log` with different columns than the backend's `trades` (migration 002). In one Supabase project whichever is created first wins and the other silently breaks. The new backend audit table was named `audit_events` to avoid the second clash.
- Decide: separate Supabase projects/schemas for alpha and the backend, or rename alpha's tables (for example `alpha_trades`). Alpha's pipeline does not write `trades` today.
- Done when: both schemas can coexist (or are kept apart) and this is documented in `ALPHA.md`.

## P3

### 12. Spec and implementation mismatches
- The backend regime engine (bull/bear/ranging from a 30-day return) does not implement the documented 0–100 score (VIX, SPY 50/200 MA, IV Rank → DEFENSIVE/NORMAL/GROWTH).
- Alpha bands A–E are quality tiers by score; the docs define them as capital-allocation buckets with 30/25/20/15/10% caps.
- Alpha filters use a spread limit of 8%; DNT rule BR-017 says 10%.
- `alpha/app/business_logic.py` is dead code that treats spread as a fraction (`< 0.08`) while the real screener uses percent (`< 8`). Delete it or make it the single implementation.
- Done when: docs and code agree, or the docs are updated to match.

### 13. Alpha data robustness
- Missing values count silently as zero in `compute_option_score` (NaN compares false; `None` raises).
- Google Sheets push: ranges are capped at A–Z and 500 rows; `USER_ENTERED` can turn text from external data into formulas.
- `app/secrets_loader.py` is never called.
- `alpha/.env.example` exists locally but is not tracked in git, while the README tells people to copy it. Commit it (without secrets) or fix the README.
- Done when: bad inputs are rejected or reported, not scored as zero.

### 14. Test coverage
- Frontend has 17 unit tests (Phase 1: close-trade flow, watchlist, settings validation); pages added later still need them.
- CI now fails on test failures (it used to swallow them with `|| echo`); confirm the first run on GitHub is green.
- `mypy` is blocked by a Windows Application Control policy on this machine; run it in CI or another environment.
- No backend test hits real Supabase.
- Done when: key flows (login, add/close trade, screener) have frontend tests and mypy runs somewhere.

### 15. Leftovers from the plan and mobile removal
- `mobile/` still references `subscription_plan` (auth store, settings screen); deferred, but it will not match the API.
- Doc bodies still contain optional paid examples (`render.yaml` with `plan: standard`, the ~$84 cost table, SendGrid scripts) under a scope banner.
- `backend/render.yaml` uses `plan: starter` (a paid Render plan, about $7/month, no sleep). Decide: keep it, or switch to `free` (sleeps when idle). `APP_ENV` in that file is not used by the code (`ENVIRONMENT` is). `vercel.json` and the other workflows (`fetch-market-data`, `calculate-greeks`, `generate-weekly-picks`) are not yet reviewed for free-tier minute use.
- Existing Supabase auth users may still carry a `subscription_plan` in their metadata (ignored, harmless).
- Done when: configs match the free-tier defaults in `../BUSINESS/03-FINANCIAL-MODEL.md`.

### 16. Repository hygiene
- `.mcp.json` GitHub server fails to connect ("Incompatible auth server: does not support dynamic client registration").
- Confirm `alpha/service_account.json` is git-ignored (it exists locally; only `service_account.example.json` should be tracked).
- Done when: the MCP server connects or is removed, and the credential file is confirmed ignored.
