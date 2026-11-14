# Pending items

Priority: **P1** = do next, **P2** = soon, **P3** = when convenient.
Delete an item when it is done and validated (see [README](README.md)). Last updated: 2026-11-14.

## Board

**Who** says what is needed: **you** = needs your accounts, secrets or a decision; **me** = can be done in the repo without secrets.

| # | Item | Priority | Who | State |
|---|------|----------|-----|-------|
| 1 | Open a PR to `develop` and get CI green | P1 | you | Committed and pushed to `feature/main-implementation`; CI not yet seen |
| 2 | Apply migrations 006 to 010 to Supabase | P1 | you | Verified on local PostgreSQL 16; not on Supabase |
| 3 | Persistence on real PostgreSQL; `DATABASE_URL` on Render | P1 | you | Smoke test 11/11 and the full suite pass locally |
| 4 | Verify the daily workflow on GitHub | P1 | you | Needs repo secrets |
| 5 | Real Supabase login end to end | P1 | you | Unit-tested only |
| 19 | Gate and option data on a weekday, market hours | P1 | you + me | Saturday run done; weekday run open |
| 25 | Decide the open-interest rule and the stale-earnings fail-safe | P1 | you | Findings recorded |
| 6 | Real data ingestion for alpha | P2 | you + me | Decision needed (small universe or paid API) |
| 7 | Clean up old duplicate rows in Supabase | P2 | you | Needs the database |
| 8 | Protect the Streamlit dashboard | P2 | you | Needs hosting access |
| 10 | Session renewal (refresh token) | P2 | me | Test it with item 5 |
| 11 | `CORS_ORIGINS` on Render; Yahoo ticker source | P2 | you + me | Code fixes done |
| 17 | Close the doc-vs-code gaps | P2 | you + me | See [DOC-CODE-GAPS.md](DOC-CODE-GAPS.md) |
| 18 | Alpha and backend table-name collisions | P2 | you | Decision needed |
| 20 | Confirm the Phase 2 rule assumptions | P2 | you | Checklist below |
| 21 | Rule thresholds as Settings (FR-830) | P2 | me | After items 20, 23, 24 are confirmed |
| 23 | Confirm Phase 3 behaviour (alerts, P&L x100) | P2 | you | Checklist below |
| 24 | Confirm Phase 4 behaviour (limits, matrix, EV) | P2 | you | Checklist below |
| 22 | Band usage endpoint shape | P3 | you | Decision |
| 12 to 16 | Spec mismatches, alpha robustness and lint, tests, leftovers, hygiene (incl. the unexplained file revert) | P3 | me + you | Partly done |

---

## P1

### 1. Open a pull request and get CI green
- All work (scope docs, plan removal, security and trade fixes, Phases 1 to 4, PostgreSQL validation tooling, live-data fixes, auth hardening, alpha scoring) is committed and pushed on `feature/main-implementation` (origin is up to date as of 2026-11-14).
- Next: open a PR into `develop` (the main branch) and let `.github/workflows/ci.yml` run. CI now fails on test failures, so the first run is the real check of the backend, alpha and frontend suites on Linux.
- Watch for: the pre-commit hook (backend black auto-fix aborts the commit once), and alpha's linters, which already fail on older files and are not covered by the hooks (`ruff` 7 errors, `black` 18 files).
- Done when: the PR's CI is green and it is merged.

### 2. Apply migrations 006 to 010 to Supabase
- **Verified on a local throwaway PostgreSQL 16 (2026-11-14):** migrations 001 to 010 apply in order with no errors, the `_down` files for 010 to 006 roll back cleanly and 006 to 010 re-apply, and the whole backend suite (373 tests) passes against the migration-built schema. A minimal stand-in for Supabase's `auth.uid()` and roles was used, so this is **not** yet a test on Supabase itself.
- `006_drop_subscription_plan.sql`, `007_persistence_logs.sql`, `008_market_regime.sql`, `009_alert_acks.sql` and `010_scenarios.sql` (each with a `_down` file) are written but **not applied**. Apply them in order with `database/scripts/apply_migrations.{sh,ps1}`.
- **None of them has been applied anywhere yet**, including 008 (`market_regime`), 009 (`alert_acks`) and 010 (`scenarios`). Try all five on a throwaway Supabase project first (see item 3), including each `_down` file once.
- Done when: all five are applied, login/portfolio/trades still work, and the smoke test passes (Validation V3, V13).

### 3. Validate persistence on real PostgreSQL
- Code is done (Phase 1): portfolios, trades, watchlists, settings and the append-only logs are stored through `backend/app/repositories/sql.py`; unit tests run on SQLite.
- **Render must have `DATABASE_URL` set.** Without it the backend silently uses in-memory SQLite and loses everything on restart (a warning is logged).
- **Passed 11/11 on the local throwaway Postgres (2026-11-14)**, including UPDATE/DELETE/TRUNCATE being rejected on `signal_log` and `audit_events`. Repeat it once on a throwaway Supabase project: `backend/scripts/smoke_db.py --disposable` proves the Postgres triggers make `signal_log` / `audit_events` append-only (SQLite cannot).
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

