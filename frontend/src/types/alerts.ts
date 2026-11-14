/** Mirrors the alerts, picks and dashboard endpoints (Phase 3). */

import type { RegimeState } from "./trading";

export type Severity = "normal" | "watch" | "warning" | "critical";
export type SuggestedAction = "hold" | "roll" | "close" | "hedge";

export interface AlertReason {
  code: string;
  severity: Severity;
  message: string;
  action: SuggestedAction;
  rule_id: string | null;
  /** null for watch-level reasons (only warning and critical can be acknowledged). */
  acknowledged: boolean | null;
}

export interface PositionAlert {
  trade_id: string;
  symbol: string;
  trade_type: "call" | "put" | "stock";
  direction: "long" | "short";
  quantity: number;
  strategy_detail: {
    strike: number | null;
    expiry: string | null;
    layer: string | null;
    band: string | null;
    entry_price: number;
    risk_amount: number | null;
  };
  severity: Severity;
  action: SuggestedAction;
  reasons: AlertReason[];
  dte: number | null;
  pnl: number | null;
  pnl_pct: number | null;
  delta: number | null;
  position_delta: number | null;
  theta: number | null;
  spot: number | null;
  mark: number | null;
  itm: boolean | null;
  assignment_risk: boolean;
  data_available: boolean;
  unacknowledged_critical: boolean;
}

export interface ExitAlertsData {
  alerts: PositionAlert[];
  summary: Record<Severity, number>;
  unacknowledged_critical: number;
  open_positions: number;
  regime: { score: number | null; state: RegimeState };
}

export interface AckRequest {
  trade_id: string;
  code: string;
  note?: string | null;
}

export interface AckRecord {
  id: string;
  trade_id: string;
  code: string;
  severity: Severity;
  note: string | null;
  acknowledged_at: string;
  resolved_at: string | null;
}

export interface WeeklyPick {
  id: string;
  symbol: string;
  side: "call" | "put" | "stock";
  strike: number | null;
  expiry: string | null;
  entry_price: number;
  target_price: number | null;
  stop_loss: number | null;
  rationale: string;
  confidence: number;
  week_of: string;
  /** Expected value per contract in dollars, from confidence and target/stop; null if missing. */
  ev?: number | null;
}

export interface DashboardSummary {
  metrics: {
    portfolio_value: number;
    cash_available: number;
    realized_pnl: number;
    unrealized_pnl: number;
    unrealized_complete: boolean;
    open_trades: number;
    options_buying_power: number;
    capital_at_risk: number;
    utilization_pct: number | null;
    account_size: number;
  };
  alerts: {
    summary: Record<Severity, number>;
    unacknowledged_critical: number;
    top: PositionAlert[];
  };
  holdings: PositionAlert[];
  picks: { week_of: string | null; top: WeeklyPick[] };
  regime: {
    score: number | null;
    state: RegimeState;
    layer_split: { base: number; growth: number };
    growth_locked: boolean;
  };
}
