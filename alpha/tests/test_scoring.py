"""Option scoring: the 0-9 score, and how missing inputs are handled."""

from __future__ import annotations

import pandas as pd

from app.screener.compute_option_score import compute_option_score

FAR = pd.Timestamp.today() + pd.Timedelta(days=60)


def _row(**over) -> dict:
    """A row that earns all nine points."""
    row = {
        "Ticker": "AAA",
        "Price": 100.0,
        "Option Volume": 5000,
        "Max OI (Near Exp)": 1000,
        "Bid-Ask Spread %": 3.0,
        "IV 30d": 0.4,
        "IV Rank (1y)": 60,
        "ATR": 2.0,
        "Next Earnings Date": FAR,
        "Short Interest %": 5.0,
        "Quality Score (1-5)": 4,
    }
    row.update(over)
    return row


def _score(*rows: dict) -> pd.DataFrame:
    return compute_option_score(pd.DataFrame(list(rows)))


def test_a_complete_strong_row_scores_nine_with_no_gaps() -> None:
    out = _score(_row())
    assert out.iloc[0]["Option Score"] == 9 and out.iloc[0]["Data Gaps"] == ""


def test_each_rule_is_worth_one_point_at_its_boundary() -> None:
    cases = {
        "Option Volume": (2000, 2001),  # needs > 2000
        "Max OI (Near Exp)": (500, 501),  # needs > 500
        "Bid-Ask Spread %": (8, 7.99),  # needs < 8
        "IV 30d": (0.25, 0.2501),  # needs > 0.25
        "IV Rank (1y)": (39.9, 40),  # needs >= 40
        "Short Interest %": (15, 14.9),  # needs < 15
        "Quality Score (1-5)": (2, 3),  # needs >= 3
    }
    for column, (fails, passes) in cases.items():
        assert _score(_row(**{column: fails})).iloc[0]["Option Score"] == 8, column
        assert _score(_row(**{column: passes})).iloc[0]["Option Score"] == 9, column


def test_atr_and_earnings_rules() -> None:
    assert _score(_row(ATR=4.0)).iloc[0]["Option Score"] == 8  # 4% of price is not below 4%
    assert _score(_row(ATR=3.99)).iloc[0]["Option Score"] == 9
    soon = pd.Timestamp.today() + pd.Timedelta(days=10)
    assert _score(_row(**{"Next Earnings Date": soon})).iloc[0]["Option Score"] == 8


def test_missing_inputs_score_nothing_and_are_named() -> None:
    nan = float("nan")
    out = _score(_row(**{"Option Volume": nan, "IV 30d": None, "Short Interest %": "n/a"}))
    assert out.iloc[0]["Option Score"] == 6  # three rules lost their point
    assert out.iloc[0]["Data Gaps"] == "Option Volume, IV 30d, Short Interest %"


def test_a_missing_value_is_not_confused_with_a_genuinely_weak_one() -> None:
    weak = _score(_row(**{"Option Volume": 10})).iloc[0]
    missing = _score(_row(**{"Option Volume": float("nan")})).iloc[0]
    assert weak["Option Score"] == missing["Option Score"] == 8
    assert weak["Data Gaps"] == "" and missing["Data Gaps"] == "Option Volume"


def test_missing_or_bad_price_and_atr_are_gaps_not_crashes() -> None:
    for over in ({"Price": 0}, {"Price": float("nan")}, {"ATR": None}, {"ATR": "x"}):
        out = _score(_row(**over)).iloc[0]
        assert out["Option Score"] == 8 and out["Data Gaps"] == "ATR/Price", over


def test_missing_or_unparseable_earnings_date_is_a_gap() -> None:
    for value in (pd.NaT, None, "not a date"):
        out = _score(_row(**{"Next Earnings Date": value})).iloc[0]
        assert out["Option Score"] == 8 and out["Data Gaps"] == "Next Earnings Date", value
    # A date given as text still works.
    assert (
        _score(_row(**{"Next Earnings Date": FAR.strftime("%Y-%m-%d")})).iloc[0]["Option Score"]
        == 9
    )


def test_quality_column_hyphen_and_en_dash_variants() -> None:
    en_dash = _row()
    en_dash["Quality Score (1–5)"] = en_dash.pop("Quality Score (1-5)")
    assert _score(en_dash).iloc[0]["Option Score"] == 9
    none = _row()
    none.pop("Quality Score (1-5)")
    out = _score(none).iloc[0]
    assert out["Option Score"] == 8 and out["Data Gaps"] == "Quality Score"


def test_sorted_best_first_and_empty_input_is_returned_as_is() -> None:
    out = _score(_row(Ticker="LOW", **{"Option Volume": 1}), _row(Ticker="HIGH"))
    assert list(out["Ticker"]) == ["HIGH", "LOW"]
    empty = pd.DataFrame()
    assert compute_option_score(empty) is empty


def test_input_is_not_modified() -> None:
    df = pd.DataFrame([_row()])
    before = df.copy()
    compute_option_score(df)
    pd.testing.assert_frame_equal(df, before)
