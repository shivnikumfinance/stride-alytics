"""Manual per-symbol flags — the NewsFlag that feeds DNT rule BR-021."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.deps import Ctx, get_ctx
from app.api.v1.schemas.settings import SymbolFlagUpdate
from app.utils.validators import normalize_symbol

router = APIRouter()


@router.get("/flags")
async def list_flags(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    return {"success": True, "data": await ctx.repo.get_symbol_flags(ctx.user_id)}


@router.put("/{symbol}/flag")
async def set_flag(
    payload: SymbolFlagUpdate,
    symbol: str = Path(min_length=1, max_length=16),
    ctx: Ctx = Depends(get_ctx),
) -> dict[str, Any]:
    """Set or clear the news flag. While set, new trades in the symbol are blocked (BR-021)."""
    sym = normalize_symbol(symbol)
    if not sym.replace(".", "").replace("-", "").isalnum():
        raise HTTPException(status_code=422, detail="Invalid symbol")
    data = await ctx.repo.set_symbol_flag(ctx.user_id, sym, payload.news_flag, payload.note)
    return {"success": True, "data": data}
