"""Greeks calculator endpoint — POST /api/v1/greeks/calculate."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.greeks import GreeksRequest, GreeksResponse
from app.services.greeks import calculate_greeks
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/calculate", response_model=GreeksResponse)
async def calculate(
    payload: GreeksRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> GreeksResponse:
    """Return Black-Scholes Greeks for the supplied option inputs."""
    log.info(
        "greeks.calculate",
        user_id=current_user.user_id,
        spot=payload.spot,
        strike=payload.strike,
        option_type=payload.option_type,
    )
    greeks = calculate_greeks(
        spot=payload.spot,
        strike=payload.strike,
        time_to_expiry=payload.time_to_expiry,
        risk_free_rate=payload.risk_free_rate,
        volatility=payload.volatility,
        option_type=payload.option_type,
    )
    return GreeksResponse(
        delta=greeks.delta,
        gamma=greeks.gamma,
        theta=greeks.theta,
        vega=greeks.vega,
        rho=greeks.rho,
        price_call=greeks.price_call,
        price_put=greeks.price_put,
        inputs=payload,
    )
