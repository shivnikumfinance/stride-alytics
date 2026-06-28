"""End-to-end backend tests for Phase 1 services.

These tests run WITHOUT a database (pure-Python services) and validate:
  - Black-Scholes Greeks engine
  - Screener filter pipeline
  - Market regime detector
  - Portfolio analytics (PnL, win rate, summary)
  - Auth JWT dev-token path

Run with:  uv run pytest backend/tests/test_services.py -v
"""

from __future__ import annotations

import math
from uuid import uuid4

import pytest

from app.services.greeks import calculate_greeks, calculate_greeks_dict, calculate_option_price
from app.services.regime import detect_regime
from app.services.portfolio import (
    PortfolioStore,
    Trade,
    calculate_pnl,
    portfolio_summary,
    portfolio_trade_breakdown,
)
from app.services.screener import ScreenerFilters, run_screener
from app.services.auth import plan_from_claims


# ---------------------------------------------------------------------------
# Greeks
# ---------------------------------------------------------------------------

class TestGreeks:
    def test_call_delta_in_0_1_range(self):
        g = calculate_greeks(spot=100, strike=100, time_to_expiry=30 / 365)
        assert 0.4 < g.delta < 0.6

    def test_put_delta_negative(self):
        g = calculate_greeks(spot=100, strike=100, time_to_expiry=30 / 365, option_type="put")
        assert -0.6 < g.delta < -0.4

    def test_put_call_parity(self):
        """Put-call parity: C - P = S - K * exp(-rT)"""
        spot, strike, r, t, sigma = 100.0, 100.0, 0.05, 0.5, 0.2
        c = calculate_option_price(spot, strike, t, r, sigma, "call")
        p = calculate_option_price(spot, strike, t, r, sigma, "put")
        diff = c - p
        expected = spot - strike * math.exp(-r * t)
        assert math.isclose(diff, expected, rel_tol=1e-6)

    def test_gamma_positive(self):
        g = calculate_greeks(100, 100, 0.1)
        assert g.gamma > 0

    def test_vega_per_1_percent(self):
        """Vega at 30% IV with 30 DTE should be a few cents per 1% IV."""
        g = calculate_greeks(100, 100, 30 / 365, volatility=0.3)
        assert 0.05 < g.vega < 0.20

    def test_rejects_zero_volatility(self):
        with pytest.raises(ValueError):
            calculate_greeks(100, 100, 0.1, volatility=0)

    def test_rejects_zero_time(self):
        with pytest.raises(ValueError):
            calculate_greeks(100, 100, 0)

    def test_dict_round_trip(self):
        d = calculate_greeks_dict(100, 100, 0.1, option_type="call")
        assert set(d.keys()) == {
            "delta", "gamma", "theta", "vega", "rho", "price_call", "price_put"
        }


# ---------------------------------------------------------------------------
# Regime
# ---------------------------------------------------------------------------

class TestRegime:
    def test_returns_valid_regime(self):
        r = detect_regime("AAPL", lookback_days=30)
        assert r.regime in {"bull", "bear", "ranging"}
        assert 0 <= r.confidence <= 1

    def test_lookback_clamped_in_endpoint(self):
        r = detect_regime("SPY", lookback_days=5)
        assert r.lookback_days >= 5


# ---------------------------------------------------------------------------
# Screener
# ---------------------------------------------------------------------------

class TestScreener:
    def test_run_returns_payload(self):
        result = run_screener(ScreenerFilters(
            symbol="AAPL", expiry_days_min=0, expiry_days_max=60,
            min_volume=0, min_open_interest=0, limit=10,
        ))
        assert result["symbol"] == "AAPL"
        assert result["spot"] > 0
        assert isinstance(result["results"], list)
        assert len(result["results"]) <= 10

    def test_option_type_filter(self):
        result = run_screener(ScreenerFilters(
            symbol="MSFT", option_type="call", expiry_days_min=0, expiry_days_max=60,
            min_volume=0, min_open_interest=0, limit=50,
        ))
        for row in result["results"]:
            assert row["option_type"] == "call"

    def test_strike_range_filter(self):
        result = run_screener(ScreenerFilters(
            symbol="SPY", min_strike=550, max_strike=600,
            expiry_days_min=0, expiry_days_max=60,
            min_volume=0, min_open_interest=0, limit=50,
        ))
        for row in result["results"]:
            assert 550 <= row["strike"] <= 600

    def test_limit_caps_results(self):
        result = run_screener(ScreenerFilters(
            symbol="AAPL", limit=3, expiry_days_min=0, expiry_days_max=60,
            min_volume=0, min_open_interest=0,
        ))
        assert len(result["results"]) <= 3


# ---------------------------------------------------------------------------
# Portfolio analytics
# ---------------------------------------------------------------------------

class TestPortfolio:
    def _make_trade(self, **overrides) -> Trade:
        defaults = dict(
            id=uuid4(), user_id=uuid4(), portfolio_id=uuid4(),
            symbol="AAPL", trade_type="call", direction="long",
            entry_price=2.0, exit_price=3.0, quantity=10,
            entry_date=None, exit_date=None, notes=None,
        )
        defaults.update(overrides)
        return Trade(**defaults)

    def test_long_winner_pnl(self):
        t = self._make_trade(direction="long", entry_price=2, exit_price=3, quantity=10)
        assert calculate_pnl(t) == 10.0

    def test_short_winner_pnl(self):
        t = self._make_trade(direction="short", entry_price=3, exit_price=2, quantity=10)
        assert calculate_pnl(t) == 10.0

    def test_long_loser_pnl(self):
        t = self._make_trade(direction="long", entry_price=3, exit_price=2, quantity=10)
        assert calculate_pnl(t) == -10.0

    def test_open_trade_zero_pnl(self):
        t = self._make_trade(exit_price=None)
        assert calculate_pnl(t) == 0.0

    def test_store_crud(self):
        store = PortfolioStore()
        user = uuid4()
        p = store.create_portfolio(user, "Test", "desc")
        t = self._make_trade(user_id=user, portfolio_id=p.id)
        store.add_trade(t)

        s = portfolio_summary(p)
        assert s["total_trades"] == 1
        assert s["closed_trades"] == 1
        assert s["winners"] == 1

    def test_duplicate_portfolio_name_rejected(self):
        store = PortfolioStore()
        user = uuid4()
        store.create_portfolio(user, "X")
        with pytest.raises(ValueError):
            store.create_portfolio(user, "X")

    def test_other_user_cannot_see_portfolio(self):
        store = PortfolioStore()
        u1, u2 = uuid4(), uuid4()
        p = store.create_portfolio(u1, "Private")
        with pytest.raises(KeyError):
            store.get_portfolio(u2, p.id)

    def test_trade_breakdown_shape(self):
        t = self._make_trade()
        rows = portfolio_trade_breakdown([t])
        assert len(rows) == 1
        assert set(rows[0].keys()) >= {
            "trade_id", "symbol", "trade_type", "direction",
            "quantity", "entry_price", "exit_price", "pnl", "open",
        }


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

class TestAuthPlan:
    def test_default_free(self):
        assert plan_from_claims({}) == "free"

    def test_pro_from_metadata(self):
        assert plan_from_claims({"user_metadata": {"subscription_plan": "pro"}}) == "pro"

    def test_lowercase_normalized(self):
        assert plan_from_claims({"user_metadata": {"subscription_plan": "Pro"}}) == "pro"
        assert plan_from_claims({"user_metadata": {"subscription_plan": "Free"}}) == "free"
