# StrideAlytics — Implementation Status

Which documented requirements exist in code today. The requirement text lives in `01`–`04`; this file only records status.
Last updated: 2026-11-14, after **Phase 4 (analytics)**.

**Status key:** **Built** · **Partial** (what is missing is noted) · **Phase N** (scheduled in the current build plan) · **Planned** (wanted, not scheduled) · **Out of scope** (personal use, no PRO/billing; mobile deferred).

**Build phases:** 1 Persistence + logs (done) → 2 Trading core: DNT gate, regime score, sizing, band caps (done) → 3 Home hub + real pages (alerts, picks, dashboard) (done) → 4 Analytics: risk, scenarios, EV, strategy matrix, option chain, charts (done). What remains is listed as **Planned** below and in `docs/TODO/`.

## Functional requirements

| Requirement | Status | Notes |
|---|---|---|
| **FR-100–110** Settings module, account/strategy/risk defaults | **Built** | `/settings` API + Settings page (account size, risk %, guardrail, band caps, regime weights, gate switch) |
| **FR-120** Watchlists with symbol groups | **Built** | CRUD, per-user, export |
| **FR-130** Per-user show/hide toggles | Partial | Stored (`widget_toggles`); no UI uses them yet |
| **FR-140** Tunable regime inputs | **Built** | Weights tunable in Settings; applied to your live score (the shared history uses the defaults) |
| **FR-200** Watchlist grid (price, IV, trend, risk) | Partial | Symbol, price, change %; IV/trend/risk metrics Planned |
| **FR-210** Refresh | Partial | Auto-refresh every 60 s; manual refresh button not added |
| **FR-220** CSV export | **Built** | Trades and watchlists |
| **FR-230** Multi-watchlist grouping, quick search | Partial | Multiple lists built; quick symbol search Planned |
| **FR-300–320** Option chain, strategy preview, risk preview | Chain **Built**; strategy preview and pre-entry risk preview Planned | Option Chain page: calls/puts per strike with Greeks and a probability-of-profit estimate; `source` shows when the chain is synthetic. The portfolio risk after a candidate trade is not previewed yet (the Sizing page and the gate cover entry) |
| **FR-330, FR-840, FR-850** Block entries on DNT / show reasons | **Built** | `POST /trades` runs the gate and refuses a blocked entry with every reason; the UI shows them. Back-dated entries (more than 1 day old) are record-keeping and not gated |
| **FR-400–430** Regime score, history, boundary alerts, Heat Dashboard | **Built** | 0–100 score, DEFENSIVE/NORMAL/GROWTH, daily history with a chart, a signal-log entry and a Slack alert when the state changes; Heat Dashboard shows risk gauges, sector exposure, band usage and position health |
| **FR-500** Active trades with P&L, Greeks, assignment risk, time to expiry | **Built** | Active Holdings and Exit Alerts show P&L, delta, theta, DTE and assignment risk from live prices; Greeks use Black-Scholes. Options P&L is now multiplied by 100 (earlier it was understated 100x) |
| **FR-510** Closed-trade history | **Built** | Filter by status, sort, paginate. Realised win rate and average P&L by layer: `GET /analytics/ev-calibration` |
| **FR-520** Aggregate portfolio metrics | **Built** | Counts, P&L, win rate, plus `GET /portfolio/risk` |
| **FR-530** Scenario simulations | **Built** | Price, volatility and time shocks repriced with Black-Scholes; a P&L curve; named scenarios saved (`scenarios`, migration 010) |
| **FR-540, FR-550** Net Delta, margin %, sector exposure; block on risk limits | **Built** | Net delta, margin % (capital at risk / equity; there is no broker margin feed), sector exposure; the master gate blocks new entries when capital at risk exceeds the limit (BR-081). Net delta and sector limits are reported as breaches, not blocks |
| **FR-600–670** Position sizing, band caps | **Built** | Sizing page and "Suggest size" in the trade form; FR-670 is implemented literally (Risk / Credit) plus a safer max-loss mode |
| **FR-700, FR-720, FR-730** Immutable trade/decision log, review, search | **Built** | Append-only `audit_events` and `signal_log`; every gate decision, blocked or allowed, is logged; filter by date, symbol, rule |
| **FR-710** Signal change log for regime shifts | **Built** | |
| **FR-800** Real-time alerts (regime, DNT, exit) | Regime change and pipeline failures **Built** (Slack); exit alerts **Built** in the app (computed on request, no push) | DNT blocks are shown in the app and logged |
| **FR-810** Email and push notifications | Planned / Out of scope | Webhooks instead of email; push is mobile |
| **FR-820, FR-830** In-app blocked-trade warnings, configurable thresholds | Warnings **Built**; configurable thresholds Partial | Risk %, equity guardrail and band caps are configurable; the rule thresholds themselves (10% spread, OI 500, ...) are constants |
| **FR-900–930** Trade flow, EV scoring, correlation | Trade flow, EV scoring **Built**; correlation **Planned** | Picks are ranked by expected value (PoP x gain - (1 - PoP) x loss). EV at entry is not stored on trades, so the calibration report shows realised results only. Backtesting and broker integration: **Planned** |
| **FR-1000–1050** Home hub, metric cards, grouped sidebar | **Built** | Home = 3 metric cards + 2x2 grid; sidebar HOME / PRIMARY / collapsible TOOLS & ANALYTICS (collapsed by default, red badge for unacknowledged critical alerts) |
| **FR-1100–1160** Strategy Design Matrix | **Built** (grid, filters, gate overlay); strategy detail page **Planned** | Six strategies x three regimes with availability, layers, bands and gate status; each cell links to the Screener, not a dedicated strategy page (FR-1140 / BR-093) |
| **FR-1200–1240** Dedicated section pages on real data | **Built** | Exit Alerts, Weekly Picks, Active Holdings, Active Trades and Strategy Matrix. Weekly Picks stay empty until the scheduler has written `weekly_picks` rows |

