# StrideAlytics — Application Requirements

## 1. Overview

This document defines the application-level requirements for the StrideAlytics platform, including functional modules, data requirements, UI/UX expectations, non-functional constraints, and acceptance criteria.

## 2. Functional Requirements

### 2.1 Settings and Configuration

- **FR-100**: Provide a configurable Settings module with a clean UI.
- **FR-110**: Support account-level settings, strategy defaults, and risk guardrail thresholds.
- **FR-120**: Allow users to set and edit watchlists with symbol groups.
- **FR-130**: Store and enforce per-user show/hide toggles for sectors, strategies, and dashboard widgets.
- **FR-140**: Expose regime score calculation input parameters and allow admins to tune them.

### 2.2 Watchlist and Data Sheets

- **FR-200**: Display a watchlist grid with symbol, underlying price, IV, trend, and risk metrics.
- **FR-210**: Provide auto-refresh and manual refresh controls for watchlist data.
- **FR-220**: Permit Excel/CSV export of watchlist symbols and analytics data.
- **FR-230**: Support multi-watchlist grouping and quick symbol search.

### 2.3 Option Chain and Strategy Entry

- **FR-300**: Present option chain data with strike, bid/ask, Greeks, and probability metrics.
- **FR-310**: Enable users to choose and preview option strategies from the chain.
- **FR-320**: Show real-time risk impact before trade entry.
- **FR-330**: Prevent trade entry on symbols or strategies that violate DNT or regime gates.

### 2.4 Regime and Market Signals

- **FR-400**: Display current regime score and mood in a dedicated dashboard panel.
- **FR-410**: Provide a Heat Dashboard with regime state, momentum, and trend statistics.
- **FR-420**: Visualize regime mode changes over time and key regime drivers.
- **FR-430**: Alert users when regime score crosses Conservative/Balanced/Growth boundaries.

### 2.4.1 Regime Engine Inputs and Outputs

- Use VIX, SPY trend (50/200 MA), and IV Rank as core inputs.
- Compute a 0–100 regime score for market state.
- Display regime states as DEFENSIVE (0–40), NORMAL (40–70), and GROWTH (70–100).
- Use regime state to adjust allocation, risk exposure, and trade eligibility.

### 2.5 Portfolio and Risk Analytics

- **FR-500**: Display active trades with P&L, Greeks, assignment risk, and time-to-expiry.
- **FR-510**: Provide closed trades history and performance analytics.
- **FR-520**: Show aggregate portfolio metrics and drill-down trade details.
- **FR-530**: Support saved portfolio scenarios and stress-test simulations.
- **FR-540**: Track Net Delta, Margin %, Sector Exposure, Total Risk, and current Regime State.
- **FR-550**: Block trading if portfolio risk exceeds configured limits.

### 2.6 Position Sizing and Execution Guidance

- **FR-600**: Offer a position sizing calculator with configurable risk budgets and trade caps.
- **FR-610**: Enforce sizing rules for Base and Growth layers.
- **FR-620**: Display notional exposure, trade percentage, and total account risk.
- **FR-630**: Provide explicit warnings when trade sizing exceeds regime or account limits.
- **FR-640**: Apply band-level capital allocation limits across the portfolio and surface compliance with Band A–E caps.
- **FR-650**: Set Base layer risk per trade to 1–1.5% of portfolio value.
- **FR-660**: Set Growth layer risk per trade to 2–3% of portfolio value.
- **FR-670**: Calculate contract quantity as Risk / Credit.

### 2.6.1 Capital Band Allocation

- Band allocation rules must be implemented as part of portfolio construction and trade approval.
- The platform should display the current percentage allocated to each band and warn when any band approaches its cap.
- Band caps:
  - Band A: 30%
  - Band B: 25%
  - Band C: 20%
  - Band D: 15%
  - Band E: 10%

### 2.7 Trade Log and Signal Tracking

- **FR-700**: Maintain an immutable trade log of all actions, including blocked signals.
- **FR-710**: Provide a signal change log that records all rule-based regime shifts.
- **FR-720**: Allow users to review historical decisions with timestamps and rule reasons.
- **FR-730**: Support search and filter in logs by date, symbol, account, and rule trigger.

