# StrideAlytics — Business Requirements

## 1. Document Purpose

This document translates the StrideAlytics Options Selling Platform (OSP) Build Guide into formal business requirements, product vision, user personas, platform phases, and high-level acceptance criteria. It is the authoritative reference for developers, product managers, and stakeholders building the web app, mobile app, backend API, and platform operations.

## 2. Important Disclaimer

StrideAlytics is an analytics and decision-support tool. It does not constitute financial advice. All rules and thresholds are configurable defaults. Users must paper-trade and backtest before deploying real capital. Consult a licensed financial professional before trading.

## 3. Product Vision

StrideAlytics is a multi-platform options selling analytics platform for individual traders and small RIAs managing $50K–$150K+ in capital. It provides a systematic, rules-driven decision framework that replaces discretionary judgment with quantitative risk gates, regime-aware allocation, and automated trade scoring.

The platform operationalizes the Adaptive Dual-Layer Engine — a Conservative/Base layer and a Growth layer — across all market regimes, enforcing hard capital gates that prevent emotional or impulsive trade decisions.

The user interface follows a **hub-and-spoke architecture**: the Home screen serves as a command center featuring four core sections — Exit Alerts & Recommendations, Top Weekly Picks, Active Holdings & Trade Alerts, and Strategy Design Matrix. Each core section provides a summary view on the Home screen with a "View Full Screen" link that navigates to a dedicated, in-depth analysis page. All other tools, analytics, and dashboards are accessible via a collapsible "Tools & Analytics" sidebar section, keeping the Home screen clean and focused.

## 4. Strategic Objectives

- Codify the full OSP rule set into production software: settings, DNT filters, regime scoring, sizing, exit logic.
- Provide real-time portfolio Greeks monitoring with hard gate enforcement.
- Surface regime-aware weekly trade picks ranked by Expected Value (EV).
- Replace manual spreadsheet workflows with a scalable, API-driven web and mobile platform.
- Target an annual return objective of 40–75% with controlled risk and regime-aware exposure.
- Support complete audit trail: all trades, blocked signals, and settings changes are logged.
- Achieve 100% free-tier deployability at MVP; designed to scale to paid tiers as AUM grows.

## 5. Primary Users

- **Individual Trader**
  - Self-directed options seller, $50K–$150K capital.
  - Key needs: regime dashboard, weekly picks, position sizing, exit alerts.
- **Small RIA**
  - Registered Investment Advisor managing client accounts.
  - Key needs: multi-account view, audit trail, RBAC, compliance logs.
- **Paper Trader**
  - User learning the system before deploying real capital.
  - Key needs: full platform access, simulated P&L, explicitly no broker integration required.
- **Admin**
  - Platform operator/developer.
  - Key needs: settings management, user administration, data pipeline monitoring.

## 6. Platform Phases

- **Phase 0 — Skeleton**
  - Watchlist, option chain, active/closed trades, signal log, change log.
  - Timeline: Days 1–5.
- **Phase 1 — Core Risk Layer**
  - Regime score, heat dashboard, position sizing calculator.
  - Timeline: Weeks 1–2.
- **Phase 2 — Scenario & Assignment**
  - Scenario stress testing, assignment risk model.
  - Timeline: Weeks 3–6.
- **Phase 3 — Signal Quality**
  - EV scoring, correlation matrix, backtesting analytics.
  - Timeline: Months 1–3.
- **Phase 4 — Automation & Scale**
  - Broker API, streaming data, smart rolling engine.
  - Timeline: Months 3–6.

## 7. Core Platform Capabilities

### 7.1 Home Screen — Core Sections

- **Exit Alerts & Recommendations** — Real-time alerts for positions approaching assignment risk, profit targets, or regime-triggered exits. Includes severity filtering, action buttons (Roll, Close, Hedge), and history.
- **Top Weekly Picks** — Regime-aware weekly trade recommendations ranked by Expected Value (EV). Shows strategy, strike, credit, PoP, and DNT status.
- **Active Holdings & Trade Alerts** — Enriched active positions view with per-position alert status (Normal, Watch, Warning, Critical), suggested actions, Greeks monitoring, and margin health.
- **Strategy Design Matrix** — Interactive grid of option strategies × regime states (Defensive, Normal, Growth) showing availability, layer compatibility, band fit, and gate status for each cell.

