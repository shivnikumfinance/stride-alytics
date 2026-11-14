"""The chain loader must reach beyond the first few (often same-week) expirations."""

from __future__ import annotations

from datetime import date, timedelta

from app.services.screener import MAX_EXPIRIES, select_expirations

TODAY = date(2026, 11, 14)


def _days(*offsets: int) -> list[str]:
    return [(TODAY + timedelta(days=d)).isoformat() for d in offsets]


def test_few_expirations_are_all_kept() -> None:
    exps = _days(2, 4, 6, 13, 20, 27, 34, 62, 97, 188)
    assert select_expirations(exps, TODAY, 60) == _days(2, 4, 6, 13, 20, 27, 34)
    assert select_expirations(exps, TODAY, 70) == _days(2, 4, 6, 13, 20, 27, 34, 62)  # exactly 8


def test_many_weeklies_are_spread_across_the_window() -> None:
    # Like AAPL: Monday/Wednesday/Friday weeklies, so the nearest eight cover only five weeks.
    exps = _days(*range(2, 91, 2))  # 45 expirations, every other day
    picked = select_expirations(exps, TODAY, 90)
    assert len(picked) == MAX_EXPIRIES and picked == sorted(picked)
    assert picked[0] == _days(2)[0]  # the nearest is kept
    assert picked[-1] == _days(90)[0]  # and the furthest in the window
    assert (
        max((date.fromisoformat(e) - TODAY).days for e in picked) > 80
    )  # not just the first weeks


def test_window_is_respected_and_capped() -> None:
    exps = _days(*range(1, 40))
    picked = select_expirations(exps, TODAY, 30)
    assert len(picked) == MAX_EXPIRIES and picked == sorted(picked)
    assert all((date.fromisoformat(e) - TODAY).days <= 30 for e in picked)
    assert (TODAY + timedelta(days=30)).isoformat() in picked


def test_unsorted_input_and_past_dates() -> None:
    exps = _days(20, -3, 5, 0)
    assert select_expirations(exps, TODAY, 60) == _days(0, 5, 20)  # today counts, the past does not


def test_falls_back_to_the_nearest_when_none_are_in_the_window() -> None:
    exps = _days(100, 200, 300, 400)
    assert select_expirations(exps, TODAY, 30) == _days(100, 200, 300)
    assert select_expirations([], TODAY, 30) == []


# ---------------------------------------------------------------- NaN-safe parsing


def test_num_handles_missing_values() -> None:
    import math

    from app.services.screener import _num

    assert _num(3) == 3.0 and _num("2.5") == 2.5
    assert _num(None) == 0.0 and _num(float("nan")) == 0.0 and _num(float("inf")) == 0.0
    assert _num("abc", default=7) == 7 and math.isfinite(_num(float("-inf")))


def test_a_nan_volume_does_not_drop_the_whole_expiry(monkeypatch) -> None:
    """Regression: int(NaN) raised, so one contract with no volume dropped its entire expiry."""
    import pandas as pd

    from app.services import screener

    nan = float("nan")
    frame = pd.DataFrame(
        {
            "strike": [100.0, 105.0, 110.0],
            "impliedVolatility": [0.3, 0.0, nan],  # the last two have no usable IV
            "bid": [1.0, nan, 0.5],
            "ask": [1.2, nan, 0.7],
            "lastPrice": [1.1, 0.0, nan],
            "openInterest": [nan, 10, 20],
            "volume": [nan, nan, 5],
        }
    )

    class FakeChain:
        calls = frame
        puts = frame

    class FakeTicker:
        options = ((date.today() + timedelta(days=30)).isoformat(),)

        def __init__(self, symbol: str) -> None:
            pass

        def option_chain(self, expiry: str):
            return FakeChain

    monkeypatch.setattr(screener.yf, "Ticker", FakeTicker)
    rows = screener._load_chain_from_yfinance("TEST", 100.0, 60)
    assert rows is not None and len(rows) == 2  # one valid call and one valid put
    assert {r["option_type"] for r in rows} == {"call", "put"}
    r = rows[0]
    assert r["open_interest"] == 0 and r["volume"] == 0 and r["bid"] == 1.0  # NaN became 0
    import json

    json.dumps(rows, allow_nan=False)  # no NaN leaks into the response
