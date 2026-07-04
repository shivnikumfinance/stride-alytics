import pandas as pd


def assign_band(row) -> str:
    """Assign a band (A–E) based on Option Score."""
    score = row["Option Score"]

    if score >= 8:
        return "A"
    if score >= 6:
        return "B"
    if score >= 4:
        return "C"
    if score >= 2:
        return "D"
    return "E"


def compute_bands(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute letter bands (A–E) for each ticker based on Option Score.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with an 'Option Score' column.

    Returns
    -------
    pd.DataFrame
        DataFrame with added 'Band' column.
    """
    if df.empty:
        return df

    df = df.copy()
    bands = df.apply(assign_band, axis=1)
    df["Band"] = bands
    return df