## Business rules

| Rule | Status |
|---|---|
| **BR-010–021** DNT rules | **Built**, except BR-013 (correlation), which is reported as "not evaluated" (**Planned**). BR-011 counts open positions with an assignment alarm; if positions cannot be priced the gate blocks (fail-safe). BR-081 (total risk) is also checked |
| **BR-100–104** Regime score and states (formerly BR-020–024) | **Built** |
| **BR-025, 030–037** Allocation, caps, layer split | **Built** (layer split shown; Growth lock; band caps; risk per trade). BR-031 continuous account stop-loss monitoring is covered by the equity guardrail and the Heat Dashboard; there is no background monitor |
| **BR-040–044** Entry and strategy rules | Partial: hard guardrails (BR-044) and Base-layer thresholds (BR-042) are in the gate; strategy selection comes from alpha's screen |
| **BR-050–054, BR-095–098** Exit logic, alerts, acknowledgement | **Built**: Normal/Watch/Warning/Critical, suggested Hold/Roll/Close/Hedge, acknowledgement stored (`alert_acks`) and resolved when the alert clears or the trade closes. Roll and Hedge are suggestions only (no smart rolling, Planned) |
| **BR-060** Log settings changes | **Built** |
| **BR-061** Log blocked signals | **Built** |
| **BR-062** Log trade add/close with time and context | **Built** |
| **BR-063** Immutable log of regime and gate changes | Regime changes **Built**; changes to the rule thresholds themselves are constants in code, so they are tracked by git |
| **BR-064** Audit export | Partial (trades CSV); audit CSV export Planned |
| **BR-070** Operational alerts | Partial (pipeline failures); API-latency alert Planned |
| **BR-071** Free-tier quota alerts | Planned (`cost_monitor` script) |
| **BR-080–082** Portfolio dashboard, block on risk limits | **Built**: Net Delta, Margin %, Sector Exposure, Total Risk and regime on the Heat Dashboard; total risk over the limit blocks entries (BR-081) |
| **BR-090–094** Strategy Matrix rules | **Built**, except BR-093 (cells open the Screener, not a strategy detail page) and BR-094 (refreshes every minute, not in real time) |

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

## Phase 4 assumptions (defaults you can change)

| Topic | Default |
|---|---|
| Margin % | Capital at risk (sum of `risk_amount` of open trades) as a share of equity; no broker margin feed |
| Total risk limit (BR-081) | Capital at risk above **50%** of equity blocks new entries (checked in the master gate) |
| Sector limit (BR-080) | Capital at risk in one sector above **25%** of equity is reported as a breach (it does not block). Sector comes from yfinance; an unknown sector is "Unknown" and never flagged |
| Net delta limit (BR-080) | Absolute net delta in dollars above **100%** of equity is reported as a breach |
| Net delta | Share-equivalent delta of the positions that could be priced; the rest are counted and shown, never assumed zero |
| Expected value | `EV = PoP x gain - (1 - PoP) x loss` per contract. For a pick, PoP is its stored confidence and gain/loss come from target and stop; for an option, PoP = 1 - |delta| |
| Scenarios | Black-Scholes with the quoted implied volatility; the model's *change* is applied to the market mark so a zero shock changes nothing. At or after expiry the value is intrinsic. Positions without a price or volatility are listed, not guessed |
| Strategy suitability | A design table (Iron Condor, Put/Call Credit Spread, Butterfly, Jade Lizard, Straddle/Strangle by regime, layer and band) in `backend/app/domain/strategy_matrix.py`; a blocked gate blocks every strategy in the current regime |
| Chain probability | Probability a short option expires worthless = 1 - |delta| |
| Thresholds | Constants in `backend/app/domain/portfolio_risk.py`, not yet editable in Settings |
