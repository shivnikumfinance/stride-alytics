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
    df = pd.read_csv(path)

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
