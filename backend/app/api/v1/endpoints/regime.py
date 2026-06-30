"""Regime endpoints — GET /api/v1/regime/{symbol}."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.regime import RegimeResponse
from app.services.regime import detect_regime
from app.utils.logger import get_logger
from app.utils.validators import normalize_symbol

# ``result.regime`` is a plain ``str`` upstream; coerce into the
# Literal the schema expects so mypy is satisfied.
_LITERAL_REGIMES = ("bull", "bear", "ranging")

router = APIRouter()
log = get_logger(__name__)


@router.get("/{symbol}", response_model=RegimeResponse)
async def get_regime(
    symbol: str,
    lookback_days: int = 30,
    current_user: CurrentUser = Depends(get_current_user),
) -> RegimeResponse:
    """Classify the broad market regime for ``symbol`` over the lookback window."""
    lookback_days = max(5, min(lookback_days, 252))
    result = detect_regime(normalize_symbol(symbol), lookback_days=lookback_days)

    log.info(
        "regime.served",
        user_id=current_user.user_id,
        symbol=symbol,
        regime=result.regime,
    )

    regime_value = result.regime if result.regime in _LITERAL_REGIMES else "ranging"
    return RegimeResponse(
        symbol=normalize_symbol(symbol),
        regime=regime_value,  # type: ignore[arg-type]
        confidence=result.confidence,
        lookback_days=result.lookback_days,
        price_return=result.price_return,
        as_of=result.as_of,
    )
