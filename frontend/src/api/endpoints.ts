/** Typed wrappers around `/api/v1/*` endpoints. */

import client from "./client";
import type { TickerPayload } from "../types/market";
import type {
  AckRecord,
  AckRequest,
  AuditLogEntry,
  DashboardSummary,
  ExitAlertsData,
  Severity,
  WeeklyPick,
  BandUsage,
  GateCheckRequest,
  GateData,
  MasterGate,
  RegimeHistoryRow,
  RegimeScoreData,
  SizingRequest,
  SizingResult,
  SymbolFlag,
  GreeksInputs,
  GreeksResult,
  LogFilters,
  LogPage,
  LoginRequest,
  PortfolioCreate,
  PortfolioListItem,
  PortfolioSummary,
  RegimeResponse,
  ScreenerFilters,
  ScreenerResponse,
  SettingsUpdate,
  SignalLogEntry,
  SignupRequest,
  TokenResponse,
  TradeClose,
  TradeCreate,
  TradeOut,
  TradePage,
  UserSettings,
  Watchlist,
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
  score: () => client.get<Envelope<RegimeScoreData>>("/regime/score").then((r) => r.data.data),
  history: (limit = 30) =>
    client.get<Envelope<RegimeHistoryRow[]>>("/regime/history", { params: { limit } }).then((r) => r.data.data),
  get: (symbol: string, lookbackDays = 30) =>
    client.get<RegimeResponse>(`/regime/${encodeURIComponent(symbol)}`, { params: { lookback_days: lookbackDays } }).then((r) => r.data),
};

// --- Portfolio ---

export const portfolioApi = {
  list: () => client.get<{ success: boolean; data: PortfolioListItem[] }>("/portfolio").then((r) => r.data),
  create: (body: PortfolioCreate) => client.post<PortfolioSummary>("/portfolio", body).then((r) => r.data),
  summary: (id: string) => client.get<PortfolioSummary>(`/portfolio/${id}`).then((r) => r.data),
  update: (id: string, body: { name?: string; description?: string | null }) =>
    client.patch<PortfolioSummary>(`/portfolio/${id}`, body).then((r) => r.data),
  remove: (id: string) => client.delete(`/portfolio/${id}`).then(() => undefined),
  bands: () => client.get<Envelope<BandUsage[]>>("/portfolio/bands").then((r) => r.data.data),
};

// --- Trades ---

export const tradesApi = {
  list: (portfolioId: string) => client.get<TradeOut[]>(`/trades/${portfolioId}`).then((r) => r.data),
  listAll: (params: { status?: "open" | "closed"; symbol?: string; sort?: string; limit?: number; offset?: number } = {}) =>
    client.get<TradePage>("/trades", { params }).then((r) => r.data),
  create: (body: TradeCreate) => client.post<TradeOut>("/trades", body).then((r) => r.data),
  updateNotes: (tradeId: string, notes: string | null) =>
    client.patch<TradeOut>(`/trades/${tradeId}`, { notes }).then((r) => r.data),
  close: (tradeId: string, body: TradeClose) =>
    client.post<TradeOut>(`/trades/${tradeId}/close`, body).then((r) => r.data),
};

// --- Watchlists ---

interface Envelope<T> {
  success: boolean;
  data: T;
}

export const watchlistApi = {
  list: () => client.get<Envelope<Watchlist[]>>("/watchlists").then((r) => r.data.data),
  create: (name: string, symbols: string[] = []) =>
    client.post<Envelope<Watchlist>>("/watchlists", { name, symbols }).then((r) => r.data.data),
  remove: (id: string) => client.delete(`/watchlists/${id}`).then(() => undefined),
  addSymbol: (id: string, symbol: string) =>
    client.post<Envelope<Watchlist>>(`/watchlists/${id}/symbols`, { symbol }).then((r) => r.data.data),
  removeSymbol: (id: string, symbol: string) =>
    client
      .delete<Envelope<Watchlist>>(`/watchlists/${id}/symbols/${encodeURIComponent(symbol)}`)
      .then((r) => r.data.data),
};

// --- Settings ---

export const settingsApi = {
  get: () => client.get<Envelope<UserSettings>>("/settings").then((r) => r.data.data),
  update: (body: SettingsUpdate) =>
    client.put<Envelope<UserSettings>>("/settings", body).then((r) => r.data.data),
  acceptDisclaimer: () =>
    client.post<Envelope<UserSettings>>("/settings/disclaimer").then((r) => r.data.data),
};

// --- Gate, sizing, symbol flags ---

export const gateApi = {
  master: () => client.get<Envelope<MasterGate>>("/gate").then((r) => r.data.data),
  check: (body: GateCheckRequest) =>
    client.post<Envelope<GateData>>("/gate/check", body).then((r) => r.data.data),
};

export const sizingApi = {
  calculate: (body: SizingRequest) =>
    client.post<Envelope<SizingResult>>("/sizing/calculate", body).then((r) => r.data.data),
};

export const symbolsApi = {
  flags: () =>
    client.get<Envelope<Record<string, SymbolFlag>>>("/symbols/flags").then((r) => r.data.data),
  setFlag: (symbol: string, news_flag: boolean, note?: string | null) =>
    client
      .put<Envelope<{ symbol: string } & SymbolFlag>>(`/symbols/${encodeURIComponent(symbol)}/flag`, {
        news_flag,
        note: note ?? null,
      })
      .then((r) => r.data.data),
};

// --- Alerts, picks, dashboard ---

export const alertsApi = {
  exits: (minSeverity: Severity = "watch") =>
    client
      .get<Envelope<ExitAlertsData>>("/alerts/exits", { params: { min_severity: minSeverity } })
      .then((r) => r.data.data),
  ack: (body: AckRequest) =>
    client.post<Envelope<AckRecord>>("/alerts/ack", body).then((r) => r.data.data),
  acks: (params: { limit?: number; offset?: number } = {}) =>
    client.get<LogPage<AckRecord>>("/alerts/acks", { params }).then((r) => r.data),
};

export const picksApi = {
  list: (weekOf?: string) =>
    client
      .get<{ success: boolean; data: WeeklyPick[]; week_of: string | null }>("/picks", {
        params: weekOf ? { week_of: weekOf } : undefined,
      })
      .then((r) => r.data),
};

export const dashboardApi = {
  summary: () => client.get<Envelope<DashboardSummary>>("/dashboard/summary").then((r) => r.data.data),
};

// --- Logs (append-only, read-only from the UI) ---

export const logsApi = {
  signals: (params: LogFilters = {}) =>
    client.get<LogPage<SignalLogEntry>>("/logs/signals", { params }).then((r) => r.data),
  audit: (params: LogFilters = {}) =>
    client.get<LogPage<AuditLogEntry>>("/logs/audit", { params }).then((r) => r.data),
};

// --- Market ---
// Canonical home for the wire types is `src/types/market.ts`.
// Import them directly from there — do NOT re-export them from this file
// (see docs/TECHNICAL/RULES/api-flow/API-FLOW.md — endpoint wrappers
// must not own domain types).

export const marketApi = {
  /** Returns the full ``TickerPayload`` envelope from ``/market/tickers``. */
  tickers: (symbols?: readonly string[]) =>
    client
      .get<TickerPayload>("/market/tickers", {
        params: symbols && symbols.length ? { symbols: symbols.join(",") } : undefined,
      })
      .then((r) => r.data),
};
