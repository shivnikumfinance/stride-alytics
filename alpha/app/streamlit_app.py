"""
Streamlit dashboard for the Option Trading System.

Displays daily metrics, option scores, volatility data, and trades
using the local data pipeline.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for Streamlit Cloud compatibility
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.load_data import load_local_csv
from app.screener.compute_option_score import compute_option_score
from app.screener.band_pipeline import compute_bands


def _get_sample_data() -> pd.DataFrame:
    """Generate sample data matching the CSV format for testing."""
    csv_columns = [
        "Ticker",
        "Price",
        "Avg Volume (Shares)",
        "Option Volume",
        "Max OI (Near Exp)",
        "Bid-Ask Spread %",
        "IV 30d",
        "IV Rank (1y)",
        "HV 30d",
        "ATR",
        "Next Earnings Date",
        "Short Interest %",
        "Revenue Growth (YoY)",
        "Debt/Equity",
        "Quality Score (1–5)",
        "Trend (Above/Below 20/50/200 EMA)",
    ]
    sample_df = pd.DataFrame(
        [
            [
                "AAPL",
                190.50,
                45000000,
                5000,
                1200,
                3.5,
                0.35,
                65,
                0.25,
                2.5,
                "2026-07-28",
                1.2,
                0.12,
                1.3,
                5,
                "Above 20, 50, 200 (Bullish)",
            ],
            [
                "MSFT",
                330.25,
                25000000,
                3500,
                800,
                2.0,
                0.28,
                45,
                0.22,
                4.2,
                "2026-08-05",
                0.8,
                0.18,
                0.4,
                5,
                "Above 20, 50, 200 (Bullish)",
            ],
            [
                "GOOGL",
                140.80,
                18000000,
                4200,
                600,
                4.5,
                0.32,
                55,
                0.30,
                3.8,
                "2026-08-30",
                1.0,
                0.08,
                0.2,
                4,
                "Above 20, Below 50, Above 200",
            ],
            [
                "TSLA",
                250.40,
                90000000,
                15000,
                2500,
                6.0,
                0.65,
                80,
                0.55,
                12.0,
                "2026-08-15",
                2.5,
                -0.05,
                0.8,
                3,
                "Below 20, 50, 200 (Bearish)",
            ],
            [
                "NVDA",
                850.30,
                45000000,
                8500,
                1800,
                3.0,
                0.45,
                70,
                0.38,
                15.0,
                "2026-08-20",
                1.5,
                0.55,
                0.1,
                5,
                "Above 20, 50, 200 (Bullish)",
            ],
        ],
        columns=csv_columns,
    )
    sample_df["Next Earnings Date"] = pd.to_datetime(sample_df["Next Earnings Date"])
    sample_df["Date"] = pd.Timestamp.today()
    return sample_df


@st.cache_data
def get_daily_metrics() -> pd.DataFrame:
    """Load and process daily metrics from the data pipeline."""
    df = load_local_csv()
    if df.empty:
        df = _get_sample_data()
    df_scored = compute_option_score(df)
    df_bands = compute_bands(df_scored)
    return df_bands


@st.cache_data
def get_option_scores() -> pd.DataFrame:
    """Get option scores from the daily metrics."""
    df = get_daily_metrics()
    if df.empty:
        return pd.DataFrame()
    return df[["Ticker", "Date", "Option Score"]].copy()


@st.cache_data
def get_trades() -> pd.DataFrame:
    """Return empty trades dataframe (no live data source)."""
    return pd.DataFrame()


# Custom CSS for smaller title and reduced top gap
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    h1 {
        font-size: 1.75rem;
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="Option Trading System", layout="wide")

st.markdown("# StrideAlytics Alpha Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Screener", "Bands & Scores", "Volatility", "Trades"])

with tab1:
    st.subheader("Screener (Daily Metrics)")
    df = get_daily_metrics()
    if not df.empty:
        display_cols = [
            "Ticker",
            "Price",
            "Option Score",
            "Band",
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
            "Trend (Above/Below 20/50/200 EMA)",
        ]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], width="stretch")
    else:
        st.info("No daily metrics found.")

with tab2:
    st.subheader("Bands & Option Scores")
    scores = get_option_scores()
    if not scores.empty:
        score_cols = ["Ticker", "Date", "Option Score", "Band", "Strategy Tag"]
        available = [c for c in score_cols if c in scores.columns]
        st.dataframe(scores[available], width="stretch")
    else:
        st.info("No option scores found.")

with tab3:
    st.subheader("Volatility (IV vs HV)")
    if not df.empty:
        vol_cols = [
            "Ticker",
            "Date",
            "IV 30d",
            "IV Rank (1y)",
            "HV 30d",
            "ATR",
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