### 7.2 Additional Tools & Analytics

- Options screener with multi-dimensional filters and DNT gating.
- Greeks calculator and risk analytics engine.
- Portfolio and trade tracking with P&L and exit alerts.
- Regime scoring engine with manual override.
- Weekly picks recommendations and EV ranking.
- Admin dashboard with user, billing, and operational control.
- Immutable signal and change logs for audit.
- Position sizing calculator with configurable risk budgets.
- Scenario simulation and stress-testing engine.
- Heat Dashboard with market health, risk gauges, and trend indicators.
- Signal log for immutable rule-based decision records.
- Watchlist management with symbol groups and quick search.
- Option chain viewer with strike, bid/ask, Greeks, and probability metrics.

## 8. Business Metrics

- Daily active users (DAU)
- Monthly active users (MAU)
- Free-to-PRO conversion rate (target 5-10%)
- Customer acquisition cost (CAC)
- Monthly recurring revenue (MRR)
- Churn rate and retention
- Average revenue per user (ARPU)
- System uptime and API latency

## 9. Tiered Offering

### Free Tier

- Basic screener access with results limits
- Unlimited Greeks calculator
- Basic portfolio tracking
- Market regime summary
- Weekly picks and alerts
- Web and mobile access

### PRO Tier

- Unlimited screener results
- Advanced filters and saved templates
- Portfolio analytics and historical reporting
- API access and webhooks
- Real-time alerts and push notifications
- No ads and priority support
- Pricing: $19/month

## 10. User Experience Requirements

- Analytics-first design with data density and actionable insight.
- Dark mode default with optional light mode.
- Gate-forward interface: CLEAR TO TRADE / BLOCKED status prominent.
- Mobile-first workflows for dashboard review, alerts, and trade entry.
- No ambiguous states: every metric shows current value, limit, and status.
- Consistent UI across web and mobile.
- Fast and intuitive onboarding.
- Transparent billing and subscription controls.
- **Home screen displays exactly 4 core sections** — Exit Alerts & Recommendations, Top Weekly Picks, Active Holdings & Trade Alerts, and Strategy Design Matrix — arranged in a 2×2 grid below a row of three summary metric cards (Portfolio Value, Total P&L, Options Buying Power). Each core section card shows summary data with a "View Full Screen" link. All other features are accessed via a collapsible "Tools & Analytics" sidebar section.

## 11. Compliance and Security Requirements

- JWT-based authentication for protected resources.
- Row-Level Security (RLS) in database for user isolation.
- Secure token storage in frontend and mobile.
- HTTPS/TLS for all API communications.
- Admin and settings access governed by RBAC.
- Audit logging for admin actions, settings changes, and blocked trades.
- Disclaimer display on first login and in settings.

## 12. Weekly and Monthly Workflows

### Daily Pre-market Workflow

- Verify Master Gate status.
- Review Regime Score and mode.
- Review exit alerts and take action.
- Refresh watchlist data and regime inputs.
- Confirm heat dashboard metrics are within gates.

### Trade Entry Workflow

- Review Weekly Picks and select candidates.
- Pre-fill sizing calculator with symbol and layer.
- Confirm strategy parameters and gate checks.
- Verify final approved contracts.
- Add trade and confirm active trade updates.
- Validate Heat Dashboard refresh.

### Weekly Review Workflow

- Run scenario simulations.
- Review recommended actions and weekly picks.
- Inspect performance analytics.
- Log change rationale and gate performance.

### Monthly Review Workflow

- Export closed trades for audit.
- Calibrate EV score against realized P&L.
- Review and tune risk settings.
- Analyze signal log frequency and rule effectiveness.
