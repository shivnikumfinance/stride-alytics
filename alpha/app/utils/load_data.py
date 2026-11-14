import pandas as pd
import warnings


def load_from_supabase() -> pd.DataFrame:
    """
    Load today's screener data from Supabase daily_metrics table.
    
    This should be the primary data source - used when data has already been
    ingested into Supabase. Falls back gracefully if no data or connection error.
    
    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with proper types matching CSV format.
    """
    try:
        from app.database.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        today_str = pd.Timestamp.today().strftime("%Y-%m-%d")
        
        # Try to fetch today's data from Supabase
        resp = client.table("daily_metrics").select("*").eq("date", today_str).execute()
        data = resp.data or []
        
        if not data:
            # No data found for today - this is expected on first run
            # Return empty df to trigger CSV fallback
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Rename snake_case columns to CSV format for compatibility
        rename_map = {
            "ticker": "Ticker",
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
            "sector": "Sector",
            "trend": "Trend (Above/Below 20/50/200 EMA)",
            "option_score": "Option Score",
            "band": "Band",
            "strategy": "Strategy Tag",
        }
        
        # Rename columns that exist
        for old_col, new_col in rename_map.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Convert Next Earnings Date to datetime
        if "Next Earnings Date" in df.columns:
            df["Next Earnings Date"] = pd.to_datetime(df["Next Earnings Date"], errors="coerce")
        
        return df
        
    except Exception as e:
        # Connection error or other issue - return empty to trigger CSV fallback
        print(f"[INFO] Could not load from Supabase (will try CSV): {e}")
        return pd.DataFrame()


def load_local_csv(path: str = "raw_screener.csv") -> pd.DataFrame:
    """
    Load raw screener data from a local CSV file.

    Parameters
    ----------
    path : str
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with proper types.
    """
    import os

    # Try multiple locations for the CSV file on Streamlit Cloud
    possible_paths = [
        path,
        os.path.join(os.path.dirname(__file__), "..", "..", "..", path),
        "/mount/src/stride-alytics/alpha/raw_screener.csv",
    ]

    df = None
    for csv_path in possible_paths:
        try:
            if os.path.exists(csv_path):
                # quotechar='"' is pandas default, but be explicit to guard
                # against malformed CSVs that contain unquoted commas inside
                # fields (e.g. "Above 20, 50, 200 (Bullish)").
                df = pd.read_csv(csv_path, quotechar='"', skipinitialspace=True)
                # Remember where it came from so callers can warn about stale files.
                df.attrs["source_path"] = csv_path
                break
        except FileNotFoundError:
            continue

    if df is None:
        # Return empty dataframe if file not exist
        return pd.DataFrame()

    # Defensive: if the Ticker column came in as numeric, the CSV is almost
    # certainly misparsed (unquoted commas split rows into too many fields
    # and shifted column values left). Surface this clearly instead of
    # silently inserting garbage into Supabase.
    if "Ticker" in df.columns and not pd.api.types.is_string_dtype(df["Ticker"]):
        print(
            "[WARNING] CSV 'Ticker' column is not string — the file likely has "
            "unquoted commas in some field (commonly the Trend column). "
            "Rejecting malformed data."
        )
        return pd.DataFrame()

    # Try both en-dash and hyphen variants for Quality Score
    for col in df.columns:
        if "Quality Score" in col:
            df = df.rename(columns={col: "Quality Score (1-5)"})
            break

    if "Next Earnings Date" in df.columns:
        df["Next Earnings Date"] = pd.to_datetime(df["Next Earnings Date"], errors="coerce")

    numeric_cols = [
        "Price",
        "Avg Volume (Shares)",
        "Option Volume",
        "Max OI (Near Exp)",
        "Bid-Ask Spread %",
        "IV 30d",
        "IV Rank (1y)",
        "HV 30d",
        "ATR",
        "Short Interest %",
        "Revenue Growth (YoY)",
        "Debt/Equity",
        "Quality Score (1-5)",
        "Market Cap",
    ]

    # Only convert columns that exist
    cols_to_convert = [c for c in numeric_cols if c in df.columns]
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors="coerce")

    return df