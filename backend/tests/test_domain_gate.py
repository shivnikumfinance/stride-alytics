"""Do-Not-Trade gate: every rule, both sides of every boundary, and the fail-safe."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.domain.gate import (
    SymbolData,
    evaluate_entry,
    evaluate_master,
    evaluate_symbol,
)
from app.domain.regime_score import RegimeScore

TODAY = date(2026, 6, 1)


def regime(score: float | None = 60, *, market_down=False, state: str | None = None) -> RegimeScore:
    st = state or ("UNKNOWN" if score is None else "NORMAL")
    return RegimeScore(
        score=score, state=st, components={}, weights={}, market_down=market_down, source="live"
    )


def good(**over) -> SymbolData:
    base = dict(
        symbol="AAPL",
        fetched=True,
        quote_type="EQUITY",
        market_cap=50e9,
        next_earnings=TODAY + timedelta(days=30),
        spread_pct=3.0,
        open_interest=1000,
    )
    base.update(over)
    return SymbolData(**base)


def rules(result) -> list[str]:
    return [r.rule_id for r in result.reasons]


def symbol_gate(data: SymbolData, **over):
    args = dict(trade_type="put", layer="growth", news_flag=False, today=TODAY)
    args.update(over)
    return evaluate_symbol(data, **args)


# ----------------------------------------------------------- master gate


def test_healthy_account_and_market_is_clear() -> None:
    r = evaluate_master(regime(60), equity=100_000, min_equity=50_000)
    assert r.clear and r.reasons == []
    assert {"BR-010", "BR-012", "BR-015"} <= set(r.checked)


def test_market_down_blocks_br010() -> None:
    assert rules(evaluate_master(regime(60, market_down=True), equity=1, min_equity=0)) == [
        "BR-010"
    ]


@pytest.mark.parametrize("score,blocked", [(24.9, True), (25.0, False), (25.1, False)])
def test_regime_baseline_boundary_br015(score, blocked) -> None:
    r = evaluate_master(regime(score, state="DEFENSIVE"), equity=1, min_equity=0)
    assert (rules(r) == ["BR-015"]) is blocked and r.clear is (not blocked)


def test_regime_unavailable_blocks_with_a_data_reason() -> None:
    r = evaluate_master(regime(None), equity=1, min_equity=0)
    assert not r.clear and r.reasons[0].kind == "data" and r.reasons[0].rule_id == "BR-015"
    assert not evaluate_master(None, equity=1, min_equity=0).clear


@pytest.mark.parametrize(
    "equity,min_equity,blocked",
    [(49_999, 50_000, True), (50_000, 50_000, False), (1, 0, False)],  # 0 disables the guardrail
)
def test_equity_guardrail_br012(equity, min_equity, blocked) -> None:
    r = evaluate_master(regime(60), equity=equity, min_equity=min_equity)
    assert (rules(r) == ["BR-012"]) is blocked


def test_assignment_alarms_and_correlation_reporting() -> None:
    default = evaluate_master(regime(60), equity=1, min_equity=0)
    assert set(default.not_evaluated) == {"BR-011", "BR-013"} and default.clear
    none = evaluate_master(regime(60), equity=1, min_equity=0, assignment_alarms=0)
    assert none.not_evaluated == ["BR-013"] and "BR-011" in none.checked and none.clear
    alarmed = evaluate_master(regime(60), equity=1, min_equity=0, assignment_alarms=2)
    assert rules(alarmed) == ["BR-011"]


# ----------------------------------------------------------- symbol gate


def test_a_clean_candidate_is_clear() -> None:
    r = symbol_gate(good())
    assert r.clear and {"BR-017", "BR-018", "BR-019", "BR-020", "BR-021"} <= set(r.checked)


@pytest.mark.parametrize("spread,blocked", [(10.0, False), (10.01, True), (0.0, False), (25, True)])
def test_spread_boundary_br017(spread, blocked) -> None:
    assert (rules(symbol_gate(good(spread_pct=spread))) == ["BR-017"]) is blocked


@pytest.mark.parametrize("oi,blocked", [(500, False), (499, True), (0, True)])
def test_open_interest_boundary_br018(oi, blocked) -> None:
    assert (rules(symbol_gate(good(open_interest=oi))) == ["BR-018"]) is blocked


@pytest.mark.parametrize("cap,blocked", [(2e9, False), (1.99e9, True)])
def test_market_cap_boundary_br019(cap, blocked) -> None:
    assert (rules(symbol_gate(good(market_cap=cap), layer="growth")) == ["BR-019"]) is blocked


@pytest.mark.parametrize(
    "cap,expected", [(10e9, []), (9.9e9, ["BR-042"]), (1.9e9, ["BR-019", "BR-042"])]
)
def test_base_layer_needs_10b_br042(cap, expected) -> None:
    assert rules(symbol_gate(good(market_cap=cap), layer="base")) == expected


@pytest.mark.parametrize(
    "days,blocked", [(0, True), (13, True), (14, True), (15, False), (60, False)]
)
def test_earnings_window_boundary_br020(days, blocked) -> None:
    r = symbol_gate(good(next_earnings=TODAY + timedelta(days=days)))
    assert (rules(r) == ["BR-020"]) is blocked and r.clear is (not blocked)


def test_news_flag_blocks_br021() -> None:
    assert rules(symbol_gate(good(), news_flag=True)) == ["BR-021"]


# ------------------------------------------------------ fail-safe (no data)


def test_missing_values_block_instead_of_passing() -> None:
    r = symbol_gate(good(market_cap=None, next_earnings=None, spread_pct=None, open_interest=None))
    assert not r.clear
    assert sorted(rules(r)) == ["BR-017", "BR-018", "BR-019", "BR-020"]
    assert {x.kind for x in r.reasons} == {"data"}
    assert all("Data unavailable" in x.message for x in r.reasons)


def test_a_past_earnings_date_is_treated_as_stale_data() -> None:
    r = symbol_gate(good(next_earnings=TODAY - timedelta(days=5)))
    assert rules(r) == ["BR-020"] and r.reasons[0].kind == "data"


def test_nothing_fetched_blocks_every_data_rule() -> None:
    r = symbol_gate(SymbolData(symbol="AAPL", fetched=False))
    assert not r.clear and {"BR-017", "BR-018", "BR-019", "BR-020"} <= set(rules(r))


# ------------------------------------------------ what does not apply


def test_etfs_skip_market_cap_and_earnings_rules() -> None:
    etf = good(symbol="SPY", quote_type="ETF", market_cap=None, next_earnings=None)
    r = symbol_gate(etf, layer="base")
    assert r.clear and "BR-019" not in r.checked and "BR-042" not in r.checked


def test_stock_trades_skip_option_liquidity_rules() -> None:
    r = symbol_gate(good(spread_pct=None, open_interest=None), trade_type="stock")
    assert r.clear and "BR-017" not in r.checked


# -------------------------------------------------------- combined entry


def entry(**over):
    args = dict(
        regime=regime(60),
        equity=100_000,
        min_equity=0,
        symbol_data=good(),
        trade_type="put",
        layer="base",
        news_flag=False,
        today=TODAY,
    )
    args.update(over)
    return evaluate_entry(**args)


def test_entry_clear_when_everything_passes() -> None:
    r = entry()
    assert r.clear and r.reasons == [] and "BR-013" in r.not_evaluated


def test_entry_collects_every_failing_rule_not_just_the_first() -> None:
    r = entry(
        regime=regime(20, market_down=True, state="DEFENSIVE"),
        symbol_data=good(spread_pct=20, open_interest=10),
        news_flag=True,
    )
    assert set(rules(r)) == {"BR-010", "BR-015", "BR-017", "BR-018", "BR-021"}


@pytest.mark.parametrize(
    "state,blocked", [("DEFENSIVE", True), ("UNKNOWN", True), ("NORMAL", False), ("GROWTH", False)]
)
def test_growth_layer_is_locked_outside_normal_and_growth_br023(state, blocked) -> None:
    score = None if state == "UNKNOWN" else {"DEFENSIVE": 35, "NORMAL": 55, "GROWTH": 80}[state]
    r = entry(layer="growth", regime=regime(score, state=state))
    assert ("BR-023" in rules(r)) is blocked


def test_base_layer_trades_in_a_defensive_regime_above_the_baseline() -> None:
    assert entry(layer="base", regime=regime(35, state="DEFENSIVE")).clear


def test_entry_with_no_regime_object_is_blocked() -> None:
    assert not entry(regime=None).clear
