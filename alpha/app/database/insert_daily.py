import pandas as pd
from datetime import date, datetime

from .supabase_client import get_supabase_client

# Column mapping from CSV format to snake_case for Supabase
CSV_TO_DB_COLUMNS = {
    "Ticker": "ticker",
    "Price": "price",
    "Avg Volume (Shares)": "avg_volume_shares",
    "Option Volume": "option_volume",
    "Max OI (Near Exp)": "max_oi_near_exp",
    "Bid-Ask Spread %": "bid_ask_spread_pct",
    "IV 30d": "iv_30d",
    "IV Rank (1y)": "iv_rank_1y",
    "HV 30d": "hv_30d",
    "ATR": "atr",
    "Next Earnings Date": "next_earnings_date",
    "Short Interest %": "short_interest_pct",
    "Revenue Growth (YoY)": "revenue_growth_yoy",
    "Debt/Equity": "debt_equity",
    "Quality Score (1–5)": "quality_score",
    "Trend (Above/Below 20/50/200 EMA)": "trend",
    "Band": "band",
    "Sector": "sector",
    "Market Cap": "market_cap",
}


def _convert_timestamps(obj):
    """Recursively convert Timestamp/Datetime objects to ISO format strings."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _convert_timestamps(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_timestamps(item) for item in obj]
    return obj


def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map CSV column names to snake_case for Supabase."""
    result = df.copy()
    for csv_col, db_col in CSV_TO_DB_COLUMNS.items():
        if csv_col in result.columns:
            result = result.rename(columns={csv_col: db_col})
    # Add date column if missing
    if "date" not in result.columns and "Date" in df.columns:
        result["date"] = df["Date"]
    elif "date" not in result.columns:
        result["date"] = pd.Timestamp.today().isoformat()
    return result


def insert_daily_metrics(df: pd.DataFrame) -> None:
    """
    Insert row-level daily metrics into Supabase.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing daily metrics (all columns).
    """
    if df.empty:
        return
    client = get_supabase_client()
    df_mapped = _map_columns(df)
    rows = df_mapped.to_dict(orient="records")
    rows = _convert_timestamps(rows)
    client.table("daily_metrics").insert(rows).execute()


def insert_option_scores(df: pd.DataFrame) -> None:
    """
    Insert ticker-level option scores into Supabase.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least 'Ticker' and 'Option Score' columns.
    """
    if df.empty:
        return
    client = get_supabase_client()
    df_mapped = _map_columns(df)
    # Select the columns needed for option_scores
    score_cols = ["date", "ticker", "option_score", "trend", "strategy"]
    available_cols = [c for c in score_cols if c in df_mapped.columns]
    rows = df_mapped[available_cols].to_dict(orient="records")
    rows = _convert_timestamps(rows)
    client.table("option_scores").insert(rows).execute()


def insert_bands(df: pd.DataFrame) -> None:
    """
    Insert band classifications into Supabase.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'Ticker' and 'Band' columns.
    """
    if df.empty:
        return
    if "Band" not in df.columns:
        return
    client = get_supabase_client()
    df_mapped = _map_columns(df)
    rows = df_mapped[["date", "ticker", "band"]].to_dict(orient="records")
    rows = _convert_timestamps(rows)
    client.table("bands").insert(rows).execute()


def insert_weekly_watchlist(df: pd.DataFrame) -> None:
    """
    Insert weekly watchlist into Supabase.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with weekly watchlist columns.
    """
    if df.empty:
        return
    client = get_supabase_client()
    df_mapped = _map_columns(df)
    watch_cols = [
        "date",
        "ticker",
        "price",
        "option_score",
        "trend",
        "strategy",
        "iv_rank_1y",
        "next_earnings_date",
    ]
    available_cols = [c for c in watch_cols if c in df_mapped.columns]
    rows = df_mapped[available_cols].to_dict(orient="records")
    rows = _convert_timestamps(rows)
    client.table("weekly_watchlist").insert(rows).execute()


def insert_trades(df: pd.DataFrame) -> None:
    """
    Insert trades into Supabase trades table.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with trades columns: date, ticker, strategy, entry_strikes,
        expiry, credit_debit, reason, exit_plan.
    """
    if df.empty:
        return
    client = get_supabase_client()
    df_mapped = _map_columns(df)
    trade_cols = [
        "date",
        "ticker",
        "strategy",
        "entry_strikes",
        "expiry",
        "credit_debit",
        "reason",
        "exit_plan",
    ]
    available_cols = [c for c in trade_cols if c in df_mapped.columns]
    rows = df_mapped[available_cols].to_dict(orient="records")
    rows = _convert_timestamps(rows)
    client.table("trades").insert(rows).execute()
