import pandas as pd

# Each scoring rule and the input columns it needs.
_QUALITY_COLUMNS = ("Quality Score (1-5)", "Quality Score (1–5)")  # hyphen and en-dash variants


def _number(value):
    """A float, or None when the value is missing (None / NaN / NaT / text that is not a number)."""
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else float(number)


def _quality(row):
    for column in _QUALITY_COLUMNS:
        if column in row.index:
            return _number(row[column])
    return None


def _earnings(row):
    value = pd.to_datetime(row.get("Next Earnings Date"), errors="coerce")
    return None if pd.isna(value) else value


def compute_option_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a composite option score (0–9) for each ticker based on
    volume, OI, spread, IV, ATR, earnings, short interest, and quality.

    A rule whose input is missing (None, NaN, NaT, or not a number) earns no point, and the
    missing input is named in the ``Data Gaps`` column, so an incomplete row is visible instead
    of looking like a genuinely weak one. Bad data never raises.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with required columns.

    Returns
    -------
    pd.DataFrame
        Sorted by Option Score descending, with ``Data Gaps`` (comma-separated names, "" if none).
    """
    if df.empty:
        return df

    today = pd.Timestamp.today()

    def score_row(row):
        score = 0
        gaps = []

        def rule(name, value, passes):
            nonlocal score
            if value is None:
                gaps.append(name)
            elif passes(value):
                score += 1

        rule("Option Volume", _number(row.get("Option Volume")), lambda v: v > 2000)
        rule("Max OI (Near Exp)", _number(row.get("Max OI (Near Exp)")), lambda v: v > 500)
        rule("Bid-Ask Spread %", _number(row.get("Bid-Ask Spread %")), lambda v: v < 8)
        rule("IV 30d", _number(row.get("IV 30d")), lambda v: v > 0.25)
        rule("IV Rank (1y)", _number(row.get("IV Rank (1y)")), lambda v: v >= 40)

        atr, price = _number(row.get("ATR")), _number(row.get("Price"))
        if atr is None or price is None or price <= 0:
            gaps.append("ATR/Price")
        elif atr / price < 0.04:
            score += 1

        rule("Next Earnings Date", _earnings(row), lambda v: v > today + pd.Timedelta(days=14))
        rule("Short Interest %", _number(row.get("Short Interest %")), lambda v: v < 15)
        rule("Quality Score", _quality(row), lambda v: v >= 3)
        return pd.Series({"Option Score": score, "Data Gaps": ", ".join(gaps)})

    df = df.copy()
    result = df.apply(score_row, axis=1)
    df["Option Score"] = result["Option Score"].astype(int)
    df["Data Gaps"] = result["Data Gaps"]
    return df.sort_values("Option Score", ascending=False)
