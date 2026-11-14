# Docs vs code — remaining gaps

Compared on 2026-11-14 (docs in `docs/BUSINESS` and `docs/TECHNICAL` against `backend/`, `alpha/`, `frontend/`, `database/`, `scheduler/` and `.github/workflows/`).
Mobile and PRO/billing are out of scope and not listed.

Rows for features built in **Phase 3** (exit alerts, acknowledgements, picks endpoint, Home hub, grouped sidebar, real section pages, disclaimer modal) were removed on 2026-11-14.

Rows for features built in **Phase 2** (DNT gate and Master Gate, regime score, layer split, band caps, sizing, gate/regime signal logging, `generate-regime` workflow) were removed on 2026-11-14.

Rows for features built in **Phase 1** (persistence, watchlists, settings, logs, pagination, failed-login logging) were removed on 2026-11-14; the full status matrix is in `docs/BUSINESS/05-IMPLEMENTATION-STATUS.md`.

Stale-fact rows (stack versions, cron times, `ALPHA.md` paths, workflow names, error types, health endpoint, backup workflow) were **fixed on 2026-11-14** and removed from this list.

What remains is documented-but-not-built functionality. For each row decide **build it** or **change the doc**, then delete the row (see [README](README.md)).

## A1. Business rules and functional requirements

| Requirement | Status in code |
|---|---|
| **EV scoring / ranking** (picks, FR-1220) | None. |
| **Portfolio risk dashboard** Net Delta, Margin %, sector exposure (BR-080, FR-540) | None. Backend returns P&L and win rate only. |
| **Strategy Design Matrix** logic (BR-090–094, FR-1100–1160) | None. Static grid. |
| **Scenario / stress simulation** (FR-530) | None. |
| **Alerts / notifications** (FR-800–830) | Regime-change and pipeline alerts go to Slack; exit alerts are in-app only (no push or email). |
| **Charting** ("advanced charting" in the system overview) | No chart library is installed; no charts exist. |

## A2. API

| Documented | Actual |
|---|---|
| `GET /auth/profile` | Not present (`/auth/me` exists). |
| `GET /screener`, `GET /screener/{id}`, `POST /screener/search` | Only `POST /screener/run` and `GET /screener/limits`. |
| Rate limit 100 req/min per IP | Not implemented. |
| Caching (screener 5 min, Greeks 1 h, regime 1 h) | `*_CACHE_TTL_SECONDS` constants exist but nothing uses them. |

## A3. Database

| Documented | Actual |
|---|---|
| `market_regime` table | Not in any migration. |
| Regime history | Built (migration 008 `market_regime`). Watchlist, signal-log and audit tables exist (migration 007). |
| Alpha: `symbols` and `signals` tables | Removed from `ALPHA.md`; not in the schema. Decide whether `signals` is needed. |

## A4. Scheduler and folders

| Documented | Actual |
|---|---|
| `scheduler/scripts/send_picks_email.py`, `report_metrics.py`, `cost_monitor.py` | Missing (noted in `05-SCHEDULER-LAYER.md`). Email and Datadog are optional; `cost_monitor` would help track free-tier limits. |
| `shared/` folder (shown in `01-SYSTEM-OVERVIEW.md` and `03-FOLDER-STRUCTURE.md`) | Does not exist. Remove it from those docs or create it. |
