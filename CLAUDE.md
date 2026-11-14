# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current scope

Personal use only. The PRO plan, billing and multi-user features have been removed from the docs, and the `mobile/` app is deferred until further confirmation. Don't build on those. Free tiers are the default, so keep designs within their limits (Supabase ~500 MB, Render free sleeps when idle, GitHub Actions minutes). Paid APIs or services (for example a data provider) may be added later if needed; record them in `docs/BUSINESS/03-FINANCIAL-MODEL.md`.

## Repo layout

Monorepo. Each module has its own dependencies and tooling.

- `alpha/`: options-screening pipeline plus Streamlit dashboard (Python, uv)
- `backend/`: FastAPI API (Python, uv)
- `frontend/`: Vite + React 19 + TypeScript SPA
- `next-app/`: separate Next.js app. Its `AGENTS.md` warns of breaking changes in this Next.js version, so read `node_modules/next/dist/docs/` before writing code.
- `mobile/`: Expo / React Native app, mirrors the frontend screens
- `scheduler/`: Python scripts run by GitHub Actions cron (market data, greeks, picks, health check)
- `database/`: SQL migrations, schema, RLS policies
- `docs/`: source of truth for business and technical rules. Read the relevant `docs/` files before feature, architecture or layer work (`.github/instructions/docs-first`). For backend work also read `docs/TECHNICAL/RULES/backend/*` and `api-flow/API-FLOW.md`.

There is no root README. `alpha/README.md` and `docs/TECHNICAL/ALPHA.md` describe the pipeline.

## Commands

Python modules need Python 3.12 (backend, scheduler) or 3.11+ (alpha) and use uv.

**alpha** (`cd alpha`)
- `uv sync`
- `uv run test_local.py`: runs the core pipeline with no external services
- `uv run python app/main.py`: full pipeline (needs Supabase and API keys)
- `streamlit run app/streamlit_app.py`: run from `alpha/` so `app.*` imports resolve
- `uv run lint|format|typecheck|verify`: ruff and black (line length 100), strict mypy
- `uv run pytest tests -q`: pipeline I/O tests (fake Supabase client, no network)
- The pipeline fails (non-zero exit + Slack/Discord alert) when there is no real data or a Supabase write fails. Built-in sample rows are used only with `ALLOW_SAMPLE_DATA=1` and are never written.

**backend** (`cd backend`)
- `uv sync`, `uv run dev` (watcher; `--once` for one run)
- `uv run lint|format|typecheck|test|verify`
- All tests: `uv run pytest tests -q`
- One test: `uv run pytest tests/test_services.py::test_name -q`
- Tests run on a per-test SQLite file (no Postgres needed). `scripts/smoke_db.py --disposable` (with `SMOKE_DB_URL`) checks the real Postgres triggers against a throwaway database only.

**frontend** (`cd frontend`)
- `npm ci`, `npm run dev`
- `npm run verify` (type-check plus lint), `npm run build`
- `npm test` (vitest + Testing Library, jsdom); one file: `npx vitest run <file>`

Setup: `scripts/setup-dev.sh` or `scripts/setup-dev.ps1` installs dependencies and husky hooks.

## Hooks and CI

- `.husky/pre-commit` runs checks only for the side that changed (`frontend/` or `backend/`). The backend black step auto-fixes files and then aborts the commit, so re-stage and commit again. Alpha is not covered by the hooks.
- `.github/workflows/ci.yml` runs on `main` and `develop`. Some steps use `|| echo` and do not block, so a green CI does not prove the tests pass.
- Alpha's Dockerfile and `daily_run.yml` use Python 3.11, while its linters target py312.

## Architecture

**Alpha pipeline** (`alpha/app/main.py:run_system`):
1. Load data: Supabase first (`utils/load_data.py`), then `alpha/raw_screener.csv`, then built-in sample rows.
2. Score options 0–9 (`screener/compute_option_score.py`).
3. Assign bands A–E (`screener/band_pipeline.py`).
4. Apply daily filters (`screener/apply_filters.py`).
5. Build the weekly watchlist (`screener/weekly_watchlist.py`).
6. Insert into Supabase (`database/insert_daily.py`). It clears today's rows first.
7. Push to Google Sheets (`sheets/push_to_sheets.py`).

Failures in the insert and Sheets steps only log a warning.

`app/ingest.py` merges yfinance, Polygon, FMP and Massive through `data_sources/`. `alpha/app/streamlit_app.py` reads Supabase tables with `st.cache_data`. The root `requirements.txt` mirrors alpha's dependencies for Streamlit Cloud.

**Persistence** (`backend/app`): endpoints use `Repo` (`repositories/sql.py`) through `get_ctx` in `api/deps.py`, which resolves the user, creates their `public.users` row on first sight and scopes every query to them. PostgreSQL is used when `DATABASE_URL` is set; otherwise an in-memory SQLite fallback starts (data lost on restart, warning logged). The ORM models define the SQLite schema and the `.sql` files in `database/migrations/` are the PostgreSQL source of truth, so change both together. `signal_log` and `audit_events` are append-only (DB trigger + `ImmutableRecordError`); every trade, portfolio, watchlist and settings change writes an audit row in the same transaction. Alpha's `trades` / `audit_log` tables have different columns than the backend's (see `docs/TODO/PENDING.md`).

**Platform**: the frontend (axios in `src/api/client.ts`, TanStack Query hooks, zustand stores) calls the backend `/api/v1` routes. The backend layers are endpoints → services → models/database, on Supabase Postgres via async SQLAlchemy, with JWT auth. The `scheduler/` scripts write to Supabase on GitHub Actions cron.

## Configuration

- Alpha (`alpha/app/config.py`): `SUPABASE_URL`, `SUPABASE_KEY`, `POLYGON_API_KEY` and `FMP_API_KEY` are required. `MASSIVE_API_KEY`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEETS_SPREADSHEET_ID` and the Slack/Discord webhook URLs are optional. The alpha README says to copy `alpha/.env.example`, but that file is not tracked.
- Root and `backend/` `.env.example` cover the backend, frontend and mobile settings.
- Backend `ENVIRONMENT` defaults to `production`. Dev auth tokens (`dev:<id>`, `dev-admin-token`) and the dev login fallback work only with `ENVIRONMENT=development` (set it in `backend/.env` for local work). Real Supabase JWTs are verified with audience `authenticated` (`SUPABASE_JWT_AUDIENCE`).
- API responses for market tickers, the screener and regime carry a `source` field; anything other than `live` is placeholder data and the UI labels it.

## Diagrams

Per `.github/instructions/mermaid.instructions.md`:
- Write diagrams to `.mmd` files and validate them (`mermaid-diagram-validator`) before showing them.
- Don't hand-edit diagrams managed by the Mermaid Sync workflow.
- Warn the user before running Repair, because it uses Mermaid AI credits.

## MCP

`.mcp.json` configures a GitHub HTTP MCP server (`https://api.githubcopilot.com/mcp/`). It currently fails to connect with "Incompatible auth server: does not support dynamic client registration".
