/** Greeks store — holds the calculator inputs and last computed result. */

import { create } from "zustand";
import type { GreeksInputs, GreeksResult } from "../types";

const DEFAULT_INPUTS: GreeksInputs = {
  spot: 100,
  strike: 100,
  time_to_expiry: 30 / 365,
  risk_free_rate: 0.05,
  volatility: 0.3,
  option_type: "call",
};

interface GreeksStoreState {
  inputs: GreeksInputs;
  result: GreeksResult | null;
  loading: boolean;
  error: string | null;
  setInputs: (partial: Partial<GreeksInputs>) => void;
  setResult: (result: GreeksResult) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useGreeksStore = create<GreeksStoreState>((set) => ({
  inputs: DEFAULT_INPUTS,
  result: null,
  loading: false,
  error: null,

  setInputs: (partial) => set((s) => ({ inputs: { ...s.inputs, ...partial } })),
  setResult: (result) => set({ result }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
