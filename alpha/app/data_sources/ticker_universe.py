"""
Dynamic Ticker Universe Loader for Alpha Option Trading System.

Supports multiple sources:
- S&P 500 constituents (Wikipedia scraping)
- NASDAQ 100 constituents (Wikipedia scraping)
- Most active tickers (FMP API)
- Custom watchlist (local CSV / Supabase)
"""
import io
import os
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from app.config import config
from app.database.supabase_client import get_supabase_client

load_dotenv()


def get_sp500_tickers() -> list[str]:
    """Fetch S&P 500 constituents from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        df = pd.read_html(str(table))[0]
        tickers = df["Symbol"].tolist()
        return [str(t).replace(".", "-") for t in tickers]
    except Exception as e:
        print(f"⚠️ Failed to fetch S&P 500 tickers: {e}")
        return []


def get_nasdaq100_tickers() -> list[str]:
    """Fetch NASDAQ 100 constituents from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        df = pd.read_html(str(table))[0]
        tickers = df["Ticker"].tolist()
        return [str(t).replace(".", "-") for t in tickers]
    except Exception as e:
        print(f"⚠️ Failed to fetch NASDAQ 100 tickers: {e}")
        return []


def get_most_active_tickers(limit: int = 200) -> list[str]:
    """Fetch most active tickers from FMP API."""
    if not config.FMP_API_KEY:
        return []
    try:
        url = f"https://financialmodelingprep.com/api/v3/actives?apikey={config.FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        tickers = [item["ticker"] for item in data[:limit]]
        return tickers
    except Exception as e:
        print(f"⚠️ Failed to fetch most active tickers: {e}")
        return []


def get_custom_universe() -> list[str]:
    """Load custom ticker universe from alpha/universe/ directory."""
    universe_dir = "universe"
    if not os.path.exists(universe_dir):
        return []
    tickers = set()
    for fname in os.listdir(universe_dir):
        if fname.endswith(".csv"):
            fpath = os.path.join(universe_dir, fname)
            try:
                df = pd.read_csv(fpath)
                if "ticker" in df.columns:
                    tickers.update(df["ticker"].tolist())
                elif "Ticker" in df.columns:
                    tickers.update(df["Ticker"].tolist())
            except Exception as e:
                print(f"⚠️ Failed to read {fpath}: {e}")
    return sorted(list(tickers))


# Persistent master list stored in Supabase (optional)
def save_universe_to_supabase(tickers: list[str]) -> None:
    """Persist ticker universe to Supabase for tracking."""
    try:
        supabase = get_supabase_client()
        now = pd.Timestamp.now().isoformat()
        rows = [{"ticker": t, "added_at": now, "source": "universe_scanner"} for t in tickers]
        supabase.table("ticker_universe").upsert(rows, on_conflict=["ticker"]).execute()
    except Exception as e:
        print(f"⚠️ Failed to save universe to Supabase: {e}")


def load_tickers(
    use_sp500: bool = True,
    use_nasdaq100: bool = True,
    use_most_active: bool = True,
    use_custom: bool = True,
    max_total: int = 2000,
) -> list[str]:
    """
    Load the full trading universe for ingestion.

    Parameters
    ----------
    use_sp500 : bool
        Include S&P 500 constituents.
    use_nasdaq100 : bool
        Include NASDAQ 100 constituents.
    use_most_active : bool
        Include most active stocks from FMP.
    use_custom : bool
        Include custom watchlist from universe/ directory.
    max_total : int
        Maximum number of tickers to return (deduplicated).

    Returns
    -------
    list[str]
        Deduplicated list of ticker symbols.
    """
    sources = []
    if use_sp500:
        sources.append(("SP500", get_sp500_tickers()))
    if use_nasdaq100:
        sources.append(("NASDAQ100", get_nasdaq100_tickers()))
    if use_most_active:
        sources.append(("MOST_ACTIVE", get_most_active_tickers()))
    if use_custom:
        sources.append(("CUSTOM", get_custom_universe()))

    # Deduplicate while preserving order
    seen = set()
    tickers = []
    for source_name, source_tickers in sources:
        added = 0
        for t in source_tickers:
            if t not in seen:
                seen.add(t)
                tickers.append(t)
                added += 1
        print(f"📥 Added {added} tickers from {source_name}")

    # Trim to max
    tickers = tickers[:max_total]
    print(f"✅ Total universe size: {len(tickers)} tickers")
    return tickers