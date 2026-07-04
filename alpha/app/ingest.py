"""
Alpha Option Trading System — Data Ingestion Pipeline

This module pulls data from:
- Polygon (options chain)
- FMP (fundamentals)
- Massive (optional)
- yfinance (price, IV, HV, earnings)

Then merges everything into a unified DataFrame ready for business_logic.py.

Finally, it pushes raw daily metrics into Supabase.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime

from app.config import config
from app.database.supabase_client import get_supabase_client

# Data source modules
from app.data_sources.polygon import fetch_polygon_options
from app.data_sources.fmp_fundamentals import fetch_fmp_fundamentals
from app.data_sources.massive import fetch_massive_data_for_tickers


# ─────────────────────────────────────────────
# Supabase client
# ─────────────────────────────────────────────

supabase = get_supabase_client()


# ─────────────────────────────────────────────
# 1. Load Tickers Universe
# ─────────────────────────────────────────────


def load_tickers() -> list:
    """
    Load tickers for ingestion.
    You can replace this with:
    - Supabase table
    - Google Sheets
    - Local CSV
    - Hardcoded list
    """

    # Hardcoded starter universe (replace with your own)
    return ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "TSLA"]


# ─────────────────────────────────────────────
# 2. yfinance Data
# ─────────────────────────────────────────────


def fetch_yfinance_data(tickers: list) -> pd.DataFrame:
    rows = []

    for t in tickers:
        try:
            yf_ticker = yf.Ticker(t)
            info = yf_ticker.info

            rows.append(
                {
                    "ticker": t,
                    "price": info.get("currentPrice"),
                    "hv_30d": info.get("historicalVolatility"),
                    "next_earnings_date": str(info.get("earningsDate")[0])
                    if info.get("earningsDate")
                    else None,
                    "sector": info.get("sector"),
                }
            )
        except Exception as e:
            print(f"⚠️ yfinance error for {t}: {e}")

    return pd.DataFrame(rows).set_index("ticker")


# ─────────────────────────────────────────────
# 3. Merge All Sources
# ─────────────────────────────────────────────


def merge_sources(yf_df, polygon_df, fmp_df, massive_df=None):
    """
    Merge all data sources into a single DataFrame.
    """

    df = yf_df.copy()

    # Merge Polygon
    df = df.merge(polygon_df, left_index=True, right_index=True, how="left")

    # Merge FMP
    df = df.merge(fmp_df, left_index=True, right_index=True, how="left")

    # Merge Massive (optional)
    if massive_df is not None:
        df = df.merge(massive_df, left_index=True, right_index=True, how="left")

    return df


# ─────────────────────────────────────────────
# 4. Push Raw Daily Metrics to Supabase
# ─────────────────────────────────────────────


def push_daily_metrics(df: pd.DataFrame):
    """
    Push raw daily metrics into Supabase table: daily_metrics
    """

    df_to_push = df.reset_index().copy()
    df_to_push["date"] = datetime.now().strftime("%Y-%m-%d")

    # Clear old rows for today
    supabase.table("daily_metrics").delete().eq("date", df_to_push["date"].iloc[0]).execute()

    # Insert new rows
    rows = df_to_push.to_dict(orient="records")
    supabase.table("daily_metrics").insert(rows).execute()

    print("✅ daily_metrics updated in Supabase")


# ─────────────────────────────────────────────
# 5. Full Ingestion Pipeline
# ─────────────────────────────────────────────


def run_ingestion_pipeline() -> pd.DataFrame:
    """
    Run the full ingestion pipeline:
    - Load tickers
    - Fetch yfinance
    - Fetch Polygon
    - Fetch FMP
    - Fetch Massive (optional)
    - Merge
    - Push to Supabase
    - Return DataFrame
    """

    tickers = load_tickers()
    print(f"📥 Ingesting data for: {tickers}")

    # Fetch data
    yf_df = fetch_yfinance_data(tickers)
    polygon_df = fetch_polygon_options(tickers)
    fmp_df = fetch_fmp_fundamentals(tickers)

    # Massive is optional
    massive_df = None
    if config.MASSIVE_API_KEY:
        massive_df = fetch_massive_data_for_tickers(tickers)

    # Merge
    final_df = merge_sources(yf_df, polygon_df, fmp_df, massive_df)

    # Push to Supabase
    push_daily_metrics(final_df)

    print("🚀 Ingestion pipeline complete.")
    return final_df


# ─────────────────────────────────────────────
# 6. Manual Test Harness
# ─────────────────────────────────────────────

if __name__ == "__main__":
    df = run_ingestion_pipeline()
    print(df.head())
