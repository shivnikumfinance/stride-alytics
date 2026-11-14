"""Position sizing endpoint (FR-600–670)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import Ctx, get_ctx
from app.api.v1.schemas.trading import SizingRequest
from app.domain.allocation import layer_split
from app.domain.sizing import calculate_sizing
from app.services.trading import load_account

router = APIRouter()


@router.post("/calculate")
async def calculate(payload: SizingRequest, ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    """Quantity and risk for a candidate trade, using your settings, the regime and band usage."""
    account = await load_account(ctx)
    s = account.settings
    risk_pct = payload.risk_pct or (
        s["base_risk_pct"] if payload.layer == "base" else s["growth_risk_pct"]
    )
    exposure = await ctx.repo.open_band_exposure(ctx.user_id)
    result = calculate_sizing(
        account_size=s["account_size"],
        layer=payload.layer,
        risk_pct=risk_pct,
        regime_state=account.regime.state,
        credit=payload.credit,
        max_loss_per_contract=payload.max_loss_per_contract,
        band=payload.band,
        band_caps=s["band_caps"],
        band_exposure_dollars=exposure.get(payload.band, 0.0) if payload.band else 0.0,
    )
    return {
        "success": True,
        "data": {
            **result.to_dict(),
            "account_size": s["account_size"],
            "regime_state": account.regime.state,
            "layer_split": layer_split(account.regime.state),
        },
    }
