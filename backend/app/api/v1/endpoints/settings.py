"""Settings endpoints (FR-100–140) and first-login disclaimer acceptance."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import Ctx, get_ctx
from app.api.v1.schemas.settings import SettingsUpdate
from app.repositories.sql import InvalidInput

router = APIRouter()


@router.get("")
async def get_settings(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    return {"success": True, "data": await ctx.repo.get_settings(ctx.user_id)}


@router.put("")
async def update_settings(payload: SettingsUpdate, ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    """Partial update: only the fields that are sent change. Changes are audit-logged."""
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    try:
        data = await ctx.repo.update_settings(ctx.user_id, changes)
    except InvalidInput as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"success": True, "data": data}


@router.post("/disclaimer")
async def accept_disclaimer(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    """Record that the user accepted the not-financial-advice disclaimer."""
    return {"success": True, "data": await ctx.repo.accept_disclaimer(ctx.user_id)}
