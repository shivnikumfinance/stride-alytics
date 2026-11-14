/** Mirrors `backend/app/api/v1/schemas/portfolio.py` (trades). */

import type { TradeType, Direction } from "./common";

export type Layer = "base" | "growth";
export type Band = "A" | "B" | "C" | "D" | "E";

export interface TradeOut {
  trade_id: string;
  portfolio_id?: string | null;
  symbol: string;
  trade_type: TradeType;
  direction: Direction;
  quantity: number;
  entry_price: number;
  exit_price: number | null;
  entry_date: string;
  exit_date: string | null;
  pnl: number;
  open: boolean;
  notes?: string | null;
  strike?: number | null;
  expiry?: string | null;
  strategy?: string | null;
  layer?: Layer | null;
  band?: Band | null;
  risk_amount?: number | null;
  credit?: number | null;
}

export interface TradeCreate {
  portfolio_id: string;
  symbol: string;
  trade_type: TradeType;
  direction: Direction;
  entry_price: number;
  quantity: number;
  entry_date: string;
  notes?: string | null;
  strike?: number | null;
  expiry?: string | null;
  strategy?: string | null;
  layer?: Layer | null;
  band?: Band | null;
  risk_amount?: number | null;
  credit?: number | null;
}

export interface TradeClose {
  exit_price: number;
  exit_date: string;
}

export interface TradePage {
  success: boolean;
  data: TradeOut[];
  total: number;
  limit: number;
  offset: number;
}
