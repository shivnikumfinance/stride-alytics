"""Business-logic services for the StrideAlytics API.

One file per backend resource. Services must be HTTP‑agnostic — they take
plain Python types and return plain Python types / Pydantic models. The
endpoint layer (``app.api.v1.endpoints.*``) is the only place that imports
``fastapi`` and translates requests into service calls.
"""

from app.services.greeks import (
    GreeksResult,
    calculate_greeks,
    calculate_greeks_dict,
    calculate_option_price,
)
from app.services.market import fetch_tickers
from app.services.screener import ScreenerFilters, run_screener
from app.services.regime import RegimeResult, detect_regime
from app.services.portfolio import (
    Portfolio,
    PortfolioStore,
    Trade,
    calculate_pnl,
    portfolio_summary,
    portfolio_trade_breakdown,
    reset_store,
    store as portfolio_store,
)
from app.services.auth import plan_from_claims, verify_supabase_jwt

__all__ = [
    "GreeksResult",
    "calculate_greeks",
    "calculate_greeks_dict",
    "calculate_option_price",
    "fetch_tickers",
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
    "reset_store",
    "portfolio_store",
    "verify_supabase_jwt",
    "plan_from_claims",
]
