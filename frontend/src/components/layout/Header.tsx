import { useEffect, useRef, useState } from "react";
import { Clock, Menu, Search, RefreshCw, Bell, Settings, Download } from "lucide-react";
import { classNames } from "../../utils";
import { tickerService } from "../../api/services/ticker.service";
import type { TickerData } from "../../types/market";
import styles from "./Header.module.css";

const TICKERS = ["SPY", "QQQ", "DIA", "VIX"];

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
    // Capture the current value into a local — the ref itself can change
    // between now and cleanup, and we want to clear exactly the interval
    // we own.
    const interval = refreshCounterRef.current;

    // Start polling on mount
    tickerService.startPolling((data) => {
      setTickers(TICKERS.map((sym) => data.find((d) => d.symbol === sym) || null));
      updateRefreshTimestamp();
    });

    return () => {
      // Cleanup on unmount
      tickerService.stopPolling();
      if (interval) {
        clearInterval(interval);
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
          <input placeholder="Search Active Ticker" type="text" />
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