### 2.8 Alerts and Notifications

- **FR-800**: Deliver real-time alerts for regime shifts, DNT activations, and exit recommendations.
- **FR-810**: Support email and push notifications for critical risk events.
- **FR-820**: Display in-app warnings for blocked trade attempts.
- **FR-830**: Allow users to configure threshold-based notifications.

### 2.8.1 Do Not Trade Filter Rules

- **FR-840**: Prevent new trade entry when spread > 10%, open interest < 500, market cap < $2B, earnings are within 14 days, or a NewsFlag exists.
- **FR-850**: Surface DNT reasons clearly in the UI.

## 2.9 Navigation and Home Screen Layout

- **FR-1000**: The Home screen is the default landing page for all authenticated users.
- **FR-1010**: The Home screen displays a row of three summary metric cards at the top: Portfolio Value (with cash available), Total P&L (Active) (with trade count), and Options Buying Power (with utilization percentage).
- **FR-1020**: Below the metric cards, the Home screen displays exactly four core sections in a 2×2 grid layout:
  - Exit Alerts & Recommendations
  - Top Weekly Picks
  - Active Holdings & Trade Alerts
  - Strategy Design Matrix
- **FR-1030**: Each core section card shows summary-level data and includes a "View Full Screen" or "View All" link that navigates to the corresponding dedicated page.
- **FR-1040**: The sidebar navigation is organized into three groups:
  - **HOME**: A single "Home" link that returns to the 4-section dashboard.
  - **PRIMARY SECTIONS**: Direct links to the four dedicated section pages (Exit Alerts, Weekly Picks, Active Holdings, Strategy Matrix).
  - **TOOLS & ANALYTICS**: A collapsible accordion section containing all other features (Watchlist, Option Chain, Active Trades, Position Sizing, Scenario Simulations, Heat Dashboard, Signal Log, Admin Panel).
- **FR-1050**: The collapsible "Tools & Analytics" section defaults to collapsed state, keeping the sidebar focused on primary navigation.

## 2.10 Strategy Design Matrix

- **FR-1100**: The Strategy Design Matrix displays option strategies as rows and regime states (Defensive, Normal, Growth) as columns in an interactive grid.
- **FR-1110**: Each strategy cell shows: availability status (🟢 Available / 🟡 Limited / 🔴 Blocked), compatible trading layers (Base, Growth), recommended capital bands (A–E), and current gate status.
- **FR-1120**: The matrix is filterable by layer (Base/Growth) and capital band (A/B/C/D/E).
- **FR-1130**: The matrix updates in real-time as regime scores, market data, and portfolio state change.
- **FR-1140**: Clicking a strategy cell navigates to a detailed strategy analysis page with configuration options.
- **FR-1150**: Strategies are visually grayed out or blocked when DNT (Do Not Trade) is active.
- **FR-1160**: At a minimum, the matrix includes these strategies: Iron Condor, Put Credit Spread, Call Credit Spread, Butterfly, Jade Lizard, and Straddle/Strangle.

## 2.11 Dedicated Section Pages

- **FR-1200**: Each of the four core Home screen sections has a corresponding dedicated full-screen page.
- **FR-1210**: **Exit Alerts & Recommendations Page** — Displays all exit alerts with severity filtering (Critical, Warning, Info), action buttons per alert (Roll, Close, Hedge), alert history timeline, and acknowledgment tracking.
- **FR-1220**: **Top Weekly Picks Detail Page** — Expands the full ranked list of weekly picks with deep analysis per pick: EV score breakdown, strategy details, Greeks, DNT status, entry preview, and comparison tools. (Enhancement of existing Weekly Picks page.)
- **FR-1230**: **Active Holdings & Trade Alerts Page** — Enriched view of all active positions with per-position trade alert status (Normal, Watch, Warning, Critical), suggested action buttons (Hold, Roll, Close, Hedge), Greeks monitoring, margin health indicators, and alert severity color-coding. (New page built on top of existing Active Trades data model.)
- **FR-1240**: **Strategy Design Matrix Page** — Full interactive matrix with all strategies × regime states, layer/band filters, detailed cell tooltips, and strategy configuration entry points.

