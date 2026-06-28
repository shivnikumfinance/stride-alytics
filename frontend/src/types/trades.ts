/** Mirrors `backend/app/api/v1/schemas/trade.py`. */

import type { TradeType, Direction } from "./common";

export interface TradeOut {
  trade_id: string;
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
}

export interface TradeClose {
  exit_price: number;
  exit_date: string;
}
