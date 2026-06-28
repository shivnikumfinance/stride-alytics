/** Mirrors `backend/app/api/v1/schemas/greeks.py`. */

import type { OptionType } from "./common";

export interface GreeksInputs {
  spot: number;
  strike: number;
  time_to_expiry: number;
  risk_free_rate: number;
  volatility: number;
  option_type: OptionType;
}

export interface GreeksResult {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
  price_call: number;
  price_put: number;
  inputs: GreeksInputs;
}
