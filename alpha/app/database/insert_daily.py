import math
from datetime import date, datetime

import pandas as pd

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
    "Quality Score (1-5)": "quality_score",
    "Trend (Above/Below 20/50/200 EMA)": "trend",
    "Trend": "trend",
    "Band": "band",
    "Sector": "sector",
    "Market Cap": "market_cap",
    "Strategy Tag": "strategy",
}

# Tables written by the daily pipeline. Every one has a TEXT ``date`` column
# holding ``YYYY-MM-DD``.
DAILY_TABLES = ("daily_metrics", "option_scores", "bands", "weekly_watchlist")


def today_str() -> str:
    """Today's date as ``YYYY-MM-DD`` (the format stored in every ``date`` column)."""
    return pd.Timestamp.today().strftime("%Y-%m-%d")


def _convert_timestamps(obj):
    """Recursively convert Timestamps, NaN/NaT and other values to JSON-compliant types."""
    if isinstance(obj, dict):
        return {k: _convert_timestamps(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_timestamps(item) for item in obj]
    # NaN / NaT / None -> null. (pd.NaT is a datetime subclass, so check this first,
    # otherwise it would be stored as the string "NaT".)
    if obj is None or (not isinstance(obj, (str, bytes)) and pd.isna(obj)):
        return None
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, float) and math.isinf(obj):
        return None
    return obj


def clear_all_tables() -> None:
    """
    Clear all data from the daily_metrics, option_scores, bands, and weekly_watchlist tables.
    Use this to reset corrupted data in Supabase.
    """
    client = get_supabase_client()
    try:
        client.table("daily_metrics").delete().neq("ticker", "").execute()
        client.table("option_scores").delete().neq("ticker", "").execute()
        client.table("bands").delete().neq("ticker", "").execute()
        client.table("weekly_watchlist").delete().neq("ticker", "").execute()
        print("[INFO] All tables cleared successfully")
    except Exception as e:
        print(f"[WARNING] Could not clear tables: {e}")


def _map_columns(df: pd.DataFrame, day: str | None = None) -> pd.DataFrame:
    """Map CSV column names to snake_case for Supabase and normalise ``date``.

    ``date`` is always ``YYYY-MM-DD``. If ``day`` is given it overrides any
    existing value so every table is written (and later deleted) under the
    same key.
    """
    result = df.copy()
    for csv_col, db_col in CSV_TO_DB_COLUMNS.items():
        if csv_col in result.columns:
            result = result.rename(columns={csv_col: db_col})

    if day is not None:
        result["date"] = day
    elif "date" in result.columns:
        result["date"] = result["date"].astype(str).str[:10]
    elif "Date" in df.columns:
        result["date"] = df["Date"].astype(str).str[:10]
    else:
        result["date"] = today_str()
    return result


# Columns that exist in the daily_metrics Supabase table (in correct order to match CSV)
DAILY_METRICS_COLUMNS = [
    "date",
    "ticker",
    "price",
    "avg_volume_shares",
    "option_volume",
    "max_oi_near_exp",
    "bid_ask_spread_pct",
    "iv_30d",
    "iv_rank_1y",
    "hv_30d",
    "atr",
    "next_earnings_date",
    "short_interest_pct",
    "revenue_growth_yoy",
    "debt_equity",
    "quality_score",
    "sector",
    "market_cap",
    "float_shares",
    "beta",
    "option_score",
    "band",
    "trend",
    "strategy",
]

OPTION_SCORE_COLUMNS = ["date", "ticker", "option_score", "trend", "strategy"]

WATCHLIST_COLUMNS = [
    "date",
    "ticker",
    "sector",
    "price",
    "option_score",
    "iv_rank_1y",
    "iv_30d",
    "next_earnings_date",
    "trend",
    "strategy",
]


def _rows(df: pd.DataFrame, columns: list[str], day: str | None = None) -> list[dict]:
    """Build JSON-safe insert rows for the given columns (those that exist)."""
    if df.empty:
        return []
    mapped = _map_columns(df, day)
    available = [c for c in columns if c in mapped.columns]
    return _convert_timestamps(mapped[available].to_dict(orient="records"))


def _band_rows(df: pd.DataFrame, day: str | None = None) -> list[dict]:
    if df.empty or "Band" not in df.columns:
        return []
    return _rows(df, ["date", "ticker", "band"], day)


def replace_day(df_bands: pd.DataFrame, weekly: pd.DataFrame, day: str | None = None) -> dict:
    """Replace one day's rows in all four daily tables.

    All payloads are built *before* anything is deleted, so a mapping/serialisation
    problem can never leave the day empty. Deletes use ``date LIKE 'YYYY-MM-DD%'`` so
    legacy rows that were stored with a time component are cleaned up too. Any
    Supabase error is raised (never swallowed).

    The Supabase REST API has no multi-table transaction, so a network failure
    between the deletes and the inserts can still leave a partial day; the caller
    should treat an exception as "re-run needed" (``main`` alerts and exits non-zero).
    """
    day = day or today_str()
    payload = {
        "daily_metrics": _rows(df_bands, DAILY_METRICS_COLUMNS, day),
        "option_scores": _rows(df_bands, OPTION_SCORE_COLUMNS, day),
        "bands": _band_rows(df_bands, day),
        "weekly_watchlist": _rows(weekly, WATCHLIST_COLUMNS, day),
    }

    client = get_supabase_client()
    for table in DAILY_TABLES:
        client.table(table).delete().like("date", f"{day}%").execute()
    for table in DAILY_TABLES:
        rows = payload[table]
        if rows:
            client.table(table).insert(rows).execute()

    return {table: len(rows) for table, rows in payload.items()}


def insert_daily_metrics(df: pd.DataFrame) -> None:
    """Insert row-level daily metrics into Supabase."""
    rows = _rows(df, DAILY_METRICS_COLUMNS)
    if rows:
        get_supabase_client().table("daily_metrics").insert(rows).execute()


def insert_option_scores(df: pd.DataFrame) -> None:
    """Insert ticker-level option scores into Supabase."""
    rows = _rows(df, OPTION_SCORE_COLUMNS)
    if rows:
        get_supabase_client().table("option_scores").insert(rows).execute()


def insert_bands(df: pd.DataFrame) -> None:
    """Insert band classifications into Supabase (needs a 'Band' column)."""
    rows = _band_rows(df)
    if rows:
        get_supabase_client().table("bands").insert(rows).execute()


def insert_weekly_watchlist(df: pd.DataFrame) -> None:
    """Insert weekly watchlist into Supabase."""
    rows = _rows(df, WATCHLIST_COLUMNS)
    if rows:
        get_supabase_client().table("weekly_watchlist").insert(rows).execute()


def insert_trades(df: pd.DataFrame) -> None:
    """
    Insert trades into Supabase trades table.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with trades columns: date, ticker, strategy, entry_strikes,
        expiry, credit_debit, reason, exit_plan.
    """
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
    rows = _rows(df, trade_cols)
    if rows:
        get_supabase_client().table("trades").insert(rows).execute()
