# StrideAlytics — Business Rules

## 1. Rule Framework

StrideAlytics centers around executable business rules that enforce safe option-selling behavior, gate risk, and support decision transparency. Rules are grouped into:

- Authorization and governance
- Strategy and trade decision rules
- Market regime and risk gating
- Portfolio allocation and position sizing
- Exit and assignment rules
- Audit, logging, and escalation

## 2. Role-Based Authorization

- **Admin**
  - Full access to platform configuration, user management, billing, and logs.
  - Required to use MFA and secure credentials.
  - Must be assigned and approved before access.
- **PRO User**
  - Access to premium analytics, unlimited screener results, API access, and advanced alerts.
  - Can manage personal portfolio settings and trade preferences.
- **Standard User**
  - Free-tier access with limited screener usage, portfolio tracking, and reports.
  - Can upgrade to PRO through the billing flow.

### 2.1 Access Enforcement

- Use RBAC at both API and frontend layers.
- Protect admin routes and settings UI with `admin` role validation.
- Gate PRO features based on subscription status.
- Enforce JWT authentication and session expiration.
- Apply database Row-Level Security (RLS) to separate user data.

## 3. Admin Governance Rules

- Admin accounts require strong passwords and MFA.
- Conduct monthly admin access reviews.
- Separate operational admin duties from financial/billing administration.
- Restrict billing and pricing changes to a limited group of admins.
- Document and timestamp all changes to subscription and pricing rules.

## 4. Core Decision Rules

### 4.1 Trading Layers

- **Conservative/Base Layer**
  - Core account protection.
  - Primary focus is low drawdown, defined risk, and capital preservation.
  - Typical trade profile: delta 0.10–0.18, DTE 45–60, IV Rank > 30, market cap > $10B, margin < 40%.
- **Growth Layer**
  - Discretionary alpha capture.
  - Built with higher allocation tolerance and more aggressive entry criteria.
  - Typical trade profile: delta 0.20–0.30, DTE 30–45, IV Rank > 50, trend strong only.

### 4.2 Rule Sets

- **Base strategy rules** are always enforced for all trades.
- **Growth strategy rules** are enabled only when broader risk gates are satisfied.
- **DNT** (Do Not Trade) rules block trade execution when any disqualifying condition exists.
- **Regime-based rules** adjust allocations and trade eligibility by market state.

## 5. DNT (Do Not Trade) Rules

- **BR-010**: DNT is triggered when the broader market is defined as "down" or risk-on signals are not aligned.
- **BR-011**: Do not add new positions if any open trade has an active assignment alarm.
- **BR-012**: Halt new trade entry if account equity is below hard guardrail thresholds.
- **BR-013**: DNT is active if key correlations exceed configured risk thresholds.
- **BR-014**: DNT is active while premium decay and underlying volatility misalign with trade objectives.
- **BR-015**: DNT is active when weekly or monthly regime scores deteriorate below baseline.
- **BR-016**: If DNT is active, the platform only permits review mode and closed/existing trade monitoring.
- **BR-017**: Do not trade if spread > 10%.
- **BR-018**: Do not trade if open interest < 500.
- **BR-019**: Do not trade if market cap < $2B.
- **BR-020**: Do not trade if earnings event is within 14 days.
- **BR-021**: Do not trade if a NewsFlag is present.

## 6. Market Regime Rules

- **BR-020**: Market regime score is computed from multiple inputs, including volatility, trend, breadth, and macro sentiment.
- **BR-021**: Regime score is categorized into Conservative, Balanced, or Growth modes.
- **BR-022**: The platform displays the current regime mood and suggested layer exposure.
- **BR-023**: A regime score below conservative thresholds locks the Growth layer and tightens sizing.
- **BR-024**: A regime score above growth thresholds enables higher allocation and broader strategy choice.

## 7. Allocation and Position Sizing Rules

- **BR-025**: Target allocation is based on regime mode, current exposure, and risk budget.
- **BR-030**: Maximum allocation per trade is capped by the active strategy layer: Base layer receives the lowest cap, Growth layer receives a higher but bounded cap.
- **BR-031**: Account stop-loss and total exposure are monitored continuously.
- **BR-032**: Use the position sizing calculator to confirm contract quantity before trade creation.
- **BR-033**: Sizing is reduced if any existing trade is within a close-to-assignment or stop-loss trigger range.
- **BR-034**: Maintain band-level capital allocation limits for portfolio diversification.

### 7.1 Capital Band Limits

| Band | Description | Cap % |
|------|-------------|-------|
| Band A | Blue chip / Low volatility / Core holdings | 30 |
| Band B | Conservative growth / Quality midcaps | 25 |
| Band C | Core growth / Mid-risk names | 20 |
| Band D | Speculative / Event-driven names | 15 |
| Band E | High-risk / Small caps / Deep OTM plays | 10 |

## 7.2 Regime Allocation Rules

