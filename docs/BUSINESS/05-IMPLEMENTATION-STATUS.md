# StrideAlytics — Implementation Status

Which documented requirements exist in code today. The requirement text lives in `01`–`04`; this file only records status.
Last updated: 2026-11-14, after **Phase 2 (trading core)**.

**Status key:** **Built** · **Partial** (what is missing is noted) · **Phase N** (scheduled in the current build plan) · **Planned** (wanted, not scheduled) · **Out of scope** (personal use, no PRO/billing; mobile deferred).

**Build phases:** 1 Persistence + logs (done) → 2 Trading core: DNT gate, regime score, sizing, band caps (done) → 3 Home hub + real pages (alerts, picks, dashboard) → 4 Analytics (risk, scenarios, EV, strategy matrix, charts).

## Functional requirements

| Requirement | Status | Notes |
|---|---|---|
| **FR-100–110** Settings module, account/strategy/risk defaults | **Built** | `/settings` API + Settings page (account size, risk %, guardrail, band caps, regime weights, gate switch) |
| **FR-120** Watchlists with symbol groups | **Built** | CRUD, per-user, export |
| **FR-130** Per-user show/hide toggles | Partial | Stored (`widget_toggles`); no UI uses them yet |
| **FR-140** Tunable regime inputs | **Built** | Weights tunable in Settings; applied to your live score (the shared history uses the defaults) |
| **FR-200** Watchlist grid (price, IV, trend, risk) | Partial | Symbol, price, change %; IV/trend/risk metrics in Phase 2–4 |
| **FR-210** Refresh | Partial | Auto-refresh every 60 s; manual refresh button not added |
| **FR-220** CSV export | **Built** | Trades and watchlists |
| **FR-230** Multi-watchlist grouping, quick search | Partial | Multiple lists built; quick symbol search Planned |
| **FR-300–320** Option chain, strategy preview, risk preview | Phase 4 | Chain data exists in the screener service |
| **FR-330, FR-840, FR-850** Block entries on DNT / show reasons | **Built** | `POST /trades` runs the gate and refuses a blocked entry with every reason; the UI shows them. Back-dated entries (more than 1 day old) are record-keeping and not gated |
| **FR-400–430** Regime score, history, boundary alerts | **Built**; Heat Dashboard in Phase 4 | 0–100 score, DEFENSIVE/NORMAL/GROWTH, daily history, a signal-log entry and a Slack alert when the state changes |
| **FR-500** Active trades with P&L, Greeks, assignment risk, time to expiry | **Built** | Active Holdings and Exit Alerts show P&L, delta, theta, DTE and assignment risk from live prices; Greeks use Black-Scholes. Options P&L is now multiplied by 100 (earlier it was understated 100x) |
| **FR-510** Closed-trade history | **Built** | Filter by status, sort, paginate. Performance analytics in Phase 4 |
| **FR-520** Aggregate portfolio metrics | Partial | Counts, P&L, win rate; risk metrics in Phase 4 |
| **FR-530** Scenario simulations | Phase 4 | |
| **FR-540, FR-550** Net Delta, margin %, sector exposure; block on risk limits | Phase 4 (metrics); block on equity guardrail **Built** | |
| **FR-600–670** Position sizing, band caps | **Built** | Sizing page and "Suggest size" in the trade form; FR-670 is implemented literally (Risk / Credit) plus a safer max-loss mode |
| **FR-700, FR-720, FR-730** Immutable trade/decision log, review, search | **Built** | Append-only `audit_events` and `signal_log`; every gate decision, blocked or allowed, is logged; filter by date, symbol, rule |
| **FR-710** Signal change log for regime shifts | **Built** | |
| **FR-800** Real-time alerts (regime, DNT, exit) | Regime change and pipeline failures **Built** (Slack); exit alerts **Built** in the app (computed on request, no push) | DNT blocks are shown in the app and logged |
| **FR-810** Email and push notifications | Planned / Out of scope | Webhooks instead of email; push is mobile |
| **FR-820, FR-830** In-app blocked-trade warnings, configurable thresholds | Warnings **Built**; configurable thresholds Partial | Risk %, equity guardrail and band caps are configurable; the rule thresholds themselves (10% spread, OI 500, ...) are constants |
| **FR-900–930** Trade flow, EV scoring, correlation | Trade flow up to the gate **Built**; EV and correlation Phase 4 | Backtesting and broker integration: **Planned** |
| **FR-1000–1050** Home hub, metric cards, grouped sidebar | **Built** | Home = 3 metric cards + 2x2 grid; sidebar HOME / PRIMARY / collapsible TOOLS & ANALYTICS (collapsed by default, red badge for unacknowledged critical alerts) |
| **FR-1100–1160** Strategy Design Matrix | Phase 4 | Home card is a link only until Phase 4 |
| **FR-1200–1240** Dedicated section pages on real data | **Built** (Exit Alerts, Weekly Picks, Active Holdings, Active Trades); Strategy Matrix Phase 4 | Weekly Picks stay empty until the scheduler has written `weekly_picks` rows. EV ranking (FR-1220) is Phase 4; picks are sorted by confidence |

## Business rules

