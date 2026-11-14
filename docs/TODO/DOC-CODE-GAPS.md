# Docs vs code — remaining gaps

Compared on 2026-11-14 (docs in `docs/BUSINESS` and `docs/TECHNICAL` against `backend/`, `alpha/`, `frontend/`, `database/`, `scheduler/` and `.github/workflows/`).
Mobile and PRO/billing are out of scope and not listed.

Rows for features built in **Phase 1** (persistence, watchlists, settings, logs, pagination, failed-login logging) were removed on 2026-11-14; the full status matrix is in `docs/BUSINESS/05-IMPLEMENTATION-STATUS.md`.

Stale-fact rows (stack versions, cron times, `ALPHA.md` paths, workflow names, error types, health endpoint, backup workflow) were **fixed on 2026-11-14** and removed from this list.

What remains is documented-but-not-built functionality. For each row decide **build it** or **change the doc**, then delete the row (see [README](README.md)).

## A1. Business rules and functional requirements

| Requirement | Status in code |
|---|---|
| **DNT rules** BR-010–BR-021, FR-840 | Partial, in `alpha/` only: option volume, OI ≥ 500, spread ≤ 8% (doc says 10%), earnings > 14 days, short interest. **Missing:** market cap < $2B, NewsFlag, assignment alarm, equity guardrail, correlation, regime-deterioration rule. Nothing blocks a trade entry. |
| **Master Gate / "CLEAR TO TRADE"** (FR-330, FR-550, BR-081) | None. |
| **Regime score 0–100** → DEFENSIVE / NORMAL / GROWTH (BR-100–104, FR-400–430) | Not implemented. Backend `regime.py` classifies bull/bear/ranging from a 30-day return; VIX is fetched but unused. No regime history or boundary alerts. |
| **Layer allocation** 80/20, 60/40, 40/60 (BR-035–037) and Base/Growth layers | None. |
| **Band capital caps** 30/25/20/15/10% (BR-034, FR-640) | None. Alpha bands A–E mean "score tier", not capital buckets. |
| **Position sizing** Risk/Credit, 1–1.5% / 2–3% (FR-600–670) | None. Sizing page is static; its button does nothing. |
| **EV scoring / ranking** (picks, FR-1220) | None. |
| **Exit alerts, assignment risk, suggested actions** (BR-050–054, 095–098, FR-1210) | None. Pages are static. |
| **Portfolio risk dashboard** Net Delta, Margin %, sector exposure (BR-080, FR-540) | None. Backend returns P&L and win rate only. |
| **Strategy Design Matrix** logic (BR-090–094, FR-1100–1160) | None. Static grid. |
| **Scenario / stress simulation** (FR-530) | None. |
| **Signal-log entries for gate decisions** (BR-061, BR-063, FR-710) | The append-only `signal_log` / `audit_events` tables, audit trail and log API exist (Phase 1). Nothing writes gate/regime decisions yet — arrives with the gate in Phase 2. |
| **Alerts / notifications** (FR-800–830) | Only pipeline failure alerts. No regime, DNT or exit alerts. |
| **Disclaimer on first login** (Business §2, §11) | The acceptance API exists (`POST /settings/disclaimer`); the modal in the frontend is Phase 3. |
| **Charting** ("advanced charting" in the system overview) | No chart library is installed; no charts exist. |

## A2. Navigation and screens (FR-1000–1240)

| Requirement | Status |
|---|---|
| Home = three metric cards (Portfolio Value, Total P&L, Options Buying Power) + 2×2 grid of the four core sections | Dashboard shows three different cards (Account limits, Market Regime, Quick actions). |
| Sidebar groups HOME / PRIMARY SECTIONS / collapsible TOOLS & ANALYTICS | One flat list of 17 links. |
| Dedicated pages for the four core sections with real data | Pages exist but are static (demo banner). |

## A3. API

| Documented | Actual |
|---|---|
| `GET /auth/profile` | Not present (`/auth/me` exists). |
| `GET /screener`, `GET /screener/{id}`, `POST /screener/search` | Only `POST /screener/run` and `GET /screener/limits`. |
| `GET /picks` | Not present. The `weekly_picks` table and `scheduler/scripts/generate_picks.py` exist, but no endpoint or frontend reads them. |
| Rate limit 100 req/min per IP | Not implemented. |
| Caching (screener 5 min, Greeks 1 h, regime 1 h) | `*_CACHE_TTL_SECONDS` constants exist but nothing uses them. |

## A4. Database

| Documented | Actual |
|---|---|
| `market_regime` table | Not in any migration. |
| Regime history | Not built (Phase 2, migration 008 `market_regime`). Watchlist, signal-log and audit tables exist (migration 007). |
| Alpha: `symbols` and `signals` tables | Removed from `ALPHA.md`; not in the schema. Decide whether `signals` is needed. |

## A5. Scheduler and folders

| Documented | Actual |
|---|---|
| `generate-regime.yml` (weekly regime) | Missing. |
| `scheduler/scripts/send_picks_email.py`, `report_metrics.py`, `cost_monitor.py` | Missing (noted in `05-SCHEDULER-LAYER.md`). Email and Datadog are optional; `cost_monitor` would help track free-tier limits. |
| `shared/` folder (shown in `01-SYSTEM-OVERVIEW.md` and `03-FOLDER-STRUCTURE.md`) | Does not exist. Remove it from those docs or create it. |
