/** Mirrors `backend/app/api/v1/schemas/screener.py`. */

import type { OptionType } from "./common";

export interface ScreenerFilters {
  symbol: string;
  min_strike?: number | null;
  max_strike?: number | null;
  expiry_days_min: number;
  expiry_days_max: number;
  option_type?: OptionType | null;
  min_volume: number;
  min_open_interest: number;
  max_iv?: number | null;
  min_iv?: number | null;
  limit: number;
}

export interface ScreenerRow {
  symbol: string;
  strike: number;
  expiry: string;
  option_type: OptionType;
  bid: number;
  ask: number;
  last_price: number;
  implied_vol: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  open_interest: number;
  volume: number;
}

export interface ScreenerResponse {
  success: true;
  symbol: string;
  spot: number;
  count: number;
  results: ScreenerRow[];
}
