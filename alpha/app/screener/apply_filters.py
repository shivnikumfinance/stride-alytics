import pandas as pd


def apply_daily_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply daily entry filters and add volatility columns (Bias, IV vs HV).

    Parameters
    ----------
    df : pd.DataFrame
        Scored DataFrame.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame with Volatility Bias and IV vs HV columns.
    """
    if df.empty:
        return df

    today = pd.Timestamp.today()

    filtered = df[
        (df["Option Volume"] >= 2000)
        & (df["Max OI (Near Exp)"] >= 500)
        & (df["Bid-Ask Spread %"] <= 8)
        & (df["Next Earnings Date"] > today + pd.Timedelta(days=14))
        & (df["Short Interest %"] < 15)
    ].copy()

    if filtered.empty:
        return filtered

    def vol_bias(row):
        if row["IV Rank (1y)"] >= 50:
            return "Sell Premium"
        if row["IV Rank (1y)"] <= 30:
            return "Buy Premium"
        return "Neutral"

    def iv_vs_hv(row):
        if row["IV 30d"] > row["HV 30d"]:
            return "IV > HV (Selling better)"
        if row["IV 30d"] < row["HV 30d"]:
            return "IV < HV (Buying better)"
        return "IV ≈ HV"

    filtered["Volatility Bias"] = filtered.apply(vol_bias, axis=1)
    filtered["IV vs HV"] = filtered.apply(iv_vs_hv, axis=1)

    return filtered
