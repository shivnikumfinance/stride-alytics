/** Portfolio store — manages portfolio list and selected portfolio state. */

import { create } from "zustand";

interface Portfolio {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface PortfolioStoreState {
  portfolios: Portfolio[];
  selectedPortfolioId: string | null;
  loading: boolean;
  error: string | null;
  setPortfolios: (portfolios: Portfolio[]) => void;
  addPortfolio: (portfolio: Portfolio) => void;
  updatePortfolio: (id: string, updates: Partial<Portfolio>) => void;
  removePortfolio: (id: string) => void;
  selectPortfolio: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const usePortfolioStore = create<PortfolioStoreState>((set) => ({
  portfolios: [],
  selectedPortfolioId: null,
  loading: false,
  error: null,

  setPortfolios: (portfolios) => set({ portfolios }),
  addPortfolio: (portfolio) => set((s) => ({ portfolios: [...s.portfolios, portfolio] })),
  updatePortfolio: (id, updates) =>
    set((s) => ({
      portfolios: s.portfolios.map((p) => (p.id === id ? { ...p, ...updates } : p)),
    })),
  removePortfolio: (id) =>
    set((s) => ({
      portfolios: s.portfolios.filter((p) => p.id !== id),
      selectedPortfolioId: s.selectedPortfolioId === id ? null : s.selectedPortfolioId,
    })),
  selectPortfolio: (selectedPortfolioId) => set({ selectedPortfolioId }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));