| Rule | Status |
|---|---|
| **BR-010–021** DNT rules | **Built**, except BR-013 (correlation, Phase 4), which is reported as "not evaluated". BR-011 now counts open positions with an assignment alarm; if positions cannot be priced the gate blocks (fail-safe) |
| **BR-100–104** Regime score and states (formerly BR-020–024) | **Built** |
| **BR-025, 030–037** Allocation, caps, layer split | **Built** (layer split shown; Growth lock; band caps; risk per trade). BR-031 continuous account stop-loss monitoring is Phase 4 |
| **BR-040–044** Entry and strategy rules | Partial: hard guardrails (BR-044) and Base-layer thresholds (BR-042) are in the gate; strategy selection comes from alpha's screen |
| **BR-050–054, BR-095–098** Exit logic, alerts, acknowledgement | **Built**: Normal/Watch/Warning/Critical, suggested Hold/Roll/Close/Hedge, acknowledgement stored (`alert_acks`) and resolved when the alert clears or the trade closes. Roll and Hedge are suggestions only (no smart rolling, Planned) |
| **BR-060** Log settings changes | **Built** |
| **BR-061** Log blocked signals | **Built** |
| **BR-062** Log trade add/close with time and context | **Built** |
| **BR-063** Immutable log of regime and gate changes | Regime changes **Built**; changes to the rule thresholds themselves are constants in code, so they are tracked by git |
| **BR-064** Audit export | Partial (trades CSV); audit CSV export Planned |
| **BR-070** Operational alerts | Partial (pipeline failures); API-latency alert Planned |
| **BR-071** Free-tier quota alerts | Planned (`cost_monitor` script) |
| **BR-080–082** Portfolio dashboard, block on risk limits | Dashboard Phase 4; equity-guardrail block **Built** |
| **BR-090–094** Strategy Matrix rules | Phase 4 |

## Security and compliance

| Item | Status |
|---|---|
| JWT auth, RLS on user tables, secrets in env | **Built** |
| Dev tokens only when `ENVIRONMENT=development` | **Built** |
| Failed-login logging | **Built** |
| First-login disclaimer | **Built** (modal until accepted; timestamp stored) |
| RBAC, MFA, admin governance | **Out of scope** (single user) |

## Out of scope / deferred

PRO plan, pricing, billing, multi-user / RIA features, admin console, mobile app (deferred until confirmed).

## Planned, not scheduled

Backtesting, broker API and streaming/WebSocket data, smart rolling engine, paid news feed (NewsFlag is manual), push notifications, API-latency and quota alerts, audit CSV export.

## Phase 2 assumptions (defaults you can change)

The docs leave these open; the code uses these documented defaults.

| Topic | Default |
|---|---|
| "Market is down" (BR-010) | SPY closes below its 200-day average |
| Regime "deteriorated" (BR-015) | Score below 25 blocks all new entries; a DEFENSIVE score of 25–40 still allows Base-layer trades |
| Regime sub-scores | Trend 0–100 (50 above the 200-day, +30 above the 50-day, +20 if 50-day over 200-day); VIX 100 at 12 or lower down to 0 at 40 or higher; IV rank = percentile of today's VIX within its last year. Weights 40/30/30, tunable in Settings |
| Spread (BR-017) | Above 10% of the mid price blocks. Alpha's screener uses 8% as a *quality* score; the gate's 10% is the hard stop |
| Base layer (BR-042) | Market cap must exceed $10B; any layer needs at least $2B (BR-019) |
| Equities only | Market cap and earnings rules are skipped for ETFs and indices |
| Missing data | Blocks the trade with a "could not verify" reason; it is never waved through |
| Sizing | Risk budget = account size × risk % (Base 1.25%, Growth 2.5% by default); halved in a DEFENSIVE or UNKNOWN regime; Growth layer locked there |
| Band caps | Share of account size committed as capital at risk (`risk_amount`) in open trades; warns at 80% of the cap, blocks at the cap |
| Back-dated entries | Entries more than 1 day old are record-keeping and skip the gate (the decision is logged) |
| Black-Scholes | European-style pricing is used for Greeks even though listed equity options are American |

## Phase 3 assumptions (defaults you can change)

| Topic | Default |
|---|---|
| Expiry / DTE | Watch at 7 days, Warning at 3, Critical on or after expiry |
| Assignment risk | Delta at 0.70 or more is Critical; 0.50 or more Warning; Watch at 0.30 (Base) / 0.40 (Growth); deep ITM (5% or more) escalates |
| Profit target | Watch at 50% of the maximum profit, Warning at 80% |
| Stop loss | Short options: Watch/Warning/Critical at 50% / 100% / 200% of the credit; long options at 50% / 75% / 90% of the premium; risk-defined at 25% / 50% / 100% of `risk_amount` |
| Regime | A score below 25 raises a Warning on open positions |
| Options Buying Power | Account equity minus capital at risk in open trades |
| Portfolio Value | Account size plus realised P&L plus unrealised P&L of the positions that could be priced (the card says when some could not) |
| Acknowledgement | Only active Warning/Critical alerts can be acknowledged; it clears itself when the alert resolves |
| Thresholds | Constants in `backend/app/domain/alerts.py`, not yet editable in Settings |
