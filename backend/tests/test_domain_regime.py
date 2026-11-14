"""Regime score: boundaries, sub-scores, missing data."""

from __future__ import annotations

import pytest

from app.domain import regime_score as rs

# Captured at import time, before the autouse fixture in conftest replaces it with a fake.
REAL_FETCH_INPUTS = rs.fetch_inputs


@pytest.mark.parametrize(
    "score,state",
    [
        (0, "DEFENSIVE"),
        (39.9, "DEFENSIVE"),
        (40, "NORMAL"),  # lower bound is inclusive
        (40.1, "NORMAL"),
        (69.9, "NORMAL"),
        (70, "GROWTH"),
        (70.1, "GROWTH"),
        (100, "GROWTH"),
        (None, "UNKNOWN"),
    ],
)
def test_classify_boundaries(score, state) -> None:
    assert rs.classify(score) == state


# ----------------------------------------------------------------- trend


def _rising(n=250):
    return [100 + i * 0.5 for i in range(n)]


def _falling(n=250):
    return [200 - i * 0.5 for i in range(n)]


def test_trend_score_extremes() -> None:
    assert rs.trend_score(_rising()) == (100.0, False)
    assert rs.trend_score(_falling()) == (0.0, True)


def test_trend_score_needs_200_days() -> None:
    assert rs.trend_score(_rising(199)) == (None, None)
    assert rs.trend_score(None) == (None, None)
    assert rs.trend_score([]) == (None, None)


def test_trend_score_between_the_averages() -> None:
    # Price recovered above its 50-day average but is still under the 200-day average.
    closes = [100.0] * 150 + [80.0] * 49 + [95.0]
    points, market_down = rs.trend_score(closes)
    assert points == 30.0 and market_down is True


# ------------------------------------------------------------------- vix


@pytest.mark.parametrize(
    "vix,expected",
    [(None, None), (5, 100.0), (12, 100.0), (26, 50.0), (40, 0.0), (80, 0.0)],
)
def test_vix_score(vix, expected) -> None:
    assert rs.vix_score(vix) == expected


def test_iv_rank_is_a_percentile_and_needs_history() -> None:
    history = list(range(1, 101))  # 100 values, last = 100 (the highest)
    assert rs.iv_rank_from_history(history) == 100.0
    assert (
        rs.iv_rank_from_history([100] + list(range(2, 100)) + [1]) == 1.0
    )  # 100 values, current is the lowest
    assert rs.iv_rank_from_history(history[:50]) is None
    assert rs.iv_rank_from_history(None) is None


# --------------------------------------------------------------- combine


def test_combine_renormalises_over_available_inputs() -> None:
    score, missing = rs.combine({"trend": 100, "vix": None, "iv_rank": 0}, rs.DEFAULT_WEIGHTS)
    assert score == pytest.approx(57.1, abs=0.05)  # (100*40 + 0*30) / 70
    assert missing == ["vix"]


def test_combine_with_nothing_or_zero_weights_is_none() -> None:
    assert rs.combine({"trend": None, "vix": None, "iv_rank": None}, rs.DEFAULT_WEIGHTS)[0] is None
    zero = {"trend": 0, "vix": 0, "iv_rank": 0}
    assert rs.combine({"trend": 50, "vix": 50, "iv_rank": 50}, zero)[0] is None


# ---------------------------------------------------------- compute_regime


def test_calm_uptrend_is_growth() -> None:
    r = rs.compute_regime(_rising(), [15.0] * 250)
    assert r.state == "GROWTH" and r.score is not None and r.score > 90
    assert r.market_down is False and r.source == "live" and r.missing == []
    assert r.vix == 15.0 and r.iv_rank == 100.0


def test_selloff_is_defensive_and_flags_a_down_market() -> None:
    vix = [20.0] * 200 + [20 + i for i in range(50)]  # VIX spiking to its high
    r = rs.compute_regime(_falling(), vix)
    assert r.state == "DEFENSIVE" and r.market_down is True
    assert r.components["trend"] == 0 and r.components["vix"] == 0


def test_custom_weights_change_the_score() -> None:
    trend_only = rs.compute_regime(
        _rising(), [30.0] * 250, weights={"trend": 100, "vix": 0, "iv_rank": 0}
    )
    assert trend_only.score == 100.0
    vix_only = rs.compute_regime(
        _rising(), [30.0] * 250, weights={"trend": 0, "vix": 100, "iv_rank": 0}
    )
    assert vix_only.score == pytest.approx(35.7, abs=0.05)  # 100*(40-30)/28


def test_no_data_means_unknown_not_a_guess() -> None:
    r = rs.compute_regime(None, None)
    assert r.score is None and r.state == "UNKNOWN" and r.source == "unavailable"
    assert set(r.missing) == {"trend", "vix", "iv_rank"}


def test_partial_data_still_scores_from_what_exists() -> None:
    r = rs.compute_regime(_rising(), None)
    assert r.score == 100.0 and set(r.missing) == {"vix", "iv_rank"}


def test_all_zero_weights_is_unknown() -> None:
    r = rs.compute_regime(_rising(), [15.0] * 250, weights={"trend": 0, "vix": 0, "iv_rank": 0})
    assert r.state == "UNKNOWN"


def test_fetch_inputs_swallows_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys
    import types

    class Boom:
        def __init__(self, *a, **k):
            raise RuntimeError("network down")

    fake = types.ModuleType("yfinance")
    fake.Ticker = Boom  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "yfinance", fake)
    monkeypatch.setattr(rs, "fetch_inputs", REAL_FETCH_INPUTS)
    assert rs.fetch_inputs() == (None, None)


def test_row_payload_for_the_scheduler_matches_the_table_columns() -> None:
    r = rs.compute_regime(_rising(), [15.0] * 250, as_of=__import__("datetime").date(2026, 6, 1))
    row = r.to_row()
    assert set(row) == {
        "as_of",
        "score",
        "state",
        "components",
        "weights",
        "vix",
        "iv_rank",
        "market_down",
        "source",
    }
    assert row["as_of"] == "2026-06-01" and row["state"] == "GROWTH" and row["source"] == "live"
    assert row["weights"] == {
        "trend": 40.0,
        "vix": 30.0,
        "iv_rank": 30.0,
    }  # default weights are stored
