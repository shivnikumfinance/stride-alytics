"""Pydantic v1 schemas (request/response models).

One file per backend resource. To add a new resource, create
``app/api/v1/schemas/<name>.py`` and re‑export its models below.
Frontend mirror lives in ``frontend/src/types/<name>.ts``.
"""

from app.api.v1.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
)
from app.api.v1.schemas.greeks import GreeksRequest, GreeksResponse
from app.api.v1.schemas.market import TickerData, TickerEnvelope
from app.api.v1.schemas.screener import (
    ScreenerQuery,
    ScreenerResponse,
    ScreenerResultRow,
)
from app.api.v1.schemas.regime import RegimeResponse
from app.api.v1.schemas.portfolio import (
    PortfolioCreate,
    PortfolioSummary,
    TradeClose,
    TradeCreate,
    TradeOut,
)

__all__ = [
    "LoginRequest",
    "SignupRequest",
    "TokenResponse",
    "GreeksRequest",
    "GreeksResponse",
    "TickerData",
    "TickerEnvelope",
    "ScreenerQuery",
    "ScreenerResponse",
    "ScreenerResultRow",
    "RegimeResponse",
    "PortfolioCreate",
    "PortfolioSummary",
    "TradeCreate",
    "TradeClose",
    "TradeOut",
]
