import pandas as pd


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