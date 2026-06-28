import { useEffect, useRef, useState } from "react";
import { Clock, Menu, Search, RefreshCw, Bell, Settings, Download } from "lucide-react";
import { classNames } from "../../utils";
import styles from "./Header.module.css";

interface TickerData {
  symbol: string;
  price: string;
  change: string;
  changePercent: string;
  timestamp: Date;
}

const TICKERS = ["SPY", "QQQ", "DIA", "VIX"];
const POLL_INTERVAL = 30000; // 30 seconds
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Ticker Service
export const tickerService = {
  previousData: {} as Record<string, TickerData>,
  pollingId: null as ReturnType<typeof setInterval> | null,

  async fetchTickerData(): Promise<TickerData[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/market/tickers`);

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const tickersData = data.data || {};

      const results: TickerData[] = [];
      for (const symbol of TICKERS) {
        if (tickersData[symbol]) {
          const ticker = {
            symbol,
            price: tickersData[symbol].price,
            change: tickersData[symbol].change,
            changePercent: tickersData[symbol].changePercent,
            timestamp: new Date(),
          };
          results.push(ticker);
          this.previousData[symbol] = ticker;
        } else if (this.previousData[symbol]) {
          results.push(this.previousData[symbol]);
        }
      }

      console.log("✅ Tickers fetched successfully:", results.length);
      return results;
    } catch (error) {
      console.warn(`⚠️ Ticker fetch failed, using fallback:`, error);
      // Return cached data as fallback
      const cached = TICKERS
        .map((sym) => this.previousData[sym])
        .filter((d) => d !== undefined) as TickerData[];
      
      if (cached.length > 0) {
        console.log("📦 Using cached ticker data");
        return cached;
      }

      // Return empty array - will trigger shimmer state
      return [];
    }
  },

  async fetchAllTickers(): Promise<TickerData[]> {
    return this.fetchTickerData();
  },

  startPolling(callback: (data: TickerData[]) => void) {
    this.fetchAllTickers().then(callback);
    this.pollingId = setInterval(() => {
      this.fetchAllTickers().then(callback);
    }, POLL_INTERVAL);
  },

  stopPolling() {
    if (this.pollingId) {
      clearInterval(this.pollingId);
      this.pollingId = null;
    }
  },
};

// Ticker Box Component
function TickerBox({ data }: { data: TickerData | null }) {
  const isLoading = !data;
  const changeNum = data ? parseFloat(data.change) : 0;
  const isNegative = changeNum < 0;

  return (
    <div
      className={classNames(
        styles.indexBox,
        isLoading && styles.shimmerLoading
      )}
    >
      <span className={styles.indexLabel}>{isLoading ? "—" : data?.symbol}</span>
      <span className={styles.indexValue}>{isLoading ? "—" : data?.price}</span>
      <span
        className={classNames(
          styles.indexChange,
          isNegative ? styles.indexChangeNegative : styles.indexChangePositive
        )}
      >
        {isLoading ? "—" : `${changeNum >= 0 ? "+" : ""}${data?.changePercent}%`}
      </span>
      <span
        className={classNames(
          styles.indexPts,
          isNegative ? styles.indexPtsNegative : styles.indexPtsPositive
        )}
      >
        {isLoading ? "—" : `${changeNum >= 0 ? "+" : ""}${data?.change}`}
      </span>
    </div>
  );
}

export function Header({ onMenu }: { onMenu: () => void }) {
  const [tickers, setTickers] = useState<(TickerData | null)[]>(
    TICKERS.map(() => null)
  );
  const [lastRefreshed, setLastRefreshed] = useState<string>("Initializing...");
  const refreshCounterRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    // Start polling on mount
    tickerService.startPolling((data) => {
      setTickers(TICKERS.map((sym) => data.find((d) => d.symbol === sym) || null));
      updateRefreshTimestamp();
    });

    return () => {
      // Cleanup on unmount
      tickerService.stopPolling();
      if (refreshCounterRef.current) {
        clearInterval(refreshCounterRef.current);
      }
    };
  }, []);

  const updateRefreshTimestamp = () => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    });
    setLastRefreshed(`Last: ${timeStr}`);
  };

  const handleManualRefresh = async () => {
    const data = await tickerService.fetchAllTickers();
    setTickers(TICKERS.map((sym) => data.find((d) => d.symbol === sym) || null));
    updateRefreshTimestamp();
  };

  return (
    <header className={styles.header}>
      {/* Mobile Menu Button */}
      <button
        type="button"
        onClick={onMenu}
        className={styles.mobileMenuBtn}
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5" />
      </button>

      <div className={styles.headerLeft} id="tickerContainer">
        {tickers.map((tickerData, idx) => (
          <TickerBox key={TICKERS[idx]} data={tickerData} />
        ))}

        {/* Last Refreshed Timestamp */}
        <div className={styles.timestamp}>
          <Clock />
          <span id="lastRefreshedTime">{lastRefreshed}</span>
        </div>
      </div>

      <div className={styles.headerRight}>
        {/* Search */}
        <div className={styles.headerSearch}>
          <Search className={styles.searchIcon} />
          <input placeholder="Search active tickers... ⌘+F" type="text" />
        </div>

        {/* Action Icons */}
        <div className={styles.headerActions}>
          <button
            className={styles.headerIconBtn}
            onClick={handleManualRefresh}
            title="Refresh market feed"
          >
            <RefreshCw />
          </button>
          <button className={styles.headerIconBtn} title="System Notifications">
            <Bell />
            <span className={styles.notifDot}></span>
          </button>
          <button className={styles.headerIconBtn} title="Reset Workspace">
            <Settings />
          </button>
        </div>

        {/* Export Button */}
        <button className={styles.headerExportBtn} title="Export Holdings CSV">
          <Download />
          <span>Export Holdings CSV</span>
        </button>
      </div>
    </header>
  );
}
