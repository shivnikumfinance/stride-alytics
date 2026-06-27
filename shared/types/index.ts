export interface User {
  id: string;
  email: string;
  full_name?: string;
  subscription_plan: "free" | "pro";
}

export interface Portfolio {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Trade {
  id: string;
  portfolio_id: string;
  symbol: string;
  trade_type: "call" | "put" | "stock";
  direction: "long" | "short";
  entry_price: number;
  exit_price?: number;
  quantity: number;
  entry_date: string;
  exit_date?: string;
  pnl?: number;
}

export interface Option {
  symbol: string;
  strike: number;
  expiry: string;
  option_type: "call" | "put";
  bid: number;
  ask: number;
  implied_vol: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
}

export interface Greeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
  price_call: number;
  price_put: number;
}