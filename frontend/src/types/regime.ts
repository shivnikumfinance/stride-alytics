/** Mirrors `backend/app/api/v1/schemas/regime.py`. */

import type { Regime } from "./common";

export interface RegimeResponse {
  symbol: string;
  regime: Regime;
  confidence: number;
  lookback_days: number;
  price_return: number;
  as_of: string;
}
