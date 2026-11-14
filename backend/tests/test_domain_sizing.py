"""Allocation, sizing and band caps."""

from __future__ import annotations

import pytest

from app.domain.allocation import growth_locked, layer_split
from app.domain.sizing import band_status, calculate_sizing

CAPS = {"A": 30, "B": 25, "C": 20, "D": 15, "E": 10}


def size(**over):
    args = dict(
        account_size=100_000,
        layer="base",
        risk_pct=1.25,
        regime_state="NORMAL",
        max_loss_per_contract=500,
    )
    args.update(over)
    return calculate_sizing(**args)


# ------------------------------------------------------------ allocation


@pytest.mark.parametrize(
    "state,base,growth",
    [("DEFENSIVE", 80, 20), ("NORMAL", 60, 40), ("GROWTH", 40, 60), ("UNKNOWN", 80, 20)],
)
def test_layer_split(state, base, growth) -> None:
    assert layer_split(state) == {"base": base, "growth": growth}


def test_growth_layer_lock() -> None:
    assert growth_locked("DEFENSIVE") and growth_locked("UNKNOWN")
    assert not growth_locked("NORMAL") and not growth_locked("GROWTH")


# ---------------------------------------------------------------- sizing


def test_max_loss_mode() -> None:
    r = size()
    assert (r.mode, r.risk_budget, r.quantity, r.risk_amount) == ("max_loss", 1250.0, 2, 1000.0)
    assert not r.blocked and r.warnings == ["No band assigned: the band cap was not checked."]


def test_credit_mode_follows_fr_670_and_warns() -> None:
    r = size(max_loss_per_contract=None, credit=2.0)  # 1250 / (2.0 * 100)
    assert (r.mode, r.quantity) == ("credit", 6)
    assert r.risk_amount is None
    assert any("premium" in w for w in r.warnings)


def test_max_loss_wins_over_credit_when_both_given() -> None:
    assert size(credit=2.0).mode == "max_loss"


def test_defensive_regime_halves_the_budget() -> None:
    r = size(regime_state="DEFENSIVE")
    assert r.risk_budget == 625.0 and r.quantity == 1
    assert any("cut to 50%" in w for w in r.warnings)


def test_unknown_regime_is_treated_like_defensive() -> None:
    assert size(regime_state="UNKNOWN").risk_budget == 625.0


@pytest.mark.parametrize("state", ["DEFENSIVE", "UNKNOWN"])
def test_growth_layer_is_blocked_when_locked(state) -> None:
    r = size(layer="growth", risk_pct=2.5, regime_state=state)
    assert r.blocked and r.quantity == 0 and r.reasons[0]["rule_id"] == "BR-023"


def test_growth_layer_sizes_in_a_normal_regime() -> None:
    r = size(layer="growth", risk_pct=2.5)
    assert not r.blocked and r.risk_budget == 2500.0 and r.quantity == 5


def test_risk_outside_the_documented_range_warns_but_still_sizes() -> None:
    r = size(risk_pct=3.0)
    assert not r.blocked and r.quantity == 6  # 3000 / 500
    assert any("outside the documented base range" in w for w in r.warnings)


def test_budget_smaller_than_one_contract_is_blocked() -> None:
    r = size(max_loss_per_contract=5000)
    assert r.blocked and r.reasons[0]["rule_id"] == "FR-630"


def test_no_price_input_gives_no_quantity_but_is_not_a_block() -> None:
    r = size(max_loss_per_contract=None, credit=None)
    assert r.mode == "none" and r.quantity == 0 and not r.blocked
    assert any("credit or the max loss" in w for w in r.warnings)


@pytest.mark.parametrize("account", [0, -5])
def test_invalid_account_size_blocks(account) -> None:
    assert size(account_size=account).blocked


def test_invalid_layer_blocks() -> None:
    assert size(layer="yolo").blocked


# ------------------------------------------------------------- band caps


def test_band_cap_reduces_quantity_to_fit() -> None:
    # growth budget 2500 -> 5 contracts, but band A has only $1,000 of room (30% = $30,000).
    r = size(layer="growth", risk_pct=2.5, band="A", band_caps=CAPS, band_exposure_dollars=29_000)
    assert r.quantity == 2 and r.risk_amount == 1000.0 and not r.blocked
    assert any("limits the quantity from 5 to 2" in w for w in r.warnings)


def test_band_at_its_cap_blocks() -> None:
    r = size(layer="growth", risk_pct=2.5, band="A", band_caps=CAPS, band_exposure_dollars=29_800)
    assert r.blocked and r.reasons[0]["rule_id"] == "BR-034"


def test_band_cap_in_credit_mode_blocks_on_overflow() -> None:
    r = size(
        max_loss_per_contract=None,
        credit=2.0,
        band="A",
        band_caps=CAPS,
        band_exposure_dollars=29_500,
    )
    assert r.blocked and r.reasons[0]["rule_id"] == "BR-034"


def test_near_cap_warning_at_80_percent() -> None:
    # 23,500 + 1,000 = 24.5% of capital; 80% of the 30% cap is 24%.
    r = size(band="A", band_caps=CAPS, band_exposure_dollars=23_500)
    assert not r.blocked and r.band_exposure_after_pct == 24.5
    assert any("near its limit" in w for w in r.warnings)
    quiet = size(band="A", band_caps=CAPS, band_exposure_dollars=20_000)
    assert not any("near its limit" in w for w in quiet.warnings)


def test_unknown_band_is_reported() -> None:
    r = size(band="Z", band_caps=CAPS)
    assert any("No cap is configured for band Z" in w for w in r.warnings)


def test_band_status_levels() -> None:
    rows = band_status(
        account_size=100_000,
        band_caps=CAPS,
        exposure_by_band={"A": 31_000, "B": 21_000, "C": 1_000},
    )
    by = {r["band"]: r for r in rows}
    assert by["A"]["status"] == "over" and by["A"]["exposure_pct"] == 31.0
    assert by["B"]["status"] == "near"  # 21% >= 80% of 25%
    assert by["C"]["status"] == "ok" and by["D"]["exposure"] == 0
    assert [r["band"] for r in rows] == ["A", "B", "C", "D", "E"]
