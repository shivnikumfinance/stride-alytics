/** Typed wrappers around `/api/v1/*` endpoints. */

import client from "./client";
import type {
  GreeksInputs,
  GreeksResult,
  LoginRequest,
  PortfolioCreate,
  PortfolioListItem,
  PortfolioSummary,
  RegimeResponse,
  ScreenerFilters,
  ScreenerResponse,
  SignupRequest,
  TokenResponse,
  TradeClose,
  TradeCreate,
  TradeOut,
} from "../types";

// --- Auth ---

export const authApi = {
  login: (body: LoginRequest) => client.post<TokenResponse>("/auth/login", body).then((r) => r.data),
  signup: (body: SignupRequest) => client.post<TokenResponse>("/auth/signup", body).then((r) => r.data),
  me: () => client.get("/auth/me").then((r) => r.data),
};

// --- Greeks ---

export const greeksApi = {
  calculate: (body: GreeksInputs) => client.post<GreeksResult>("/greeks/calculate", body).then((r) => r.data),
};

// --- Screener ---

export const screenerApi = {
  run: (body: ScreenerFilters) => client.post<ScreenerResponse>("/screener/run", body).then((r) => r.data),
  limits: () => client.get("/screener/limits").then((r) => r.data),
};

// --- Regime ---

export const regimeApi = {
  get: (symbol: string, lookbackDays = 30) =>
    client.get<RegimeResponse>(`/regime/${encodeURIComponent(symbol)}`, { params: { lookback_days: lookbackDays } }).then((r) => r.data),
};

// --- Portfolio ---

export const portfolioApi = {
  list: () => client.get<{ success: boolean; data: PortfolioListItem[] }>("/portfolio").then((r) => r.data),
  create: (body: PortfolioCreate) => client.post<PortfolioSummary>("/portfolio", body).then((r) => r.data),
  summary: (id: string) => client.get<PortfolioSummary>(`/portfolio/${id}`).then((r) => r.data),
};

// --- Trades ---

export const tradesApi = {
  list: (portfolioId: string) => client.get<TradeOut[]>(`/trades/${portfolioId}`).then((r) => r.data),
  create: (body: TradeCreate) => client.post<TradeOut>("/trades", body).then((r) => r.data),
  close: (tradeId: string, body: TradeClose) =>
    client.post<TradeOut>(`/trades/${tradeId}/close`, body).then((r) => r.data),
};
