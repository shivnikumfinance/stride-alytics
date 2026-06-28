/** React Query hooks wrapping the typed API client. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  authApi,
  greeksApi,
  portfolioApi,
  regimeApi,
  screenerApi,
  tradesApi,
} from "../api/endpoints";
import { withApiErrorLogging } from "../api/errors";
import type {
  GreeksInputs,
  PortfolioCreate,
  PortfolioSummary,
  ScreenerFilters,
  TradeClose,
  TradeCreate,
  TradeOut,
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
    },
    onError: withApiErrorLogging("trades.create", "Could not add trade"),
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
