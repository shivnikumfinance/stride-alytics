"""Phase 4 pure logic: portfolio risk, expected value, strategy matrix, scenario repricing."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.domain import ev
from app.domain.alerts import MarketInput, PositionInput
from app.domain.portfolio_risk import (
    MAX_CAPITAL_AT_RISK_PCT,
    PositionRisk,
    calculate_portfolio_risk,
    entry_risk_reason,
)
from app.domain.strategy_matrix import REGIMES, build_matrix, strategy_names
from app.services.scenarios import Shock, reprice_position, run_scenario, spot_ladder

TODAY = date(2026, 6, 1)

# ----------------------------------------------------------- portfolio risk


def test_empty_portfolio_has_no_risk() -> None:
    r = calculate_portfolio_risk([], 100_000)
    assert r.capital_at_risk == 0 and r.margin_pct == 0 and r.net_delta == 0
    assert r.breaches == [] and r.sectors == [] and r.unpriced_positions == 0


def test_margin_net_delta_and_sectors() -> None:
    r = calculate_portfolio_risk(
        [
            PositionRisk("AAPL", 5000, "Technology", position_delta=40, spot=200),
            PositionRisk("MSFT", 3000, "Technology", position_delta=-10, spot=400),
            PositionRisk("XOM", 2000, "Energy", position_delta=20, spot=100),
        ],
        100_000,
    )
    assert r.capital_at_risk == 10_000 and r.margin_pct == 10.0
    assert r.net_delta == 50
    assert r.net_delta_dollars == 40 * 200 - 10 * 400 + 20 * 100  # 6000
    assert r.net_delta_pct == 6.0
    tech, energy = r.sectors
    assert (tech["sector"], tech["capital_at_risk"], tech["pct_of_equity"]) == (
        "Technology",
        8000,
        8.0,
    )
    assert tech["pct_of_risk"] == 80.0 and energy["sector"] == "Energy"
    assert r.breaches == []


def test_unpriced_positions_are_counted_not_assumed_zero() -> None:
    r = calculate_portfolio_risk(
        [PositionRisk("AAPL", 1000, "Technology"), PositionRisk("MSFT", 1000, None, 5, 100)],
        50_000,
    )
    assert r.unpriced_positions == 1 and r.net_delta == 5
    assert r.sectors[1]["sector"] == "Unknown" or r.sectors[0]["sector"] == "Unknown"


@pytest.mark.parametrize(
    ("risk", "breached"), [(50_000, False), (50_001, True)], ids=["at-limit", "over-limit"]
)
def test_total_risk_limit_boundary(risk: float, breached: bool) -> None:
    r = calculate_portfolio_risk([PositionRisk("AAPL", risk, "Technology")], 100_000)
    assert any(b.rule_id == "BR-081" for b in r.breaches) is breached


def test_sector_concentration_breach_ignores_unknown_sector() -> None:
    over = calculate_portfolio_risk([PositionRisk("AAPL", 26_000, "Technology")], 100_000)
    assert [b.code for b in over.breaches] == ["sector"]
    unknown = calculate_portfolio_risk([PositionRisk("AAPL", 26_000, None)], 100_000)
    assert unknown.breaches == []


def test_net_delta_exposure_breach() -> None:
    r = calculate_portfolio_risk([PositionRisk("AAPL", 100, "Technology", 600, 200)], 100_000)
    assert [b.code for b in r.breaches] == ["net_delta"]  # 120,000 = 120% of equity


def test_zero_equity_gives_no_percentages() -> None:
    r = calculate_portfolio_risk([PositionRisk("AAPL", 100, "Technology")], 0)
    assert r.margin_pct is None and r.net_delta_pct is None and r.breaches == []


def test_entry_risk_reason() -> None:
    assert entry_risk_reason(100_000, 40_000, None) is None
    assert entry_risk_reason(100_000, 40_000, 10_000) is None  # exactly the limit
    assert "would be" in (entry_risk_reason(100_000, 40_000, 10_001) or "")
    assert "is 55.0%" in (entry_risk_reason(100_000, 55_000, None) or "")
    assert entry_risk_reason(0, 5_000, 1_000) is None
    assert MAX_CAPITAL_AT_RISK_PCT == 50.0


# ------------------------------------------------------------------ expected value


def test_pop_from_delta() -> None:
    assert ev.pop_from_delta(-0.2) == pytest.approx(0.8)
    assert ev.pop_from_delta(0.35) == pytest.approx(0.65)
    assert ev.pop_from_delta(1.4) == 0.0 and ev.pop_from_delta(None) is None


def test_expected_value_signs_and_inputs() -> None:
    assert ev.expected_value(0.8, 100, 400) == 0.0  # fair bet
    assert ev.expected_value(0.9, 100, 400) == 50.0
    assert ev.expected_value(0.5, 100, 400) == -150.0
    assert ev.expected_value(None, 100, 100) is None
    assert ev.expected_value(1.2, 100, 100) is None and ev.expected_value(0.5, -1, 1) is None


def test_pick_ev_and_ranking() -> None:
    base = {"side": "call", "entry_price": 2.5, "target_price": 4, "stop_loss": 1.5}
    assert ev.pick_ev({**base, "confidence": 0.6}) == 50.0  # 0.6x150 - 0.4x100
    assert ev.pick_ev({**base, "side": "stock", "confidence": 0.6}) == 0.5
    assert ev.pick_ev({**base, "stop_loss": None, "confidence": 0.6}) is None

    ranked = ev.rank_picks(
        [
            {**base, "symbol": "NOEV", "stop_loss": None, "confidence": 0.99},
            {**base, "symbol": "LOW", "confidence": 0.5},
            {**base, "symbol": "HIGH", "confidence": 0.8},
        ]
    )
    assert [p["symbol"] for p in ranked] == ["HIGH", "LOW", "NOEV"]
    assert ranked[0]["ev"] == 100.0 and ranked[2]["ev"] is None


def test_calibration_groups_by_layer() -> None:
    out = ev.calibration(
        [
            {"layer": "base", "pnl": 100, "expected": 40},
            {"layer": "base", "pnl": -50, "expected": None},
            {"layer": None, "pnl": 10, "expected": None},
        ]
    )
    base = next(g for g in out["groups"] if g["group"] == "base")
    assert base["trades"] == 2 and base["win_rate"] == 50.0 and base["avg_pnl"] == 25.0
    assert base["avg_expected"] == 40.0 and base["with_expected"] == 1
    assert any(g["group"] == "unassigned" for g in out["groups"]) and out["total_trades"] == 3
    assert ev.calibration([])["groups"] == []


# --------------------------------------------------------------- strategy matrix


def test_matrix_has_the_required_strategies_and_regimes() -> None:
    assert set(strategy_names()) == {
        "Iron Condor",
        "Put Credit Spread",
        "Call Credit Spread",
        "Butterfly",
        "Jade Lizard",
        "Straddle/Strangle",
    }
    m = build_matrix("NORMAL", gate_clear=True)
    assert m["regimes"] == list(REGIMES) and len(m["rows"]) == 6
    for row in m["rows"]:
        assert set(row["cells"]) == set(REGIMES)
        assert {c["availability"] for c in row["cells"].values()} <= {
            "available",
            "limited",
            "blocked",
        }


def test_gate_blocked_blocks_every_cell_of_the_current_regime_only() -> None:
    m = build_matrix("NORMAL", gate_clear=False)
    for row in m["rows"]:
        assert row["cells"]["NORMAL"]["availability"] == "blocked"
        assert row["cells"]["NORMAL"]["gate"] == "blocked"
        assert row["cells"]["GROWTH"]["gate"] is None
    # Other columns keep their own suitability.
    ic = next(r for r in m["rows"] if r["strategy"] == "Iron Condor")
    assert ic["cells"]["GROWTH"]["availability"] == ic["cells"]["GROWTH"]["base_availability"]


def test_clear_gate_and_unknown_regime() -> None:
    clear = build_matrix("GROWTH", gate_clear=True)
    assert all(r["cells"]["GROWTH"]["gate"] == "clear" for r in clear["rows"])
    unknown = build_matrix(None, gate_clear=None)
    assert not any(c["current"] for r in unknown["rows"] for c in r["cells"].values())


def test_layer_and_band_filters_flag_cells_without_removing_them() -> None:
    m = build_matrix("NORMAL", gate_clear=True, layer="growth", band="E")
    ic = next(r for r in m["rows"] if r["strategy"] == "Iron Condor")
    assert ic["cells"]["NORMAL"]["filtered"] is True  # bands A-C only
    straddle = next(r for r in m["rows"] if r["strategy"] == "Straddle/Strangle")
    assert straddle["cells"]["NORMAL"]["filtered"] is False  # growth layer, band E
    butterfly = next(r for r in m["rows"] if r["strategy"] == "Butterfly")
    assert butterfly["cells"]["DEFENSIVE"]["filtered"] is False  # blocked cells are not "filtered"


# --------------------------------------------------------------------- scenarios


def _put(**over) -> PositionInput:
    base = dict(
        trade_id="t1",
        symbol="AAPL",
        trade_type="put",
        direction="short",
        quantity=1,
        entry_price=2.0,
        strike=190.0,
        expiry=TODAY + timedelta(days=30),
    )
    base.update(over)
    return PositionInput(**base)


def _mkt(**over) -> MarketInput:
    base = dict(available=True, spot=200.0, mark=2.0, iv=0.30)
    base.update(over)
    return MarketInput(**base)


def test_no_shock_changes_nothing() -> None:
    r = reprice_position(_put(), _mkt(), Shock(), today=TODAY)
    assert r["priced"] and r["change"] == pytest.approx(0.0, abs=0.01)
    assert r["current_pnl"] == 0.0  # mark equals entry


def test_short_put_loses_when_the_price_falls_and_gains_when_it_rises() -> None:
    down = reprice_position(_put(), _mkt(), Shock(spot_pct=-10), today=TODAY)
    up = reprice_position(_put(), _mkt(), Shock(spot_pct=10), today=TODAY)
    assert down["change"] < -100 and up["change"] > 0
    assert up["change"] <= 200  # cannot make more than the credit (2.00 x 100)


def test_long_call_gains_when_the_price_rises() -> None:
    long_call = _put(trade_type="call", direction="long", strike=200.0)
    up = reprice_position(long_call, _mkt(mark=4.0), Shock(spot_pct=10), today=TODAY)
    down = reprice_position(long_call, _mkt(mark=4.0), Shock(spot_pct=-10), today=TODAY)
    assert up["change"] > 0 > down["change"]


def test_time_decay_helps_a_short_option_and_a_vol_rise_hurts_it() -> None:
    later = reprice_position(_put(), _mkt(), Shock(days_forward=15), today=TODAY)
    vol = reprice_position(_put(), _mkt(), Shock(iv_shift=0.10), today=TODAY)
    assert later["change"] > 0 and vol["change"] < 0


def test_expiry_uses_intrinsic_value() -> None:
    r = reprice_position(_put(), _mkt(), Shock(spot_pct=-10, days_forward=30), today=TODAY)
    # Spot 180 vs strike 190: worth 10.00 at expiry; short at 2.00 credit, was marked 2.00.
    assert r["scenario_pnl"] == pytest.approx((2.0 - 10.0) * 100)
    otm = reprice_position(_put(), _mkt(), Shock(spot_pct=5, days_forward=40), today=TODAY)
    assert otm["scenario_pnl"] == pytest.approx(200.0)  # expires worthless: keep the credit


def test_stock_position_scales_one_to_one() -> None:
    stock = PositionInput("t2", "AAPL", "stock", "long", 10, 100.0)
    r = reprice_position(
        stock, MarketInput(available=True, spot=100.0, mark=100.0), Shock(spot_pct=-10), today=TODAY
    )
    assert r["current_pnl"] == 0.0 and r["scenario_pnl"] == -100.0 and r["change"] == -100.0


def test_missing_inputs_are_unpriced_with_a_reason() -> None:
    assert (
        reprice_position(_put(), MarketInput(available=False), Shock(), today=TODAY)["reason"]
        == "no market data"
    )
    assert reprice_position(_put(), _mkt(iv=None), Shock(), today=TODAY)["reason"] == (
        "no implied volatility"
    )
    assert reprice_position(_put(strike=None), _mkt(), Shock(), today=TODAY)["priced"] is False
    crash = reprice_position(_put(), _mkt(), Shock(spot_pct=-100), today=TODAY)
    assert crash["priced"] is False


def test_totals_leave_out_unpriced_positions() -> None:
    res = run_scenario(
        [(_put(), _mkt()), (_put(trade_id="t2"), MarketInput(available=False))],
        Shock(spot_pct=-10),
        today=TODAY,
    )
    assert res["priced"] == 1 and res["unpriced"] == 1
    assert res["total_change"] == res["positions"][0]["change"]


def test_ladder_is_monotonic_for_a_short_put() -> None:
    ladder = spot_ladder([(_put(), _mkt())], today=TODAY)
    changes = [p["total_change"] for p in ladder]
    assert changes == sorted(changes)  # a short put never loses less as the price falls
    assert [p["spot_pct"] for p in ladder][:2] == [-20.0, -10.0]
