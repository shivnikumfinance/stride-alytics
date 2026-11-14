"""Read-only access to the append-only signal and audit logs (FR-700–730)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import Ctx, get_ctx

router = APIRouter()


@router.get("/signals")
async def list_signals(
    start: datetime | None = None,
    end: datetime | None = None,
    symbol: str | None = Query(default=None, max_length=16),
    rule_id: str | None = Query(default=None, max_length=16),
    decision: str | None = Query(default=None, pattern="^(allowed|blocked|info)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: Ctx = Depends(get_ctx),
) -> dict[str, Any]:
    """Rule/gate decisions, including blocked signals."""
    rows, total = await ctx.repo.list_signals(
        ctx.user_id,
        start=start,
        end=end,
        symbol=symbol,
        rule_id=rule_id,
        decision=decision,
        limit=limit,
        offset=offset,
    )
    return {"success": True, "data": rows, "total": total, "limit": limit, "offset": offset}


@router.get("/audit")
async def list_audit(
    start: datetime | None = None,
    end: datetime | None = None,
    entity: str | None = Query(default=None, max_length=32),
    action: str | None = Query(default=None, max_length=32),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: Ctx = Depends(get_ctx),
) -> dict[str, Any]:
    """Changes to trades, portfolios, watchlists and settings."""
    rows, total = await ctx.repo.list_audit(
        ctx.user_id,
        start=start,
        end=end,
        entity=entity,
        action=action,
        limit=limit,
        offset=offset,
    )
    return {"success": True, "data": rows, "total": total, "limit": limit, "offset": offset}
