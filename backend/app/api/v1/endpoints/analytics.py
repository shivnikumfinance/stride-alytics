"""Performance analytics: how realised results compare with expectations (FR-920)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import Ctx, get_ctx
from app.domain.ev import calibration
from app.services.portfolio import calculate_pnl

router = APIRouter()


@router.get("/ev-calibration")
async def ev_calibration(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    """Win rate and average P&L of closed trades by layer.

    Entry EV is not stored on a trade yet, so ``avg_expected`` is empty until it is; the realised
    figures are real.
    """
    closed = await ctx.repo.closed_trades(ctx.user_id)
    rows = [{"layer": t.layer, "pnl": calculate_pnl(t), "expected": None} for t in closed]
    data = calibration(rows)
    data["note"] = (
        "Expected value at entry is not recorded on trades yet, so only realised results are shown."
    )
    return {"success": True, "data": data}
