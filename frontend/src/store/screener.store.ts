/** Screener store — holds the active filter set, results, and pagination. */

import { create } from "zustand";
import type { ScreenerFilters, ScreenerRow } from "../types";

const DEFAULT_FILTERS: ScreenerFilters = {
  symbol: "AAPL",
  min_strike: null,
  max_strike: null,
  expiry_days_min: 0,
  expiry_days_max: 60,
  option_type: null,
  min_volume: 0,
  min_open_interest: 0,
  max_iv: null,
  min_iv: null,
  limit: 50,
};

interface ScreenerStoreState {
  filters: ScreenerFilters;
  results: ScreenerRow[];
  spot: number | null;
  loading: boolean;
  setFilters: (partial: Partial<ScreenerFilters>) => void;
  resetFilters: () => void;
  setResults: (results: ScreenerRow[], spot: number) => void;
  setLoading: (loading: boolean) => void;
}

export const useScreenerStore = create<ScreenerStoreState>((set) => ({
  filters: DEFAULT_FILTERS,
  results: [],
  spot: null,
  loading: false,

  setFilters: (partial) => set((s) => ({ filters: { ...s.filters, ...partial } })),
  resetFilters: () => set({ filters: DEFAULT_FILTERS }),
  setResults: (results, spot) => set({ results, spot }),
  setLoading: (loading) => set({ loading }),
}));
