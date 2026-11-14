import type { AlertReason, DashboardSummary, PositionAlert, Severity } from "../types";

export function reason(over: Partial<AlertReason> = {}): AlertReason {
  return {
    code: "assignment_risk",
    severity: "critical",
    message: "Delta 0.80 is at or above 0.7: assignment alarm.",
    action: "roll",
    rule_id: "BR-052",
    acknowledged: false,
    ...over,
  };
}

export function alert(over: Partial<PositionAlert> = {}): PositionAlert {
  return {
    trade_id: "t1",
    symbol: "AAPL",
    trade_type: "put",
    direction: "short",
    quantity: 1,
    strategy_detail: { strike: 190, expiry: "2026-07-17", layer: "base", band: "A", entry_price: 2, risk_amount: 1000 },
    severity: "critical",
    action: "roll",
    reasons: [reason()],
    dte: 20,
    pnl: -100,
    pnl_pct: -0.5,
    delta: -0.8,
    position_delta: 80,
    theta: 4,
    spot: 180,
    mark: 3,
    itm: true,
    assignment_risk: true,
    data_available: true,
    unacknowledged_critical: true,
    ...over,
  };
}

export const SUMMARY_COUNTS: Record<Severity, number> = { normal: 1, watch: 1, warning: 0, critical: 1 };

export function summary(over: Partial<DashboardSummary> = {}): DashboardSummary {
  return {
    metrics: {
      portfolio_value: 99910,
      cash_available: 94900,
      realized_pnl: -100,
      unrealized_pnl: 10,
      unrealized_complete: true,
      open_trades: 2,
      options_buying_power: 94900,
      capital_at_risk: 5000,
      utilization_pct: 5,
      account_size: 100000,
    },
    alerts: { summary: SUMMARY_COUNTS, unacknowledged_critical: 1, top: [alert()] },
    holdings: [alert(), alert({ trade_id: "t2", symbol: "MSFT", severity: "normal", reasons: [], pnl: 25, unacknowledged_critical: false })],
    picks: {
      week_of: "2026-06-01",
      top: [
        { id: "p1", symbol: "NVDA", side: "call", strike: 900, expiry: "2026-07-17", entry_price: 5, target_price: 8, stop_loss: 3, rationale: "Momentum", confidence: 0.82, week_of: "2026-06-01" },
      ],
    },
    regime: { score: 62.5, state: "NORMAL", layer_split: { base: 60, growth: 40 }, growth_locked: false },
    ...over,
  };
}

export const calmGate = {
  clear: true,
  status: "CLEAR TO TRADE",
  reasons: [],
  checked: [],
  not_evaluated: [],
  regime: { score: 62.5, state: "NORMAL" as const, components: {}, weights: {}, missing: [], market_down: false, vix: 17, iv_rank: 40, as_of: "2026-06-01", source: "live" },
  equity: 100000,
  min_equity: 0,
  enforce_gate: true,
  layer_split: { base: 60, growth: 40 },
  growth_locked: false,
};
