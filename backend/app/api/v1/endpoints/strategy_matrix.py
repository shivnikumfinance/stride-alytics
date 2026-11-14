"""Strategy Design Matrix (BR-090–094, FR-1100–1160)."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.deps import Ctx, get_ctx
from app.domain.strategy_matrix import build_matrix
from app.services.position_data import PositionDataProvider, get_position_data_provider
from app.services.trading import load_account, master_gate

router = APIRouter()


@router.get("")
async def strategy_matrix(
    layer: Literal["base", "growth"] | None = Query(default=None),
    band: Literal["A", "B", "C", "D", "E"] | None = Query(default=None),
    ctx: Ctx = Depends(get_ctx),
    positions: PositionDataProvider = Depends(get_position_data_provider),
) -> dict[str, Any]:
    """Strategies x regimes, with the current regime and gate status overlaid."""
    account = await load_account(ctx, positions)
    gate = master_gate(account)
    state = account.regime.state
    current = state if state in ("DEFENSIVE", "NORMAL", "GROWTH") else None
    data = build_matrix(current, gate_clear=gate.clear, layer=layer, band=band)
    data["gate_reasons"] = [asdict(r) for r in gate.reasons]
    data["regime_score"] = account.regime.score
    return {"success": True, "data": data}