- **BR-035**: In DEFENSIVE regime, allocate 80% to Base and 20% to Growth.
- **BR-036**: In NORMAL regime, allocate 60% to Base and 40% to Growth.
- **BR-037**: In GROWTH regime, allocate 40% to Base and 60% to Growth.

## 7.3 Strategy Design Matrix Rules

- **BR-090**: The Strategy Design Matrix displays option strategies as rows and regime states (Defensive, Normal, Growth) as columns in a grid layout.
- **BR-091**: Each matrix cell shows the strategy's suitability for that regime including: availability status (Available / Limited / Blocked), compatible trading layers (Base, Growth), recommended capital bands (A–E), and current gate status.
- **BR-092**: Strategies are visually grayed out or blocked when DNT (Do Not Trade) is active or when the strategy is incompatible with the current regime.
- **BR-093**: Clicking a strategy cell navigates to the strategy's detailed configuration and analysis page.
- **BR-094**: The matrix updates in real-time as regime scores, market data, and portfolio state change.

## 7.4 Active Holdings & Trade Alerts Rules

- **BR-095**: Every active position displays a trade alert status: Normal (no action needed), Watch (monitor closely), Warning (consider action), or Critical (immediate action required).
- **BR-096**: Critical alerts are triggered by assignment risk exceeding thresholds, stop-loss breaches, or imminent regime deterioration. They are highlighted in red and require explicit user acknowledgment.
- **BR-097**: Each active position shows a suggested action: Hold, Roll, Close, or Hedge, based on current market conditions and position P&L.
- **BR-098**: Trade alerts persist until the position is closed or the alert condition is resolved and acknowledged by the user.

## 7.5 Active Holdings Page — Trade Alert Integration

- The Active Holdings & Trade Alerts page displays all active positions enriched with per-position alert data from BR-095–BR-098.
- Alert severity is visually indicated with color-coded badges and border highlights.
- Suggested action buttons (Roll, Close, Hedge) are rendered inline per position for one-click workflow.
- Greeks warnings (Delta, Theta, Vega breaches) are displayed per position alongside the alert.

## 8. Entry and Strategy Rules

- **BR-040**: Option strategy selection is driven by screen conditions and signal quality.
- **BR-041**: Limit new trade entries to candidate symbols that satisfy both technical marker and regime filters.
- **BR-042**: Base layer trades require stricter entry thresholds and smaller notional exposure.
- **BR-043**: Growth layer trades may use wider strike selection when regime conditions permit.
- **BR-044**: If any candidate violates a hard guardrail, it is removed from the active trade list.

## 8.5 Portfolio Dashboard and Trade Flow

- **BR-080**: Track Net Delta, Margin %, Sector Exposure, Total Risk, and current Regime State in the Portfolio Dashboard.
- **BR-081**: Block new trade entry if portfolio risk exceeds configured limits.
- **BR-082**: Trade flow must follow Market Data → Regime Engine → Allocation → Screening → Base/Growth Picks → TradeMaster → ActiveTrades.

## 9. Exit and Assignment Rules

- **BR-050**: Exit logic is based on realized/unrealized profit, time decay, assigned risk, and regime drift.
- **BR-051**: Close trades early when market regime deteriorates sharply.
- **BR-052**: If assignment risk rises above defined limits, notify user and recommend hedging or rolling.
- **BR-053**: System may auto-suggest exits when Greek exposures exceed configurable tolerances.
- **BR-054**: Existing trade management remains active even while DNT prohibits new entries.

## 10. Audit, Logging, and Change Control

- **BR-060**: Log all admin actions, settings changes, role updates, and feature toggles.
- **BR-061**: Log all trade decisions, including blocked signals and rule triggers.
- **BR-062**: Record every active trade addition and exit action with timestamp, user, and rule context.
- **BR-063**: Store a full immutable change log of regime score updates and gate rule modifications.
- **BR-064**: Provide audit exports for authorized reviewers.

## 11. Operational Escalation Rules

- **BR-070**: Notify admins if API latency exceeds 500ms for more than 5 minutes.
- **BR-071**: Send product/ops alerts if usage reaches 90% of free-tier quotas for 3 consecutive days.
- **BR-072**: If monthly cost passes 80% of projected revenue, trigger a formal cost review.
- **BR-073**: If a security event is detected, lock admin sessions and initiate escalation immediately.

## 12. Admin Screen and Controls

- Admin access requires the `admin` role and MFA.
- Admin UI surfaces user management, subscriptions, audit logs, and scheduler status.
- All admin operations must be auditable and reversible.
- Admin screens provide warnings for high-risk configuration changes.
- Billing and payment controls are strictly separated from product configuration controls.

## 13. Additional Compliance Notes

- Maintain a user-facing privacy policy and terms of service.
- Require explicit consent for email communications and notification preferences.
- Use standard encryption practices for all sensitive data at rest and in transit.
- Implement retention policies for logs and audit data according to privacy and compliance goals.
