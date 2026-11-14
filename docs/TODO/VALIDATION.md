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
- Restart the backend: the trades are still there (after DB-backed trades are done).

### V3. Migration 006 (Pending 2)
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
