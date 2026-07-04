import pandas as pd

from .supabase_client import supabase


def insert_daily_metrics(df: pd.DataFrame) -> None:
    """
    Insert row-level daily metrics into Supabase.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing daily metrics (all columns).
    """
    rows = df.to_dict(orient="records")
    supabase.table("daily_metrics").insert(rows).execute()


def insert_option_scores(df: pd.DataFrame) -> None:
    """
    Insert ticker-level option scores into Supabase.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least 'Ticker' and 'Option Score' columns.
    """
    rows = df[["Ticker", "Option Score"]].to_dict(orient="records")
    supabase.table("option_scores").insert(rows).execute()