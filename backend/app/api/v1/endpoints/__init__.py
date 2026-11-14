"""API v1 endpoint routers — aggregated by ``app.api.v1.router``.

Each module here must expose an ``APIRouter`` instance named ``router``.
Adding a new resource means: add the module to this file *and* register it
in ``app.api.v1.router``.
"""

from app.api.v1.endpoints import (
    alerts,
    auth,
    dashboard,
    gate,
    greeks,
    logs,
    market,
    picks,
    portfolio,
    regime,
    screener,
    settings,
    sizing,
    symbols,
    trades,
    watchlists,
)

__all__ = [
    "alerts",
    "auth",
    "dashboard",
    "gate",
    "greeks",
    "logs",
    "market",
    "picks",
    "portfolio",
    "regime",
    "screener",
    "settings",
    "sizing",
    "symbols",
    "trades",
    "watchlists",
]
