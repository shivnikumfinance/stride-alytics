"""API v1 endpoint routers — aggregated by ``app.api.v1.router``.

Each module here must expose an ``APIRouter`` instance named ``router``.
Adding a new resource means: add the module to this file *and* register it
in ``app.api.v1.router``.
"""

from app.api.v1.endpoints import (
    alerts,
    analytics,
    auth,
    dashboard,
    gate,
    greeks,
    logs,
    market,
    options,
    picks,
    portfolio,
    regime,
    scenarios,
    screener,
    settings,
    sizing,
    strategy_matrix,
    symbols,
    trades,
    watchlists,
)

__all__ = [
    "alerts",
    "analytics",
    "auth",
    "dashboard",
    "gate",
    "greeks",
    "logs",
    "market",
    "options",
    "picks",
    "portfolio",
    "regime",
    "scenarios",
    "screener",
    "settings",
    "sizing",
    "strategy_matrix",
    "symbols",
    "trades",
    "watchlists",
]
