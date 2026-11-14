# Validation checklist

Run the relevant checks before deleting an item from [PENDING.md](PENDING.md).
Delete a check once the thing it covers is permanently automated in CI.

## Automated (run after any code change)

```bash
# Backend (cd backend)
uv run pytest tests -q          # last known: 70 passed
uv run ruff check .
uv run black --check .
uv run mypy app                 # blocked on this machine (Application Control); run elsewhere

# Frontend (cd frontend)
npm run type-check
npm run lint
npm run build

# Alpha (cd alpha)
uv run pytest tests -q          # last known: 11 passed
uv run ruff check . && uv run black --check .
```

## Manual checks

### V1. Dev-token bypass is closed (Pending 1)
- With `ENVIRONMENT=production` (or unset), `GET /api/v1/auth/me` with `Authorization: Bearer dev-admin-token` returns **401**.
- With `ENVIRONMENT=development` it returns 200.
- A production build (`npm run build`, then preview) shows **no** "Continue as Admin (dev)" button.

### V2. Trades (Pending 3)
- Add two trades, close the second: only the second shows as closed, with the exit price you typed.
- Restart the backend (with `DATABASE_URL` set): the trades are still there. (Without `DATABASE_URL` the backend uses in-memory SQLite and loses them.)

### V3. Migrations 006 and 007 (Pending 2)
- Apply `006_drop_subscription_plan.sql` on a copy or the dev project first.
- `\d users` no longer lists `subscription_plan`; login, portfolios and trades still work.
- Apply `006_drop_subscription_plan_down.sql` once to confirm it restores the column, then re-apply the up migration.

### V4. Real login (Pending 5)
- Sign up and log in through the frontend against the deployed API.
- `GET /api/v1/auth/me` returns 200 with your user id and email; a token with a different audience or a bad signature returns 401.

### V5. Daily workflow (Pending 4)
- Actions → "Daily Option System Run" → Run workflow: the job finishes green and the log shows `Supabase updated: {...}`.
- Temporarily break `SUPABASE_KEY`: the job turns red and a Slack/Discord alert arrives.
- Remove the CSV and the day's rows with `ALLOW_SAMPLE_DATA` unset: the run fails with "No input data" instead of writing demo rows.

### V6. Alpha data in Supabase (Pending 6, 7)
- After a run, each of `daily_metrics`, `option_scores`, `bands` and `weekly_watchlist` has rows for today only once (no duplicates), and `date` looks like `2026-11-14` (no time part).
- Run the pipeline twice in a row: row counts stay the same.

### V7. Streamlit (Pending 8)
- The dashboard shows only the latest day, with the full row count (not capped at 1000).
- Opening the app URL in a private window does not expose the data.

### V8. Data labelling
- Disconnect the network or block Yahoo: the header and Dashboard show "Sample data — not live", and the Screener and Regime pages show the same badge.
- With the network on, the badge is absent and screener rows have non-zero delta/gamma/theta/vega.

### V9. Demo pages (Pending 9)
- Every page that still shows the "Demo data" banner is listed in Pending 9; when a page is built on real data, its banner is removed.
- The sidebar has no link to a deleted page and `/admin` redirects to the home page.

### V10. Frontend session (Pending 10)
- Reload the browser: the sidebar still shows your email and Settings shows your account.
- Leave the app open past token expiry: you are not silently logged out (or you are sent to login cleanly).

### V11. Backup workflow (new)
- Add repo secrets `BACKUP_DATABASE_URL` and `BACKUP_PASSPHRASE`, then Actions → "Database Backup" → Run workflow.
- The job is green and a `db-backup` artifact with a `.sql.gz.gpg` file appears.
- **Restore test (once):** download it, then `gpg --decrypt <file> | gunzip | psql "<throwaway database URL>"` recreates your tables and rows.
- If the install step fails on the runner (PGDG repo, `postgresql-client-17`), adjust the step; the workflow has not been run yet.

### V12. Health endpoint and schedule (new)
- `GET https://<your-api>/health` returns 200 without a token; Render shows the service as healthy.
- `health-check.yml` is scheduled every 6 hours (Actions → Health Checks → Run workflow works).

### V13. Phase 1 on real PostgreSQL (new)
- Throwaway Supabase project: apply migrations 001–007 (and the 007 down file once, then 007 again).
- `cd backend && SMOKE_DB_URL=<throwaway url> uv run python scripts/smoke_db.py --disposable` prints all checks as PASS, including "UPDATE/DELETE/TRUNCATE on audit_events and signal_log is rejected". (Not yet run: SQLite cannot test the triggers.)
- Deployed API: `DATABASE_URL` is set on Render; add a portfolio and a trade, restart the service, and confirm they are still there.
- A second account cannot see the first account's portfolios, trades, watchlists, settings or logs.
- The Watchlist, Settings and Signal & Audit Log pages work with a real login; Export CSV downloads open correctly in a spreadsheet (a cell starting with `=` shows as text).

### V14. CI (new)
- Push a branch: all jobs (backend, alpha, frontend, database, scheduler) are green. Introduce a failing backend test on a scratch branch to confirm the job now turns red.

### V15. Phase 2: gate, regime and sizing with real data (new)
- Apply migration 008, then open the Regime page: a score appears (not "unavailable"), the history table gains today's row, and a second refresh does not duplicate it.
- Dashboard shows CLEAR TO TRADE or BLOCKED with reasons that match the market (SPY above or below its 200-day average).
- "Check gate" on 10–15 real symbols (for example AAPL, MSFT, SPY, a small cap with weak options): each result's reasons match what you see on the broker (spread, open interest, earnings date, market cap). Note any symbol where data is "could not verify".
- Add a trade dated today that the gate blocks: you get a 409, every reason is shown, no trade appears, and the Signal log has one "blocked" row per reason. Fix the cause (or clear a news flag) and add it again: it saves and the log shows "allowed".
- Tick "News flag" on a symbol, then try to add it: blocked with BR-021; untick: allowed.
- Settings: change band caps / risk % / regime weights; the Sizing page and your live regime score follow.
- Sizing: a Growth trade while the regime is DEFENSIVE is refused; Base is allowed with a halved budget.
- GitHub: run "Generate Market Regime" manually with `SUPABASE_URL`, `SUPABASE_KEY` and `SLACK_WEBHOOK` set: it writes today's row, and a state change posts to Slack.
- Run "Check gate" once **during** market hours and once **after hours**: after hours, bid/ask and open interest are often 0 or missing, which blocks option trades with "could not verify". Note which behaviour you get.
- `GET /portfolio/bands` (the account-wide band usage on the Sizing page) shows exposure rising after you add an open trade with a band and capital at risk.
