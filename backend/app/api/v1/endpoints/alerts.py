"""Exit / risk alerts for open positions and their acknowledgement (BR-095–098, FR-1210)."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import Ctx, get_ctx
from app.domain.alerts import rank, summarize
from app.services.position_data import PositionDataProvider, get_position_data_provider
from app.services.positions import annotate_acks, evaluate_open_positions
from app.services.trading import load_account

router = APIRouter()


class AckRequest(BaseModel):
    trade_id: UUID
    code: str = Field(min_length=1, max_length=32)
    note: str | None = Field(default=None, max_length=500)


@router.get("/exits")
async def exit_alerts(
    min_severity: Literal["normal", "watch", "warning", "critical"] = "watch",
    ctx: Ctx = Depends(get_ctx),
    provider: PositionDataProvider = Depends(get_position_data_provider),
) -> dict[str, Any]:
    """Open positions rated Normal / Watch / Warning / Critical, most urgent first.

    ``min_severity=normal`` returns every open position (used by Active Holdings).
    """
    account = await load_account(ctx)
    alerts = await evaluate_open_positions(ctx, provider, account.regime.score)
    dicts, unacknowledged = await annotate_acks(ctx, alerts)
    shown = [d for d in dicts if rank(d["severity"]) >= rank(min_severity)]
    return {
        "success": True,
        "data": {
            "alerts": shown,
            "summary": summarize(alerts),
            "unacknowledged_critical": unacknowledged,
            "open_positions": len(alerts),
            "regime": {"score": account.regime.score, "state": account.regime.state},
        },
    }


@router.post("/ack")
async def acknowledge(
    payload: AckRequest,
    ctx: Ctx = Depends(get_ctx),
    provider: PositionDataProvider = Depends(get_position_data_provider),
) -> dict[str, Any]:
    """Acknowledge an alert that is firing right now. Critical alerts require this (BR-096)."""
    account = await load_account(ctx)
    alerts = await evaluate_open_positions(ctx, provider, account.regime.score)
    trade_id = str(payload.trade_id)
    severity = next(
        (
            r.severity
            for a in alerts
            if a.trade_id == trade_id
            for r in a.reasons
            if r.code == payload.code and rank(r.severity) >= 2
        ),
        None,
    )
    if severity is None:
        raise HTTPException(status_code=404, detail="That alert is not active on an open position")
    try:
        data = await ctx.repo.ack_alert(
            ctx.user_id, payload.trade_id, payload.code, severity, payload.note
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Trade not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"success": True, "data": data}


@router.get("/acks")
async def acknowledgement_history(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: Ctx = Depends(get_ctx),
) -> dict[str, Any]:
    """History of acknowledgements (the alert timeline, FR-1210)."""
    rows, total = await ctx.repo.list_acks(ctx.user_id, limit=limit, offset=offset)
    return {"success": True, "data": rows, "total": total, "limit": limit, "offset": offset}
