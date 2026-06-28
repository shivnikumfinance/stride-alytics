/**
 * Ticker polling service.
 *
 * All HTTP work goes through {@link marketApi} in `api/endpoints.ts`,
 * and the axios client (with JWT + interceptors) is the single source
 * of truth for baseURL construction. This file owns only polling,
 * caching, and the contract that the `Header` component consumes.
 */

import { marketApi } from "../endpoints";
import type { TickerData } from "../../types/market";

const DEFAULT_TICKERS: readonly string[] = ["SPY", "QQQ", "DIA", "VIX"];
const POLL_INTERVAL_MS = 30_000;

export interface TickerServiceOptions {
  symbols?: readonly string[];
  pollIntervalMs?: number;
}

export const tickerService = {
  previousData: {} as Record<string, TickerData>,
  pollingId: null as ReturnType<typeof setInterval> | null,
  symbols: DEFAULT_TICKERS,
  pollIntervalMs: POLL_INTERVAL_MS,

  configure(opts: TickerServiceOptions = {}) {
    if (opts.symbols) this.symbols = opts.symbols;
    if (opts.pollIntervalMs) this.pollIntervalMs = opts.pollIntervalMs;
  },

  async fetchTickerData(): Promise<TickerData[]> {
    try {
      const payload = await marketApi.tickers();
      const tickersData = payload.data ?? {};

      const results: TickerData[] = [];
      for (const symbol of this.symbols) {
        const raw = tickersData[symbol];
        if (raw) {
          const ticker: TickerData = {
            symbol,
            price: raw.price,
            change: raw.change,
            changePercent: raw.changePercent,
            timestamp: new Date(),
          };
          results.push(ticker);
          this.previousData[symbol] = ticker;
        } else if (this.previousData[symbol]) {
          results.push(this.previousData[symbol]);
        }
      }

      return results;
    } catch (error) {
      console.warn("⚠️ Ticker fetch failed, using fallback:", error);
      const cached = this.symbols
        .map((sym) => this.previousData[sym])
        .filter((d): d is TickerData => d !== undefined);

      return cached;
    }
  },

  async fetchAllTickers(): Promise<TickerData[]> {
    return this.fetchTickerData();
  },

  startPolling(callback: (data: TickerData[]) => void) {
    this.fetchAllTickers().then(callback);
    this.pollingId = setInterval(() => {
      this.fetchAllTickers().then(callback);
    }, this.pollIntervalMs);
  },

  stopPolling() {
    if (this.pollingId) {
      clearInterval(this.pollingId);
      this.pollingId = null;
    }
  },
};
