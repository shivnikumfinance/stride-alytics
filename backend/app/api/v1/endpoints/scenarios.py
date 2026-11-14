"""Scenario / stress simulation and saved scenarios (FR-530)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.api.deps import Ctx, get_ctx
from app.services.position_data import PositionDataProvider, get_position_data_provider
from app.services.risk_service import positions_with_market, run_user_scenario

router = APIRouter()


class ScenarioParams(BaseModel):
    spot_pct: float = Field(default=0.0, ge=-90, le=200, description="Underlying move, in %")
    iv_shift: float = Field(default=0.0, ge=-0.5, le=1.0, description="Implied-vol change, points")
    days_forward: int = Field(default=0, ge=0, le=365, description="Days that pass")


class SaveScenario(ScenarioParams):
    name: str = Field(min_length=1, max_length=80)


@router.post("/run")
async def run(
    body: ScenarioParams,
    ctx: Ctx = Depends(get_ctx),
    provider: PositionDataProvider = Depends(get_position_data_provider),
) -> dict[str, Any]:
    """Reprice the open positions under the shock. Writes nothing."""
    positions = await positions_with_market(ctx, provider)
    return {"success": True, "data": run_user_scenario(positions, **body.model_dump())}


@router.get("")
async def list_scenarios(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    return {"success": True, "data": await ctx.repo.list_scenarios(ctx.user_id)}


@router.post("", status_code=status.HTTP_201_CREATED)
async def save_scenario(body: SaveScenario, ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    params = body.model_dump(exclude={"name"})
    try:
        saved = await ctx.repo.save_scenario(ctx.user_id, body.name.strip(), params)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"success": True, "data": saved}


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(scenario_id: UUID, ctx: Ctx = Depends(get_ctx)) -> Response:
    try:
        await ctx.repo.delete_scenario(ctx.user_id, scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Scenario not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
