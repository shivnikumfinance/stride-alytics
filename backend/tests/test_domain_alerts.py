"""Exit/risk alert rules: severities, boundaries, suggested actions, missing data."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.domain.alerts import MarketInput, PositionInput, evaluate_position, summarize

TODAY = date(2026, 6, 1)


def pos(**over) -> PositionInput:
    base = dict(
        trade_id="t1",
        symbol="AAPL",
        trade_type="put",
        direction="short",
        quantity=2,
        entry_price=2.0,
        strike=100.0,
        expiry=TODAY + timedelta(days=30),
        layer="base",
    )
    base.update(over)
    return PositionInput(**base)


def mkt(**over) -> MarketInput:
    base = dict(available=True, spot=110.0, mark=1.5, delta=-0.2, theta=0.05)
    base.update(over)
    return MarketInput(**base)


def ev(p=None, m=None, **kw):
    return evaluate_position(p or pos(), m or mkt(), today=TODAY, **kw)


def codes(alert) -> list[str]:
    return [r.code for r in alert.reasons]


# ------------------------------------------------------------------ calm


def test_a_calm_position_is_normal_and_reports_its_numbers() -> None:
    a = ev()
    assert (a.severity, a.action, a.reasons) == ("normal", "hold", [])
    assert a.pnl == 100.0 and a.pnl_pct == 0.25  # (2.00 - 1.50) x 2 x 100; 25% of the credit
    assert (
        a.dte == 30 and a.itm is False and a.data_available is True and a.assignment_risk is False
    )


# ------------------------------------------------------------------ time


@pytest.mark.parametrize(
    "days,severity,code",
    [
        (30, "normal", None),
        (8, "normal", None),
        (7, "watch", "dte"),
        (4, "watch", "dte"),
        (3, "warning", "dte"),
        (0, "warning", "dte"),
        (-1, "critical", "expired"),
    ],
)
def test_days_to_expiry_boundaries(days, severity, code) -> None:
    a = ev(pos(expiry=TODAY + timedelta(days=days)))
    assert a.severity == severity and (code in codes(a) if code else a.reasons == [])


def test_an_expired_open_trade_must_be_closed() -> None:
    a = ev(pos(expiry=TODAY - timedelta(days=2)))
    assert a.severity == "critical" and a.action == "close" and a.reasons[0].rule_id == "BR-050"
    assert a.assignment_risk is False  # expiry is its own code, not an assignment alarm


# ------------------------------------------------------------- moneyness


@pytest.mark.parametrize(
    "trade_type,strike,spot,severity,code",
    [
        ("put", 100, 110, "normal", None),  # out of the money
        ("put", 100, 98, "warning", "itm"),  # 2% in the money
        ("put", 100, 94, "critical", "assignment_risk"),  # 6% in the money
        ("call", 100, 90, "normal", None),
        ("call", 100, 103, "warning", "itm"),
        ("call", 100, 106, "critical", "assignment_risk"),
    ],
)
def test_short_options_in_the_money(trade_type, strike, spot, severity, code) -> None:
    a = ev(
        pos(trade_type=trade_type, strike=strike),
        mkt(spot=spot, delta=0.1 if trade_type == "call" else -0.1),
    )
    assert a.severity == severity and (code in codes(a) if code else "itm" not in codes(a))
    assert a.assignment_risk is (code == "assignment_risk")


def test_a_long_option_in_the_money_is_not_an_alarm() -> None:
    a = ev(pos(direction="long", entry_price=2.0), mkt(spot=90.0, mark=11.0, delta=-0.6))
    assert "itm" not in codes(a) and "assignment_risk" not in codes(a)
    assert a.itm is True


# ----------------------------------------------------------------- delta


@pytest.mark.parametrize(
    "delta,layer,severity,code",
    [
        (-0.70, "base", "critical", "assignment_risk"),  # boundary is inclusive
        (-0.69, "base", "warning", "delta_high"),
        (-0.50, "base", "warning", "delta_high"),
        (-0.49, "base", "watch", "delta_watch"),
        (-0.30, "base", "watch", "delta_watch"),
        (-0.29, "base", "normal", None),
        (-0.35, "growth", "normal", None),  # the Growth layer tolerates more
        (-0.40, "growth", "watch", "delta_watch"),
        (0.72, "base", "critical", "assignment_risk"),  # calls: magnitude is what matters
    ],
)
def test_delta_tiers_for_short_options(delta, layer, severity, code) -> None:
    a = ev(pos(layer=layer), mkt(delta=delta))
    assert a.severity == severity and (code in codes(a) if code else a.reasons == [])


def test_a_long_option_with_high_delta_warns_but_is_never_an_assignment_alarm() -> None:
    a = ev(pos(direction="long", entry_price=2.0), mkt(mark=2.0, delta=0.75, spot=105))
    assert a.severity == "warning" and "delta_high" in codes(a) and a.assignment_risk is False


# ----------------------------------------------------------------- profit


@pytest.mark.parametrize(
    "mark,severity,pct",
    [(1.10, "normal", 0.45), (1.0, "watch", 0.5), (0.5, "watch", 0.75), (0.4, "warning", 0.8)],
)
def test_profit_target_on_short_premium(mark, severity, pct) -> None:
    a = ev(m=mkt(mark=mark))
    assert a.severity == severity and a.pnl_pct == pytest.approx(pct)
    if severity != "normal":
        assert a.action == "close" and "profit_target" in codes(a)


# ------------------------------------------------------------------- loss


@pytest.mark.parametrize(
    "mark,severity",
    [
        (2.99, "normal"),
        (3.0, "watch"),
        (3.99, "watch"),
        (4.0, "warning"),
        (5.99, "warning"),
        (6.0, "critical"),
    ],
)
def test_loss_tiers_against_the_credit(mark, severity) -> None:
    a = ev(m=mkt(mark=mark))
    assert a.severity == severity
    # A watch-level loss means "keep an eye on it"; warning and critical losses suggest closing.
    assert (
        a.action
        == {"normal": "hold", "watch": "hold", "warning": "close", "critical": "close"}[severity]
    )


@pytest.mark.parametrize(
    "mark,severity", [(3.0, "normal"), (3.5, "watch"), (4.5, "warning"), (7.0, "critical")]
)
def test_loss_tiers_against_capital_at_risk_when_known(mark, severity) -> None:
    # capital at risk $1,000 (2 contracts): loss = (mark - 2.0) x 200 -> 100 / 300 / 500 / 1000
    a = ev(pos(risk_amount=1000.0), mkt(mark=mark))
    assert a.severity == severity


@pytest.mark.parametrize(
    "mark,severity", [(2.5, "normal"), (2.0, "watch"), (1.0, "warning"), (0.4, "critical")]
)
def test_loss_tiers_for_long_options(mark, severity) -> None:
    a = ev(
        pos(direction="long", entry_price=4.0, trade_type="call"),
        mkt(mark=mark, spot=110, delta=0.1),
    )
    assert a.severity == severity


def test_stock_positions_are_priced_per_share() -> None:
    a = ev(
        pos(
            trade_type="stock",
            direction="long",
            entry_price=100.0,
            quantity=10,
            strike=None,
            expiry=None,
        ),
        mkt(mark=90.0, spot=90.0, delta=None),
    )
    assert a.pnl == -100.0 and a.pnl_pct == -0.1 and a.severity == "normal" and a.dte is None


# ---------------------------------------------------------- missing data


def test_missing_prices_skip_price_rules_but_flag_the_position() -> None:
    a = ev(m=MarketInput(available=False))
    assert a.severity == "watch" and codes(a) == ["no_market_data"]
    assert a.pnl is None and a.delta is None and a.data_available is False


def test_date_rules_still_run_without_prices() -> None:
    a = ev(pos(expiry=TODAY + timedelta(days=2)), MarketInput(available=False))
    assert a.severity == "warning" and set(codes(a)) == {"dte", "no_market_data"}


def test_stock_without_prices_is_not_flagged() -> None:
    a = ev(
        pos(trade_type="stock", direction="long", strike=None, expiry=None),
        MarketInput(available=False),
    )
    assert a.severity == "normal" and a.reasons == []


# ----------------------------------------------------------------- regime


@pytest.mark.parametrize(
    "score,flagged", [(24.9, True), (25.0, False), (80.0, False), (None, False)]
)
def test_regime_deterioration_boundary(score, flagged) -> None:
    a = ev(regime_score=score)
    assert ("regime" in codes(a)) is flagged
    if flagged:
        assert a.severity == "warning" and a.action == "hedge"  # Base layer: hedge


def test_regime_deterioration_closes_growth_positions() -> None:
    assert ev(pos(layer="growth"), regime_score=10).action == "close"


# ---------------------------------------------------------------- actions


def test_assignment_alarm_suggests_roll_with_time_left_and_close_without() -> None:
    assert ev(m=mkt(delta=-0.75)).action == "roll"
    last_day = ev(pos(expiry=TODAY), mkt(delta=-0.75))
    assert last_day.severity == "critical" and last_day.action == "close"


def test_the_most_urgent_reason_decides_the_action() -> None:
    # profit target (close, watch) + ITM (roll, warning): the warning wins -> roll
    a = ev(m=mkt(mark=1.0, spot=99.0, delta=-0.2))
    assert a.severity == "warning" and a.action == "roll"
    assert [r.severity for r in a.reasons] == sorted(
        (r.severity for r in a.reasons),
        key=lambda s: -["normal", "watch", "warning", "critical"].index(s),
    )


def test_equal_severity_prefers_the_more_decisive_action() -> None:
    # profit target warning (close) vs delta_high warning (roll): close
    a = ev(m=mkt(mark=0.3, delta=-0.55))
    assert a.severity == "warning" and a.action == "close"


# ----------------------------------------------------------- numbers / misc


@pytest.mark.parametrize(
    "direction,delta,qty,expected",
    [("short", -0.2, 2, 40.0), ("long", 0.5, 1, 50.0), ("short", 0.3, 1, -30.0)],
)
def test_position_delta_sign_and_size(direction, delta, qty, expected) -> None:
    a = ev(
        pos(direction=direction, quantity=qty),
        mkt(delta=delta, spot=120, mark=0.5 if direction == "short" else 3.0),
    )
    assert a.position_delta == expected


def test_summarize_counts_each_severity() -> None:
    alerts = [ev(), ev(), ev(m=mkt(mark=1.0)), ev(m=mkt(delta=-0.8))]
    assert summarize(alerts) == {"normal": 2, "watch": 1, "warning": 0, "critical": 1}
