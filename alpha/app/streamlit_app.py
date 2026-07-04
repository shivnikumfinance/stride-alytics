"""
Streamlit dashboard for the Option Trading System.

Displays daily metrics, option scores, volatility data, and trades
pulled from Supabase.
"""

import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@st.cache_data
def get_daily_metrics() -> pd.DataFrame:
    res = supabase.table("daily_metrics").select("*").execute()
    return pd.DataFrame(res.data)


@st.cache_data
def get_option_scores() -> pd.DataFrame:
    res = supabase.table("option_scores").select("*").execute()
    return pd.DataFrame(res.data)


@st.cache_data
def get_trades() -> pd.DataFrame:
    res = supabase.table("trades").select("*").execute()
    return pd.DataFrame(res.data)


st.set_page_config(page_title="Option Trading System", layout="wide")

st.title("\U0001f4c8 Option Trading System Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Screener", "Bands & Scores", "Volatility", "Trades"]
)

with tab1:
    st.subheader("Screener (Daily Metrics)")
    df = get_daily_metrics()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No daily metrics found.")

with tab2:
    st.subheader("Bands & Option Scores")
    scores = get_option_scores()
    if not scores.empty:
        st.dataframe(scores, use_container_width=True)
        st.line_chart(scores.groupby("Date")["Option Score"].mean())
    else:
        st.info("No option scores found.")

with tab3:
    st.subheader("Volatility (IV vs HV)")
    if not df.empty:
        if "IV_30d" in df.columns and "HV_30d" in df.columns:
            vol_df = df[["Ticker", "Date", "IV_30d", "HV_30d"]]
            st.dataframe(vol_df, use_container_width=True)
            st.line_chart(vol_df.set_index("Date")[["IV_30d", "HV_30d"]])
        else:
            st.warning("IV_30d / HV_30d columns missing in daily_metrics.")
    else:
        st.info("No daily metrics found.")

with tab4:
    st.subheader("Trades & P&L")
    trades = get_trades()
    if not trades.empty:
        st.dataframe(trades, use_container_width=True)
        if "Pnl" in trades.columns:
            st.bar_chart(trades.set_index("Date")["Pnl"])
    else:
        st.info("No trades found.")