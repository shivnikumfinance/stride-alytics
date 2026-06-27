/**
 * Shared TypeScript types mirroring `backend/app/api/v1/schemas/*`
 * and `shared/types/index.ts`.
 */

export type SubscriptionPlan = "free" | "pro";
export type OptionType = "call" | "put";
export type TradeType = "call" | "put" | "stock";
export type Direction = "long" | "short";
export type Regime = "bull" | "bear" | "ranging";

// ---------- Auth ----------

export interface User {
  id: string;
  email: string;
  full_name?: string;
  subscription_plan: SubscriptionPlan;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: "bearer";
  expires_in: number;
  user_id: string;
  email?: string;
  subscription_plan: SubscriptionPlan;
}

// ---------- Greeks ----------

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

// ---------- Screener ----------

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

// ---------- Regime ----------

export interface RegimeResponse {
  symbol: string;
  regime: Regime;
  confidence: number;
  lookback_days: number;
  price_return: number;
  as_of: string;
}

// ---------- Portfolio ----------

export interface PortfolioSummary {
  portfolio_id: string;
  name: string;
  total_trades: number;
  open_trades: number;
  closed_trades: number;
  total_pnl: number;
  win_rate: number;
  winners: number;
  losers: number;
}

export interface PortfolioListItem {
  id: string;
  name: string;
  description?: string | null;
}

export interface PortfolioCreate {
  name: string;
  description?: string | null;
}

// ---------- Trades ----------

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

// ---------- API envelope ----------

export interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: { type: string; status: number; message: string; details?: unknown };
}
