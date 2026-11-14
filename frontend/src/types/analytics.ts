/** Mirrors the Phase 4 analytics endpoints: risk, scenarios, strategy matrix, option chain. */

import type { RegimeState } from "./trading";

export interface RiskBreach {
  rule_id: string;
  code: "total_risk" | "sector" | "net_delta";
  message: string;
}

export interface SectorExposure {
  sector: string;
  capital_at_risk: number;
  pct_of_equity: number | null;
  pct_of_risk: number | null;
}

export interface PortfolioRisk {
  equity: number;
  capital_at_risk: number;
  /** Capital at risk as a share of equity (there is no broker margin feed). */
  margin_pct: number | null;
  net_delta: number;
  net_delta_dollars: number;
  net_delta_pct: number | null;
  unpriced_positions: number;
  open_positions: number;
  sectors: SectorExposure[];
  breaches: RiskBreach[];
  limits: { capital_at_risk_pct: number; sector_risk_pct: number; net_delta_pct: number };
  regime_score: number | null;
  regime_state: RegimeState;
}

export interface ScenarioParams {
  spot_pct: number;
  iv_shift: number;
  days_forward: number;
}

export interface ScenarioPosition {
  trade_id: string;
  symbol: string;
  trade_type: "call" | "put" | "stock";
  direction: "long" | "short";
  quantity: number;
  priced: boolean;
  current_pnl: number | null;
  scenario_pnl: number | null;
  change: number | null;
  reason?: string;
}

export interface ScenarioResult {
  shock: ScenarioParams;
  positions: ScenarioPosition[];
  total_change: number;
  total_scenario_pnl: number;
  priced: number;
  unpriced: number;
  ladder: { spot_pct: number; total_change: number }[];
}

export interface SavedScenario {
  id: string;
  name: string;
  params: ScenarioParams;
  created_at: string | null;
}

export type Availability = "available" | "limited" | "blocked";

export interface MatrixCell {
  availability: Availability;
  base_availability: Availability;
  layers: ("base" | "growth")[];
  bands: string[];
  note: string;
  gate: "clear" | "blocked" | "unknown" | null;
  current: boolean;
  filtered: boolean;
}

export interface StrategyMatrix {
  regimes: ("DEFENSIVE" | "NORMAL" | "GROWTH")[];
  current_regime: "DEFENSIVE" | "NORMAL" | "GROWTH" | null;
  gate_clear: boolean | null;
  gate_reasons: { rule_id: string; message: string }[];
  regime_score: number | null;
  rows: { strategy: string; description: string; cells: Record<string, MatrixCell> }[];
}

export interface ChainSide {
  bid: number;
  ask: number;
  last: number;
  iv: number;
  delta: number | null;
  gamma: number | null;
  theta: number | null;
  vega: number | null;
  open_interest: number;
  volume: number;
  /** Probability a short option expires worthless (from delta). */
  pop_short: number | null;
}

export interface OptionChain {
  symbol: string;
  spot: number;
  source: string;
  expiry: string;
  dte: number;
  expiries: string[];
  strikes: { strike: number; call: ChainSide | null; put: ChainSide | null }[];
}

export interface CalibrationGroup {
  group: string;
  trades: number;
  win_rate: number;
  avg_pnl: number;
  total_pnl: number;
  avg_expected: number | null;
  with_expected: number;
}

export interface Calibration {
  groups: CalibrationGroup[];
  total_trades: number;
  note: string;
}
