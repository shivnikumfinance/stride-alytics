"""
Streamlit dashboard for the Option Trading System.

Displays daily metrics, option scores, volatility data, and trades
from Supabase (real scanned data).
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.supabase_client import get_supabase_client
from app.utils.date_utils import format_date_mmm_dd_yyyy, normalize_date_for_merge


def _load_from_supabase(table: str) -> pd.DataFrame:
    try:
        client = get_supabase_client()
        resp = client.table(table).select("*").execute()
        data = resp.data or []
        return pd.DataFrame(data)
    except Exception as e:
        st.warning(f"Failed to load {table} from Supabase: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_daily_metrics() -> pd.DataFrame:
    daily = _load_from_supabase("daily_metrics")
    scores = _load_from_supabase("option_scores")
    bands = _load_from_supabase("bands")
    if daily.empty:
        return pd.DataFrame()
    
    # Normalize date format for merging
    if "date" in daily.columns:
        daily["date"] = daily["date"].astype(str).str[:10]
    if "date" in scores.columns:
        scores["date"] = scores["date"].astype(str).str[:10]
    if "date" in bands.columns:
        bands["date"] = bands["date"].astype(str).str[:10]
    
    if not scores.empty:
        daily = daily.merge(
            scores[["date", "ticker", "option_score", "trend", "strategy"]],
            on=["date", "ticker"],
            how="left",
        )
    if not bands.empty:
        daily = daily.merge(
            bands[["date", "ticker", "band"]],
            on=["date", "ticker"],
            how="left",
        )
    return daily


@st.cache_data
def get_option_scores() -> pd.DataFrame:
    df = _load_from_supabase("option_scores")
    if df.empty:
        return pd.DataFrame()
    bands = _load_from_supabase("bands")
    
    # Normalize date format for merging
    if "date" in df.columns:
        df["date"] = df["date"].astype(str).str[:10]
    if "date" in bands.columns:
        bands["date"] = bands["date"].astype(str).str[:10]
    
    # Merge with bands to get Band column
    if not bands.empty:
        df = df.merge(bands[["date", "ticker", "band"]], on=["date", "ticker"], how="left")
    df = df.rename(columns={
        "option_score": "Option Score",
        "ticker": "Ticker",
        "date": "Date",
        "trend": "Trend",
        "strategy": "Strategy Tag",
        "band": "Band",
    })
    # Format Date column
    if "Date" in df.columns:
        df["Date"] = df["Date"].apply(format_date_mmm_dd_yyyy)
    return df[["Ticker", "Date", "Option Score", "Trend", "Strategy Tag", "Band"]].copy()


@st.cache_data
def get_trades() -> pd.DataFrame:
    return pd.DataFrame()


def _normalize_daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # Normalize date column to string format for consistent merging
    if "date" in df.columns:
        df["date"] = df["date"].astype(str).str[:10]  # Take just YYYY-MM-DD part
    if "next_earnings_date" in df.columns:
        df["next_earnings_date"] = df["next_earnings_date"].astype(str).str[:10]
    
    rename_map = {
        "ticker": "Ticker",
        "date": "Date",
        "price": "Price",
        "option_volume": "Option Volume",
        "max_oi_near_exp": "Max OI (Near Exp)",
        "bid_ask_spread_pct": "Bid-Ask Spread %",
        "iv_30d": "IV 30d",
        "iv_rank_1y": "IV Rank (1y)",
        "hv_30d": "HV 30d",
        "atr": "ATR",
        "next_earnings_date": "Next Earnings Date",
        "short_interest_pct": "Short Interest %",
        "revenue_growth_yoy": "Revenue Growth (YoY)",
        "debt_equity": "Debt/Equity",
        "quality_score": "Quality Score (1-5)",
        "option_score": "Option Score",
        "band": "Band",
        "trend": "Trend (Above/Below 20/50/200 EMA)",
        "sector": "Sector",
    }
    df = df.rename(columns=rename_map)
    
    # Format Date columns after rename
    if "Date" in df.columns:
        df["Date"] = df["Date"].apply(format_date_mmm_dd_yyyy)
    if "Next Earnings Date" in df.columns:
        df["Next Earnings Date"] = df["Next Earnings Date"].apply(format_date_mmm_dd_yyyy)
    
    # Compute Volatility Bias and IV vs HV columns
    if "IV Rank (1y)" in df.columns:
        def vol_bias(val):
            if pd.isna(val):
                return "N/A"
            if val >= 50:
                return "Sell Premium"
            if val <= 30:
                return "Buy Premium"
            return "Neutral"
        df["Volatility Bias"] = df["IV Rank (1y)"].apply(vol_bias)
    
    if "IV 30d" in df.columns and "HV 30d" in df.columns:
        def iv_vs_hv(iv_30d, hv_30d):
            if pd.isna(iv_30d) or pd.isna(hv_30d):
                return "N/A"
            if iv_30d > hv_30d:
                return "IV > HV (Selling better)"
            if iv_30d < hv_30d:
                return "IV < HV (Buying better)"
            return "IV ≈ HV"
        df["IV vs HV"] = df.apply(
            lambda row: iv_vs_hv(row["IV 30d"], row["HV 30d"]), axis=1
        )
    
    return df


st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { font-size: 1.75rem; margin-top: 0; margin-bottom: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="Option Trading System", layout="wide")
st.markdown("# StrideAlytics Alpha Dashboard")

# Load data once at startup
raw = get_daily_metrics()
df = _normalize_daily_metrics(raw)

tab1, tab2, tab3, tab4 = st.tabs(["Screener", "Bands & Scores", "Volatility", "Trades"])

with tab1:
    st.subheader("Screener (Daily Metrics)")
    if not df.empty:
        display_cols = [
            "Ticker",
            "Price",
            "Option Score",
            "Band",
            "Trend (Above/Below 20/50/200 EMA)",
            "IV 30d",
            "IV Rank (1y)",
            "HV 30d",
            "Option Volume",
            "Max OI (Near Exp)",
            "Bid-Ask Spread %",
            "ATR",
            "Next Earnings Date",
            "Short Interest %",
            "Quality Score (1-5)",
        ]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], width="stretch")
    else:
        st.info("No daily metrics found.")

with tab2:
    st.subheader("Bands & Option Scores")
    scores = get_option_scores()
    if not scores.empty:
        score_cols = ["Ticker", "Date", "Option Score", "Trend", "Strategy Tag", "Band"]
        available = [c for c in score_cols if c in scores.columns]
        st.dataframe(scores[available], width="stretch")
    else:
        st.info("No option scores found.")

with tab3:
    st.subheader("Volatility (IV vs HV)")
    if not raw.empty:
        vol_cols = [
            "Ticker",
            "Date",
            "IV 30d",
            "IV Rank (1y)",
            "HV 30d",
            "ATR",
            "Next Earnings Date",
            "Sector",
            "Volatility Bias",
            "IV vs HV",
        ]
        available = [c for c in vol_cols if c in df.columns]
        if available:
            st.dataframe(df[available], width="stretch")
        else:
            st.warning("Volatility columns missing in daily_metrics.")
    else:
        st.info("No daily metrics found.")

with tab4:
    st.subheader("Trades & P&L")
    trades = get_trades()
    if not trades.empty:
        st.dataframe(trades, width="stretch")
    else:
        st.info("No trades found.")