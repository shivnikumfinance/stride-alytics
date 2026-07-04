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
        "Quality Score (1\u20135)",
    ]

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    return df