/** React Query hooks wrapping the typed API client. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  authApi,
  gateApi,
  greeksApi,
  logsApi,
  marketApi,
  portfolioApi,
  regimeApi,
  screenerApi,
  settingsApi,
  sizingApi,
  symbolsApi,
  tradesApi,
  watchlistApi,
} from "../api/endpoints";
import { withApiErrorLogging } from "../api/errors";
import type {
  BandUsage,
  GateCheckRequest,
  GateData,
  GreeksInputs,
  LogFilters,
  PortfolioCreate,
  MasterGate,
  PortfolioSummary,
  RegimeHistoryRow,
  RegimeScoreData,
  ScreenerFilters,
  SettingsUpdate,
  SizingRequest,
  SizingResult,
  SymbolFlag,
  TradeClose,
  TradeCreate,
  TradeOut,
  UserSettings,
  Watchlist,
} from "../types";

// --- Auth ---

export const useMe = () =>
  useQuery({
    queryKey: ["auth", "me"],
    queryFn: () => authApi.me(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

// --- Screener ---

export const useRunScreener = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (filters: ScreenerFilters) => screenerApi.run(filters),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["screener"] }),
    onError: withApiErrorLogging("screener.run", "Screener request failed"),
  });
};

export const useScreenerLimits = () =>
  useQuery({
    queryKey: ["screener", "limits"],
    queryFn: () => screenerApi.limits(),
    staleTime: 60 * 60 * 1000,
  });

// --- Greeks ---

export const useCalculateGreeks = () =>
  useMutation({
    mutationFn: (inputs: GreeksInputs) => greeksApi.calculate(inputs),
    onError: withApiErrorLogging("greeks.calculate", "Greeks calculation failed"),
  });

// --- Regime ---

export const useRegime = (symbol: string, lookbackDays = 30) =>
  useQuery({
    queryKey: ["regime", symbol, lookbackDays],
    queryFn: () => regimeApi.get(symbol, lookbackDays),
    enabled: !!symbol,
    staleTime: 60 * 60 * 1000,
  });

// --- Portfolio ---

export const usePortfolios = () =>
  useQuery({
    queryKey: ["portfolios"],
    queryFn: () => portfolioApi.list(),
  });

export const useCreatePortfolio = () => {
  const qc = useQueryClient();
  return useMutation<PortfolioSummary, Error, PortfolioCreate>({
    mutationFn: (body) => portfolioApi.create(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["portfolios"] }),
    onError: withApiErrorLogging("portfolio.create", "Could not create portfolio"),
  });
};

export const usePortfolioSummary = (id?: string) =>
  useQuery({
    queryKey: ["portfolio", id, "summary"],
    queryFn: () => portfolioApi.summary(id!),
    enabled: !!id,
  });

// --- Trades ---

export const useTrades = (portfolioId?: string) =>
  useQuery<TradeOut[]>({
    queryKey: ["trades", portfolioId],
    queryFn: () => tradesApi.list(portfolioId!),
    enabled: !!portfolioId,
  });

export const useAddTrade = (portfolioId?: string) => {
  const qc = useQueryClient();
  return useMutation<TradeOut, Error, TradeCreate>({
    mutationFn: (body) => tradesApi.create(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["trades", portfolioId] });
      qc.invalidateQueries({ queryKey: ["portfolio"] });
      qc.invalidateQueries({ queryKey: ["gate"] });
      qc.invalidateQueries({ queryKey: ["logs"] });
    },
    onError: (err: unknown) => {
      withApiErrorLogging("trades.create", "Could not add trade")(err);
    },
  });
};

export const useCloseTrade = (portfolioId?: string) => {
  const qc = useQueryClient();
  return useMutation<TradeOut, Error, { tradeId: string; body: TradeClose }>({
    mutationFn: ({ tradeId, body }) => tradesApi.close(tradeId, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["trades", portfolioId] });
      qc.invalidateQueries({ queryKey: ["portfolio"] });
    },
    onError: withApiErrorLogging("trades.close", "Could not close trade"),
  });
};

// --- Watchlists ---

export const useWatchlists = () =>
  useQuery<Watchlist[]>({ queryKey: ["watchlists"], queryFn: () => watchlistApi.list() });

export const useCreateWatchlist = () => {
  const qc = useQueryClient();
  return useMutation<Watchlist, Error, { name: string; symbols?: string[] }>({
    mutationFn: ({ name, symbols }) => watchlistApi.create(name, symbols),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
    onError: withApiErrorLogging("watchlist.create", "Could not create watchlist"),
  });
};

export const useDeleteWatchlist = () => {
  const qc = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => watchlistApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
    onError: withApiErrorLogging("watchlist.delete", "Could not delete watchlist"),
  });
};

export const useAddSymbol = () => {
  const qc = useQueryClient();
  return useMutation<Watchlist, Error, { id: string; symbol: string }>({
    mutationFn: ({ id, symbol }) => watchlistApi.addSymbol(id, symbol),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
    onError: withApiErrorLogging("watchlist.add_symbol", "Could not add symbol"),
  });
};

export const useRemoveSymbol = () => {
  const qc = useQueryClient();
  return useMutation<Watchlist, Error, { id: string; symbol: string }>({
    mutationFn: ({ id, symbol }) => watchlistApi.removeSymbol(id, symbol),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
    onError: withApiErrorLogging("watchlist.remove_symbol", "Could not remove symbol"),
  });
};

/** Quotes for a watchlist's symbols (refetched every 60 s while the page is open). */
export const useQuotes = (symbols: readonly string[]) =>
  useQuery({
    queryKey: ["quotes", [...symbols].sort().join(",")],
    queryFn: () => marketApi.tickers(symbols),
    enabled: symbols.length > 0,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

// --- Settings ---

export const useSettings = () =>
  useQuery<UserSettings>({ queryKey: ["settings"], queryFn: () => settingsApi.get() });

export const useUpdateSettings = () => {
  const qc = useQueryClient();
  return useMutation<UserSettings, Error, SettingsUpdate>({
    mutationFn: (body) => settingsApi.update(body),
    onSuccess: (data) => {
      qc.setQueryData(["settings"], data);
      qc.invalidateQueries({ queryKey: ["logs"] });
    },
    onError: withApiErrorLogging("settings.update", "Could not save settings"),
  });
};

// --- Logs ---

export const useSignalLog = (filters: LogFilters = {}) =>
  useQuery({ queryKey: ["logs", "signals", filters], queryFn: () => logsApi.signals(filters) });

export const useAuditLog = (filters: LogFilters = {}) =>
  useQuery({ queryKey: ["logs", "audit", filters], queryFn: () => logsApi.audit(filters) });

// --- Gate, regime score, sizing, bands, flags ---

/** The master gate (CLEAR TO TRADE / BLOCKED). Re-checked every 5 minutes. */
export const useMasterGate = () =>
  useQuery<MasterGate>({
    queryKey: ["gate"],
    queryFn: () => gateApi.master(),
    staleTime: 60_000,
    refetchInterval: 5 * 60_000,
    retry: 1,
  });

export const useGateCheck = () =>
  useMutation<GateData, Error, GateCheckRequest>({
    mutationFn: (body) => gateApi.check(body),
    onError: withApiErrorLogging("gate.check", "Could not check the gate"),
  });

export const useRegimeScore = () =>
  useQuery<RegimeScoreData>({
    queryKey: ["regime", "score"],
    queryFn: () => regimeApi.score(),
    staleTime: 5 * 60_000,
  });

export const useRegimeHistory = (limit = 30) =>
  useQuery<RegimeHistoryRow[]>({
    queryKey: ["regime", "history", limit],
    queryFn: () => regimeApi.history(limit),
  });

export const useSizing = () =>
  useMutation<SizingResult, Error, SizingRequest>({
    mutationFn: (body) => sizingApi.calculate(body),
    onError: withApiErrorLogging("sizing.calculate", "Could not calculate the size"),
  });

export const useBands = () =>
  useQuery<BandUsage[]>({ queryKey: ["portfolio", "bands"], queryFn: () => portfolioApi.bands() });

export const useSymbolFlags = () =>
  useQuery<Record<string, SymbolFlag>>({
    queryKey: ["symbol-flags"],
    queryFn: () => symbolsApi.flags(),
  });

export const useSetSymbolFlag = () => {
  const qc = useQueryClient();
  return useMutation<unknown, Error, { symbol: string; news_flag: boolean }>({
    mutationFn: ({ symbol, news_flag }) => symbolsApi.setFlag(symbol, news_flag),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["symbol-flags"] });
      qc.invalidateQueries({ queryKey: ["gate"] });
      qc.invalidateQueries({ queryKey: ["logs"] });
    },
    onError: withApiErrorLogging("symbols.flag", "Could not update the flag"),
  });
};
