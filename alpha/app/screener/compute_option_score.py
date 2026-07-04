import pandas as pd


def compute_option_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a composite option score (0–9) for each ticker based on
    volume, OI, spread, IV, ATR, earnings, short interest, and quality.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with required columns.

    Returns
    -------
    pd.DataFrame
        Sorted by Option Score descending.
    """
    today = pd.Timestamp.today()

    def score_row(row):
        score = 0
        if row["Option Volume"] > 2000:
            score += 1
        if row["Max OI (Near Exp)"] > 500:
            score += 1
        if row["Bid-Ask Spread %"] < 8:
            score += 1
        if row["IV 30d"] > 0.25:
            score += 1
        if row["IV Rank (1y)"] >= 40:
            score += 1
        if (row["ATR"] / row["Price"]) < 0.04:
            score += 1
        if row["Next Earnings Date"] > today + pd.Timedelta(days=14):
            score += 1
        if row["Short Interest %"] < 15:
            score += 1
        if row["Quality Score (1\u20135)"] >= 3:
            score += 1
        return score

    df = df.copy()
    df["Option Score"] = df.apply(score_row, axis=1)
    return df.sort_values("Option Score", ascending=False)