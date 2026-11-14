/** Mirrors the gate, sizing, regime-score and flag endpoints (Phase 2). */

import type { Band, Layer } from "./trades";

export type RegimeState = "DEFENSIVE" | "NORMAL" | "GROWTH" | "UNKNOWN";

export interface GateReason {
  rule_id: string;
  message: string;
  /** "block" = a rule failed; "data" = it could not be verified (which also blocks). */
  kind: "block" | "data";
}

export interface GateData {
  clear: boolean;
  status: string; // "CLEAR TO TRADE" | "BLOCKED" | "NOT GATED"
  reasons: GateReason[];
  checked: string[];
  not_evaluated: string[];
  skipped?: boolean;
  message?: string;
  regime_state?: RegimeState;
}

export interface RegimeScoreData {
  score: number | null;
  state: RegimeState;
  components: Record<string, number | null>;
  weights: Record<string, number>;
  missing: string[];
  market_down: boolean | null;
  vix: number | null;
  iv_rank: number | null;
  as_of: string;
  /** "live" | "stored" | "unavailable" */
  source: string;
}

export interface MasterGate extends GateData {
  regime: RegimeScoreData;
  equity: number;
  min_equity: number;
  enforce_gate: boolean;
  layer_split: { base: number; growth: number };
  growth_locked: boolean;
}

export interface RegimeHistoryRow {
  as_of: string;
  score: number | null;
  state: RegimeState;
  vix: number | null;
  iv_rank: number | null;
  market_down: boolean | null;
  source: string;
}

export interface GateCheckRequest {
  symbol: string;
  trade_type: "call" | "put" | "stock";
  layer?: Layer | null;
  strike?: number | null;
  expiry?: string | null;
  entry_date?: string | null;
}

export interface SizingRequest {
  layer: Layer;
  credit?: number | null;
  max_loss_per_contract?: number | null;
  band?: Band | null;
  risk_pct?: number | null;
}

export interface SizingResult {
  mode: "max_loss" | "credit" | "none";
  risk_pct: number;
  risk_budget: number;
  quantity: number;
  risk_amount: number | null;
  blocked: boolean;
  reasons: { rule_id: string; message: string }[];
  warnings: string[];
  band: Band | null;
  band_cap_pct: number | null;
  band_exposure_after_pct: number | null;
  account_size: number;
  regime_state: RegimeState;
  layer_split: { base: number; growth: number };
}

export interface BandUsage {
  band: Band;
  exposure: number;
  exposure_pct: number;
  cap_pct: number;
  status: "ok" | "near" | "over";
}

export interface SymbolFlag {
  news_flag: boolean;
  note: string | null;
}
