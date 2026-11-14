"""Regime endpoints — GET /api/v1/regime/{symbol}."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.deps import Ctx, get_ctx
from app.api.middleware.auth import CurrentUser, get_current_user
from app.domain import regime_score as rs
from app.services import regime_service
from app.api.v1.schemas.regime import RegimeResponse
from app.services.regime import detect_regime
from app.utils.logger import get_logger
from app.utils.validators import normalize_symbol

# ``result.regime`` is a plain ``str`` upstream; coerce into the
# Literal the schema expects so mypy is satisfied.
_LITERAL_REGIMES = ("bull", "bear", "ranging")

router = APIRouter()
log = get_logger(__name__)


@router.get("/score")
async def regime_score(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    """0–100 regime score (DEFENSIVE / NORMAL / GROWTH) using your weights from Settings.

    If the live inputs cannot be fetched the last stored score is returned with
    ``source: "stored"``; if there is none, ``state`` is ``UNKNOWN`` (never a made-up value).
    """
    settings = await ctx.repo.get_settings(ctx.user_id)
    spy, vix = await run_in_threadpool(regime_service.get_inputs)
    mine = rs.compute_regime(spy, vix, settings["regime_weights"])

    # The shared history always uses the default weights, so it is comparable day to day.
    shared = rs.compute_regime(spy, vix)
    previous_state = await ctx.repo.save_regime(shared)
    if previous_state and previous_state != shared.state:
        await ctx.repo.log_signal(
            ctx.user_id,
            kind="regime",
            decision="info",
            message=f"Regime changed from {previous_state} to {shared.state}.",
            details={"from": previous_state, "to": shared.state, "score": shared.score},
        )

    if mine.score is not None:
        return {"success": True, "data": mine.to_dict()}
    stored = await ctx.repo.latest_regime()
    if stored is not None:
        return {"success": True, "data": {**stored, "source": "stored", "missing": mine.missing}}
    return {"success": True, "data": mine.to_dict()}


@router.get("/history")
async def regime_history(
    limit: int = Query(default=90, ge=1, le=365), ctx: Ctx = Depends(get_ctx)
) -> dict[str, Any]:
    """Stored daily regime scores, newest first (default weights)."""
    return {"success": True, "data": await ctx.repo.regime_history(limit)}


@router.get("/{symbol}", response_model=RegimeResponse)
def get_regime(  # plain def: detect_regime does blocking network I/O (runs in a thread)
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
        source="live" if result.source == "live" else "synthetic",
    )
