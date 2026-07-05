import pandas as pd


def _compute_strategy_tag(row) -> str:
    """Compute strategy tag for a single row based on IV rank and trend."""
    iv_rank = row.get("IV Rank (1y)", 0)
    trend = str(row.get("Trend (Above/Below 20/50/200 EMA)", "")).lower()

    if iv_rank >= 50:
        if "bull" in trend:
            return "Short Put / Bull Put Spread"
        if "bear" in trend:
            return "Bear Call Spread / Iron Condor"
        return "Iron Condor / Short Strangle"

    if iv_rank <= 30:
        if "bull" in trend:
            return "Bull Call Debit Spread / Call Calendar"
        if "bear" in trend:
            return "Bear Put Debit Spread / Put Calendar"
        return "Straddle / Strangle / Calendar"

    if "range" in trend:
        return "Iron Condor / Butterfly"

    return "Directional Spread"


def compute_strategy_for_all(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute strategy tags for all tickers in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with IV Rank (1y), Trend (Above/Below 20/50/200 EMA), etc.

    Returns
    -------
    pd.DataFrame
        DataFrame with added 'Strategy Tag' column.
    """
    if df.empty:
        return df

    df = df.copy()
    df["Strategy Tag"] = df.apply(_compute_strategy_tag, axis=1)
    return df


def weekly_watchlist(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a weekly watchlist from scored data, applying strategy tags
    based on IV rank and trend.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Option Score, IV Rank (1y), Trend, etc.

    Returns
    -------
    pd.DataFrame
        Weekly watchlist with Strategy Tag and Sector columns.
    """
    if df.empty:
        return df

    today = pd.Timestamp.today()

    weekly = df[
        (df["Option Score"] >= 6) & (df["Next Earnings Date"] > today + pd.Timedelta(days=14))
    ].copy()

    if weekly.empty:
        return weekly

    weekly["Strategy Tag"] = weekly.apply(_compute_strategy_tag, axis=1)

    # Add Date column if missing (use today's date)
    if "Date" not in weekly.columns and "date" not in weekly.columns:
        weekly["Date"] = today

    return weekly[
        [
            "Ticker",
            "Date",
            "Sector",
            "Price",
            "Option Score",
            "IV Rank (1y)",
            "IV 30d",
            "Next Earnings Date",
            "Trend (Above/Below 20/50/200 EMA)",
            "Strategy Tag",
        ]
    ].rename(columns={"Trend (Above/Below 20/50/200 EMA)": "Trend"})