## 2.12 Trade Flow and Implementation Phases

- **FR-900**: Implement trade flow from Market Data → Regime Engine → Allocation → Screening → Base/Growth Picks → TradeMaster → ActiveTrades.
- **FR-910**: Phase 1 builds the Regime Engine, Base and Growth layers, Portfolio Dashboard, and position sizing.
- **FR-920**: Phase 2 adds scenario simulation and basic EV scoring.
- **FR-930**: Phase 3 adds correlation/backtesting and broker integration.

## 3. Data Requirements

### 3.1 Core Data Models

- **User Profiles**
  - Profile settings, subscription status, RBAC role, watchlists, and preferences.
- **Symbols and Market Data**
  - Underlying price, IV, delta, gamma, theta, vega, option chain values, and correlations.
- **Regime Scores**
  - Computed regime mood, score components, classification, and timestamp.
- **Trade Records**
  - Active and closed trades, strategy, position size, entry/exit details, P&L, Greeks, and assignment triggers.
- **Signal Logs**
  - Rule triggers, DNT state, and regime commentary.
- **Audit Records**
  - Admin changes, setting revisions, user role updates, and access logs.

### 3.2 Data Integrity and Storage

- Persist all active and closed trades with immutable history.
- Require timestamps on every trade and log entry.
- Maintain a complete audit trail for settings changes and admin operations.
- Enforce referential integrity between trades, symbols, and user accounts.
- Version regime score inputs and gate rules for reproducibility.

### 3.3 External Data Interfaces

- Ingest market and options data from a reliable pricing provider.
- Support batch refresh and on-demand refresh endpoints.
- Protect external API keys and credentials in the backend.
- Provide normalized option chain data for both web and mobile views.

## 4. UI/UX Requirements

### 4.1 Design Principles

- Actionable dashboards with minimal clutter.
- Clear status indicators for trade readiness and blocked conditions.
- Distinct color coding for Conservative, Balanced, and Growth modes.
- High-contrast text and accessible charts.
- Responsive layouts for mobile and desktop.

### 4.2 Key Screens

- **Dashboard**
  - Current regime, heat score, top trade candidates, and active trade summary.
- **Watchlist Screen**
  - Symbol metrics, strategy tags, and price movement indicators.
- **Option Chain Screen**
  - Strike ladder, Greeks, and trade setup tools.
- **Trade Manager**
  - Active contract details, management actions, and exit recommendations.
- **Settings Screen**
  - Strategy thresholds, watchlist config, and notification preferences.
- **Admin Screen**
  - User management, subscription oversight, logs, and operational health.

### 4.3 Usability Requirements

- Provide onboarding tooltips for first-time users.
- Keep navigation simple and consistent.
- Surfaces important warnings before any trade commitment.
- Display both current value and limit value for risk-related metrics.
- Enable quick review of active trade risk at a glance.

## 5. Non-functional Requirements

### 5.1 Security

- Use HTTPS/TLS for all traffic.
- Implement JWT authentication with role claims.
- Store refresh tokens and secrets securely.
- Protect all admin APIs behind RBAC.
- Log failed login attempts and suspicious activity.

### 5.2 Performance

- Dashboard loads in under 2 seconds for authenticated users.
- Watchlist refreshes within 5 seconds on demand.
- Regime score calculation completes within 1 second for the user path.

### 5.3 Availability and Reliability

- Design for 99.5% platform availability.
- Support graceful degradation if external data sources fail.
- Provide alerts for scheduler or pricing ingest failures.

### 5.4 Compliance and Privacy

- Maintain a privacy policy and terms of use.
- Adhere to personal data protection best practices.
- Implement data retention rules for logs and trade history.
- Provide user control over notification preferences.

## 6. Acceptance Criteria

- The platform prevents new trade entry when DNT rules are active.
- Users can view an audit log of all rule-based signal decisions.
- Regime score updates are visible and explainable in the dashboard.
- Active trade monitoring displays Greeks, P&L, and assignment risk.
- Admin users can manage users, roles, and subscription statuses.
- All closed trades are persisted with immutable timestamps and references.
- Notifications are generated for critical risk events.
- Free and PRO tiers are clearly separated in feature availability.
