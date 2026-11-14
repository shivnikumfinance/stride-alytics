"""API v1 endpoint routers — aggregated by ``app.api.v1.router``.

Each module here must expose an ``APIRouter`` instance named ``router``.
Adding a new resource means: add the module to this file *and* register it
in ``app.api.v1.router``.
"""

from app.api.v1.endpoints import (
    auth,
    gate,
    greeks,
    logs,
    market,
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
    "auth",
    "gate",
    "greeks",
    "logs",
    "market",
    "portfolio",
    "regime",
    "screener",
    "settings",
    "sizing",
    "symbols",
    "trades",
    "watchlists",
]
