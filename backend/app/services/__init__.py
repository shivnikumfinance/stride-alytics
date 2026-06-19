"""Business-logic services for the StrideAlytics API."""

from app.services.greeks import (
    GreeksResult,
    calculate_greeks,
    calculate_greeks_dict,
    calculate_option_price,
)
from app.services.screener import ScreenerFilters, run_screener
from app.services.regime import RegimeResult, detect_regime
from app.services.portfolio import (
    Portfolio,
    PortfolioStore,
    Trade,
    calculate_pnl,
    portfolio_summary,
    portfolio_trade_breakdown,
    store as portfolio_store,
)
from app.services.auth import plan_from_claims, verify_supabase_jwt

__all__ = [
    "GreeksResult",
    "calculate_greeks",
    "calculate_greeks_dict",
    "calculate_option_price",
    "ScreenerFilters",
    "run_screener",
    "RegimeResult",
    "detect_regime",
    "Portfolio",
    "PortfolioStore",
    "Trade",
    "calculate_pnl",
    "portfolio_summary",
    "portfolio_trade_breakdown",
    "portfolio_store",
    "verify_supabase_jwt",
    "plan_from_claims",
]
