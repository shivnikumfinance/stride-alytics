# StrideAlytics — Implementation Status

Which documented requirements exist in code today. The requirement text lives in `01`–`04`; this file only records status.
Last updated: 2026-11-14, after **Phase 1 (persistence + logs)**.

**Status key:** **Built** · **Partial** (what is missing is noted) · **Phase N** (scheduled in the current build plan) · **Planned** (wanted, not scheduled) · **Out of scope** (personal use, no PRO/billing; mobile deferred).

**Build phases:** 1 Persistence + logs (done) → 2 Trading core (DNT gate, regime score, sizing, band caps) → 3 Home hub + real pages (alerts, picks, dashboard) → 4 Analytics (risk, scenarios, EV, strategy matrix, charts).

## Functional requirements

| Requirement | Status | Notes |
|---|---|---|
| **FR-100–110** Settings module, account/strategy/risk defaults | **Built** | `/settings` API + Settings page (account size, risk %, guardrail, band caps, regime weights, gate switch) |
| **FR-120** Watchlists with symbol groups | **Built** | CRUD, per-user, export |
| **FR-130** Per-user show/hide toggles | Partial | Stored (`widget_toggles`); no UI uses them yet |
| **FR-140** Tunable regime inputs | Partial | Weights stored and validated; the regime score itself is Phase 2 |
| **FR-200** Watchlist grid (price, IV, trend, risk) | Partial | Symbol, price, change %; IV/trend/risk metrics in Phase 2–4 |
| **FR-210** Refresh | Partial | Auto-refresh every 60 s; manual refresh button not added |
| **FR-220** CSV export | **Built** | Trades and watchlists |
| **FR-230** Multi-watchlist grouping, quick search | Partial | Multiple lists built; quick symbol search Planned |
| **FR-300–320** Option chain, strategy preview, risk preview | Phase 4 | Chain data exists in the screener service |
| **FR-330, FR-840, FR-850** Block entries on DNT / show reasons | Phase 2 | |
| **FR-400–430** Regime score, Heat Dashboard, history, boundary alerts | Phase 2 (score, history, alerts), Phase 4 (heat dashboard) | Today: simple bull/bear/ranging |
| **FR-500** Active trades with P&L, Greeks, assignment risk, time to expiry | Partial | Realised P&L built; Greeks/assignment in Phase 3 |
| **FR-510** Closed-trade history | **Built** | Filter by status, sort, paginate. Performance analytics in Phase 4 |
| **FR-520** Aggregate portfolio metrics | Partial | Counts, P&L, win rate; risk metrics in Phase 4 |
| **FR-530** Scenario simulations | Phase 4 | |
| **FR-540, FR-550** Net Delta, margin %, sector exposure; block on risk limits | Phase 4 (metrics) / Phase 2 (block) | |
| **FR-600–670** Position sizing, band caps | Phase 2 | Inputs (account size, risk %, caps) are stored now |
| **FR-700, FR-720, FR-730** Immutable trade/decision log, review, search | **Built** (audit trail), Phase 2 (decision entries) | Append-only `audit_events` and `signal_log`; filter by date, symbol, rule |
| **FR-710** Signal change log for regime shifts | Phase 2 | |
| **FR-800** Real-time alerts (regime, DNT, exit) | Phase 2 (regime) / Phase 3 (exit) | Pipeline failure alerts built (Slack/Discord) |
| **FR-810** Email and push notifications | Planned / Out of scope | Webhooks instead of email; push is mobile |
| **FR-820, FR-830** In-app blocked-trade warnings, configurable thresholds | Phase 2 | |
| **FR-900–930** Trade flow, EV scoring, correlation | Phase 2–4 | Backtesting and broker integration: **Planned** |
| **FR-1000–1050** Home hub, metric cards, grouped sidebar | Phase 3 | |
| **FR-1100–1160** Strategy Design Matrix | Phase 4 (full) / Phase 3 (summary card) | |
| **FR-1200–1240** Dedicated section pages on real data | Phase 3 | |

## Business rules

| Rule | Status |
|---|---|
| **BR-010–021** DNT rules | Phase 2 (alpha already filters on liquidity and earnings as a quality screen) |
| **BR-100–104** Regime score and states (formerly BR-020–024) | Phase 2 |
| **BR-025, 030–037** Allocation, caps, layer split | Phase 2 |
| **BR-040–044** Entry and strategy rules | Phase 2–3 (alpha screening is Partial) |
| **BR-050–054, BR-095–098** Exit logic, alerts, acknowledgement | Phase 3 |
| **BR-060** Log settings changes | **Built** |
| **BR-061** Log blocked signals | Phase 2 |
| **BR-062** Log trade add/close with time and context | **Built** |
| **BR-063** Immutable log of regime and gate changes | Phase 2 |
| **BR-064** Audit export | Partial (trades CSV); audit CSV export Planned |
| **BR-070** Operational alerts | Partial (pipeline failures); API-latency alert Planned |
| **BR-071** Free-tier quota alerts | Planned (`cost_monitor` script) |
| **BR-080–082** Portfolio dashboard, block on risk limits | Phase 4 / Phase 2 |
| **BR-090–094** Strategy Matrix rules | Phase 4 |

## Security and compliance

| Item | Status |
|---|---|
| JWT auth, RLS on user tables, secrets in env | **Built** |
| Dev tokens only when `ENVIRONMENT=development` | **Built** |
| Failed-login logging | **Built** |
| First-login disclaimer | Partial: acceptance API built, modal is Phase 3 |
| RBAC, MFA, admin governance | **Out of scope** (single user) |

## Out of scope / deferred

PRO plan, pricing, billing, multi-user / RIA features, admin console, mobile app (deferred until confirmed).

## Planned, not scheduled

Backtesting, broker API and streaming/WebSocket data, smart rolling engine, paid news feed (NewsFlag is manual), push notifications, API-latency and quota alerts, audit CSV export.