### 10. Frontend session renewal
- **Fixed:** after a reload the user is restored from `/auth/me`; a bad `VITE_API_URL` no longer crashes the app at import time.
- **Open:** the refresh token is never used, so the session ends after about an hour (Supabase's default) and you are sent to the login page. Renewing needs the refresh token stored and a retry-on-401, which should be written and tested against a real Supabase login (item 5).
- The access token is kept in `localStorage`; that is acceptable for personal use, but any XSS would expose it.
- Done when: the session renews without a new login, or you accept the hourly login.

### 11. Backend hardening
- **Fixed:** `/auth/refresh` now takes the refresh token in the request body (a URL can end up in logs); CORS no longer combines `*` with credentials (credentials only for explicit origins) and logs a warning when `*` is used outside development.
- **Open, set on Render:** `CORS_ORIGINS` to your frontend URL (the default is still `*`).
- **Open:** `market.py` uses Yahoo's v7 quote endpoint, which likely needs a crumb and so always returns the fallback values; the responses are labelled `source`, but switch the source or accept the label. Check the Dashboard ticker with the network on.
- Done when: `CORS_ORIGINS` is set in production and the market-ticker source is fixed or accepted.

### 17. Close the doc-vs-code gaps
- See [DOC-CODE-GAPS.md](DOC-CODE-GAPS.md). The stale facts were fixed; what remains is documented-but-unbuilt functionality (push or email alerts, `/auth/profile`, screener search endpoints, rate limiting, caching, scheduler scripts, the `shared/` folder).
- For each row decide: build it, or change the doc to match; then delete the row.
- Done when: `DOC-CODE-GAPS.md` is empty.

### 18. Table-name collisions between alpha and backend
- `alpha/app/supabase_schema.sql` defines `trades` and `audit_log` with different columns than the backend's `trades` (migration 002). In one Supabase project whichever is created first wins and the other silently breaks. The new backend audit table was named `audit_events` to avoid the second clash.
- Decide: separate Supabase projects/schemas for alpha and the backend, or rename alpha's tables (for example `alpha_trades`). Alpha's pipeline does not write `trades` today.
- Done when: both schemas can coexist (or are kept apart) and this is documented in `ALPHA.md`.

### 19. Check the gate against real market data
- **Done on a Saturday (2026-11-14):** 14 symbols, regime, option liquidity, sectors, chains and scenarios were run through the real yfinance providers; results are in `VALIDATION.md` ("Live-data results") and the findings are item 25. The gate blocked and cleared for the right reasons, and bid/ask were present rather than 0.
- **Still to do:** repeat the option checks on a weekday during market hours and in pre-market, when bid/ask can be 0 and would block every option trade ("could not verify"). If that is common, consider a better data source (a paid API is allowed; record it in `../BUSINESS/03-FINANCIAL-MODEL.md`).
- Done when: the weekday check shows typical symbols pass or fail for the right reasons (Validation V15).

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
- Done when: the thresholds are confirmed and the P&L figure is checked (Validation V16).

### 24. Phase 4 behaviour to confirm
- **Limits are my defaults** (see `../BUSINESS/05-IMPLEMENTATION-STATUS.md`, "Phase 4 assumptions"): total capital at risk 50% of equity (blocks new entries), sector 25% and net delta 100% of equity (reported only). Confirm or change each, then decide whether they belong in Settings (same question as items 21 and 23).
  - [ ] Total risk limit 50% (blocks)  - [ ] Sector limit 25%  - [ ] Net delta limit 100%
  - [ ] The strategy suitability table (`backend/app/domain/strategy_matrix.py`) matches how you want to trade each strategy per regime.
  - [ ] EV uses a pick's confidence as the probability of profit; confirm that the weekly job's confidence means that.
- **Margin % is not real margin.** It is capital at risk / equity. A broker feed would be needed for true margin.
- **Correlation (BR-013) is still not evaluated** in the gate; it needs return histories per symbol and a threshold you choose. Planned.
- **EV at entry is not stored on trades**, so the calibration report (`/analytics/ev-calibration`) shows realised results by layer only. To compare EV with outcomes, store the entry EV on each trade first.
- **Strategy cells link to the Screener**, not to a strategy detail page (FR-1140 / BR-093). Build the page or accept the link.
- **Sectors and chains come from yfinance** (unofficial, may be rate limited or return nothing after hours); both labels say when data is missing or synthetic. Check a few symbols.
- **Bundle size:** the production build is one JS file over 500 kB (recharts). Code-split the chart pages with `React.lazy` if load time matters.
- Done when: the thresholds are confirmed and the pages have been checked with real positions (Validation V17).

### 25. Live-data findings (checked 2026-11-14, a Saturday, so quotes were Friday's close)
- **Fixed:** the chain loader fetched only the first 3 expirations, so for AAPL (Mon/Wed/Fri weeklies) every contract expired within 6 days and the Option Chain page and the screener's 30-day window found nothing. It now picks up to 8 expirations spread across the window (default 90 days; the screener uses its own `expiry_days_max`).
- **Fixed:** one contract with a missing volume or open interest (NaN) made `int(NaN)` raise and dropped its whole expiry; NaN also leaked into JSON. Parsing is now NaN-safe, and contracts with no implied volatility are skipped instead of being given an invented 0.3.
- **Open, decide:** the open-interest minimum of 500 (BR-018) blocks weekly options. The ATM puts of the 30-day weekly (11 Dec) had OI 314 (AAPL), 255 (SPY) and 191 (MSFT), while the monthly (18 Dec) has tens of thousands. Either keep the rule (trade monthlies) or lower it; this is part of item 21.
- **Open, accept or change:** when yfinance gives only a past earnings date (Ford: 2026-10-28), BR-020 blocks with "could not verify the next earnings date". That is the intended fail-safe, but it blocks every trade in such symbols until the date updates.
- **Not yet checked:** a weekday, during market hours and in pre-market, when bid/ask can be 0. Repeat the V15 option checks then.
- Cosmetic: yfinance logs HTTP 404 for SPY/QQQ fundamentals (ETFs have none); the gate handles ETFs correctly.
- Done when: the OI rule is decided and the weekday check is done (Validation V15).

## P3

### 12. Spec and implementation mismatches
- The older `/regime/{symbol}` endpoint (bull/bear/ranging from a 30-day return) still exists next to the new 0–100 score (`/regime/score`); decide whether to keep or remove it.
- Alpha bands A–E are quality tiers by score; the docs define them as capital-allocation buckets with 30/25/20/15/10% caps.
- `alpha/app/business_logic.py` is dead code that treats spread as a fraction (`< 0.08`) while the real screener uses percent (`< 8`). Delete it or make it the single implementation.
- Done when: docs and code agree, or the docs are updated to match.

### 13. Alpha data robustness
- **Fixed:** `compute_option_score` no longer raises on `None`/NaN/bad values; a missing input earns no point and is named in a new `Data Gaps` column (it shows in Sheets; it is not stored in Supabase). Decide whether rows with gaps should be excluded from the watchlist or flagged in the dashboard.
- Google Sheets push: ranges are capped at A–Z and 500 rows; `USER_ENTERED` can turn text from external data into formulas.
- `app/secrets_loader.py` is never called.
- `alpha/.env.example` exists locally but is not tracked in git, while the README tells people to copy it. Commit it (without secrets) or fix the README.
- Done when: bad inputs are rejected or reported, not scored as zero.

### 14. Test coverage
- Frontend has 113 unit tests, backend 382, alpha 21 (Active Holdings, Active Trades and the auth store are now covered). The Greeks, Screener and Portfolio pages are still thin.
- CI now fails on test failures (it used to swallow them with `|| echo`); confirm the first run on GitHub is green.
- `mypy` is blocked by a Windows Application Control policy on this machine; run it in CI or another environment.
- **Alpha lint fails on older files** (`ruff` 7 errors, 6 auto-fixable; `black` would reformat 18 files). The pre-commit hook does not cover alpha, but CI may. Run `uv run ruff check --fix . && uv run black .` in `alpha/` as its own commit, or exclude the files.
- No backend test hits real Supabase.
- Done when: key flows (login, add/close trade, screener) have frontend tests and mypy runs somewhere.

### 15. Leftovers from the plan and mobile removal
- `mobile/` still references `subscription_plan` (auth store, settings screen); deferred, but it will not match the API.
- Doc bodies still contain optional paid examples (`render.yaml` with `plan: standard`, the ~$84 cost table, SendGrid scripts) under a scope banner.
- `backend/render.yaml` uses `plan: starter` (a paid Render plan, about $7/month, no sleep). Decide: keep it, or switch to `free` (sleeps when idle). `APP_ENV` in that file is not used by the code (`ENVIRONMENT` is). `vercel.json` and the other workflows (`fetch-market-data`, `calculate-greeks`, `generate-weekly-picks`) are not yet reviewed for free-tier minute use.
- Existing Supabase auth users may still carry a `subscription_plan` in their metadata (ignored, harmless).
- Done when: configs match the free-tier defaults in `../BUSINESS/03-FINANCIAL-MODEL.md`.

### 16. Repository hygiene
- **Unexplained revert (2026-11-14, 14:26):** `backend/app/api/v1/endpoints/portfolio.py` and `trades.py` were overwritten in the working tree with the pre-Phase-1 in-memory versions (the backend then failed to import). It was not a commit; something outside the session rewrote them. They were restored from `HEAD` and the copies kept in the session scratchpad. If it recurs, check editor extensions, other AI tools, sync clients and any `git checkout`/stash done on an old commit. A `git status` before each commit catches it.
- `.mcp.json` GitHub server fails to connect ("Incompatible auth server: does not support dynamic client registration").
- Confirm `alpha/service_account.json` is git-ignored (it exists locally; only `service_account.example.json` should be tracked).
- Done when: the MCP server connects or is removed, and the credential file is confirmed ignored.
