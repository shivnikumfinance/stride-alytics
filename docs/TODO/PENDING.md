# Pending items

Priority: **P1** = do next, **P2** = soon, **P3** = when convenient.
Delete an item when it is done and validated (see [README](README.md)).

---

## P1

### 1. Commit the current work
- Several changes are uncommitted: scope docs, `subscription_plan` removal (migration 006), auth/trade fixes, JWT audience, data-source labelling, alpha pipeline, workflow, mock-page banners, `AdminPage` deletion.
- Suggested commits: docs scope · plan removal · security + trade bugs · labelling · alpha + workflow · frontend demo banners.
- Done when: committed on a branch and CI is green.

### 2. Apply migrations 006 to 009 to Supabase
- `006_drop_subscription_plan.sql`, `007_persistence_logs.sql`, `008_market_regime.sql` and `009_alert_acks.sql` (each with a `_down` file) are written but **not applied**. Apply them in order with `database/scripts/apply_migrations.{sh,ps1}`.
- **None of them has been applied anywhere yet**, including 008 (`market_regime`) and 009 (`alert_acks`). Try all four on a throwaway Supabase project first (see item 3), including each `_down` file once.
- Done when: all four are applied, login/portfolio/trades still work, and the smoke test passes (Validation V3, V13).

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

### 19. Check the gate against real market data
- The gate's data comes from yfinance (market cap, earnings date, bid/ask, open interest) and is tested with fakes only. Real fields can be missing or stale, and because missing data **blocks** the trade, a poor feed would block legitimate entries.
- Try 10–15 real symbols (large caps, ETFs like SPY, a small cap) through "Check gate". If too many say "could not verify", consider a better data source (a paid data API is allowed; record it in `../BUSINESS/03-FINANCIAL-MODEL.md`).
- Also check: yfinance's `calendar` earnings date, `marketCap` for ETFs, and bid/ask/open interest after hours (they are often 0 or missing when the market is closed, which would block every option trade).
- Done when: typical symbols pass or fail for the right reasons (Validation V15).

### 20. Confirm the rule assumptions
- The docs gave no numbers for several rules, so defaults were chosen. They are listed in `../BUSINESS/05-IMPLEMENTATION-STATUS.md` ("Phase 2 assumptions"). Confirm or change each:
  - [ ] **Market "down"** (BR-010): SPY closes below its 200-day average.
  - [ ] **Regime floor** (BR-015): a score below 25 blocks all new entries; 25–40 (DEFENSIVE) still allows Base-layer trades.
  - [ ] **Regime sub-score formulas**: trend 0–100 (50 above the 200-day, +30 above the 50-day, +20 if the 50-day is over the 200-day); VIX 100 at 12 or lower down to 0 at 40 or higher; IV rank = percentile of today's VIX within its last year; weights 40/30/30.
  - [ ] **Halved risk budget** in a DEFENSIVE (or UNKNOWN) regime, with the Growth layer locked.
  - [ ] **Band caps** measured as capital at risk (`risk_amount`) as a share of account size; warn at 80% of the cap, block at the cap.
  - [ ] **FR-670 sizing** taken literally (Risk / Credit, sized by premium), next to a safer max-loss mode.
  - [ ] **Back-dated entries** (more than 1 day old) skip the gate.
- Done when: each box is ticked (accepted) or a change has been made.

### 21. Rule thresholds are constants, not settings
- The gate's thresholds (spread 10%, open interest 500, market cap $2B/$10B, earnings 14 days, regime floor 25) live in `backend/app/domain/gate.py`. FR-830 asks for configurable thresholds.
- Changing one today means editing code and redeploying; there is no audit trail for the change except git.
- Done when: they are exposed in Settings (with audit), or the docs say they are fixed.

### 22. Band usage endpoint differs from the plan
- The plan said `GET /portfolio/{id}/bands`; it was built as `GET /portfolio/bands` because the band caps apply to the whole account, not to one portfolio. The Sizing page and the status docs use the account-wide version.
- Decide: keep it account-wide (then nothing to do), or also offer a per-portfolio view.
- Done when: the choice is confirmed, or a per-portfolio endpoint exists.

### 23. Phase 3 behaviour to confirm
- **Option P&L is now x100** (contract multiplier). Earlier it was understated 100x. Check one real trade against your broker. Trades already stored are not changed, only how P&L is computed.
- Alert thresholds (7/3 days, delta 0.30/0.50/0.70, profit 50%/80%, stop-loss multiples, regime floor 25) are listed in `../BUSINESS/05-IMPLEMENTATION-STATUS.md` ("Phase 3 assumptions"). Confirm or change each, then decide whether they should move into Settings (same question as item 21).
- Roll and Hedge are suggestions only: nothing is placed, and no roll candidate is computed (smart rolling is Planned).
- Alerts are computed when you open a page (60-second price cache), not pushed. Email or Slack alerts for exits would need the scheduler.
- Weekly Picks need `weekly_picks` rows from `scheduler/scripts/generate_picks.py`; until it runs the page is empty.
- Strategy Matrix, Option Chain, Heat Dashboard and Scenarios pages are still demo pages (Phase 4).
- Done when: the thresholds are confirmed and the P&L figure is checked (Validation V16).

## P3

### 12. Spec and implementation mismatches
- The older `/regime/{symbol}` endpoint (bull/bear/ranging from a 30-day return) still exists next to the new 0–100 score (`/regime/score`); decide whether to keep or remove it.
- Alpha bands A–E are quality tiers by score; the docs define them as capital-allocation buckets with 30/25/20/15/10% caps.
- `alpha/app/business_logic.py` is dead code that treats spread as a fraction (`< 0.08`) while the real screener uses percent (`< 8`). Delete it or make it the single implementation.
- Done when: docs and code agree, or the docs are updated to match.

### 13. Alpha data robustness
- Missing values count silently as zero in `compute_option_score` (NaN compares false; `None` raises).
- Google Sheets push: ranges are capped at A–Z and 500 rows; `USER_ENTERED` can turn text from external data into formulas.
- `app/secrets_loader.py` is never called.
- `alpha/.env.example` exists locally but is not tracked in git, while the README tells people to copy it. Commit it (without secrets) or fix the README.
- Done when: bad inputs are rejected or reported, not scored as zero.

### 14. Test coverage
- Frontend has 67 unit tests (Phases 1-3); the Phase 4 pages and the remaining demo pages still need them. The Active Holdings and Active Trades pages have no tests yet.
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
