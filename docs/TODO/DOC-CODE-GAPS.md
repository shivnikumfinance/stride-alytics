# Docs vs code — remaining gaps

Last updated 2026-11-14 (after Phase 4 and the live-data fixes). Compared on 2026-11-14 (docs in `docs/BUSINESS` and `docs/TECHNICAL` against `backend/`, `alpha/`, `frontend/`, `database/`, `scheduler/` and `.github/workflows/`).
Mobile and PRO/billing are out of scope and not listed.

Rows for features built in **Phase 4** (portfolio risk, scenarios, EV ranking, strategy matrix, option chain, heat dashboard, charts) were removed on 2026-11-14.

Rows for features built in **Phase 3** (exit alerts, acknowledgements, picks endpoint, Home hub, grouped sidebar, real section pages, disclaimer modal) were removed on 2026-11-14.

Rows for features built in **Phase 2** (DNT gate and Master Gate, regime score, layer split, band caps, sizing, gate/regime signal logging, `generate-regime` workflow) were removed on 2026-11-14.

Rows for features built in **Phase 1** (persistence, watchlists, settings, logs, pagination, failed-login logging) were removed on 2026-11-14; the full status matrix is in `docs/BUSINESS/05-IMPLEMENTATION-STATUS.md`.

Stale-fact rows (stack versions, cron times, `ALPHA.md` paths, workflow names, error types, health endpoint, backup workflow) were **fixed on 2026-11-14** and removed from this list.

What remains is documented-but-not-built functionality. For each row decide **build it** or **change the doc**, then delete the row (see [README](README.md)).

## A1. Business rules and functional requirements

Documented but not (fully) built. Status per requirement is in `../BUSINESS/05-IMPLEMENTATION-STATUS.md`; open decisions are in [PENDING.md](PENDING.md).

| Requirement | Status in code | Tracked in |
|---|---|---|
| **Alerts / notifications** (FR-800–830) | Regime-change and pipeline alerts go to Slack; exit alerts are in-app only (no push or email) | Pending 23 |
| **Configurable rule thresholds** (FR-830) | Gate, alert and risk limits are constants in `backend/app/domain/`; only risk %, equity guardrail, band caps and regime weights are in Settings | Pending 21 |
| **Correlation rule** (BR-013, FR-930) | Reported as "not evaluated" in the gate; needs return histories and a threshold | Pending 24 |
| **Entry EV stored on trades** (FR-920) | Not stored, so `/analytics/ev-calibration` shows realised results only | Pending 24 |
| **Strategy detail page** (BR-093, FR-1140) | Matrix cells link to the Screener | Pending 24 |
| **Real-time matrix and prices** (BR-094, FR-1130) | Refresh every 1 to 2 minutes; no streaming | — (Planned) |
| **Strategy preview and risk preview before entry** (FR-310, FR-320) | The Sizing page and the gate cover entry; the portfolio risk after a candidate trade is not previewed | — (Planned) |
| **Watchlist IV / trend / risk columns, manual refresh, quick search** (FR-200, 210, 230) | Symbol, price, change %, news flag only; auto-refresh | — (Planned) |
| **Show/hide widget toggles** (FR-130) | Stored in `widget_toggles`; no UI uses them | — (Planned) |
| **Audit CSV export** (BR-064) | Trades CSV only | — (Planned) |
| **API-latency and free-tier quota alerts** (BR-070, BR-071) | Pipeline failures only; no `cost_monitor` | A4 below |
| **True margin** (BR-080) | Margin % is capital at risk / equity; no broker feed | Pending 24 |
| **Smart rolling, backtesting, broker integration, WebSocket streaming, paid news feed** | Not built; Roll and Hedge are suggestions only | — (Planned) |

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
| Alpha: `symbols` and `signals` tables | Removed from `ALPHA.md`; not in the schema. Decide whether `signals` is needed. |

## A4. Scheduler and folders

| Documented | Actual |
|---|---|
| `scheduler/scripts/send_picks_email.py`, `report_metrics.py`, `cost_monitor.py` | Missing (noted in `05-SCHEDULER-LAYER.md`). Email and Datadog are optional; `cost_monitor` would help track free-tier limits. |
| `shared/` folder (shown in `01-SYSTEM-OVERVIEW.md` and `03-FOLDER-STRUCTURE.md`) | Does not exist. Remove it from those docs or create it. |
