"""Do-Not-Trade gate endpoints (BR-010–021)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import Ctx, get_ctx
from app.api.v1.schemas.trading import GateCheckRequest
from app.domain.allocation import growth_locked, layer_split
from app.services.symbol_data import SymbolDataProvider, get_symbol_data_provider
from app.services.trading import entry_gate, load_account, master_gate
from app.utils.validators import normalize_symbol

router = APIRouter()

# Entries dated before this many days ago are treated as record-keeping and not gated. One day of
# slack covers users whose local date is behind the server's (UTC) date.
BACKDATE_GRACE_DAYS = 1


def is_backdated(entry_date: date) -> bool:
    return entry_date < date.today() - timedelta(days=BACKDATE_GRACE_DAYS)


@router.get("")
async def get_master_gate(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    """Account/market-level gate: CLEAR TO TRADE or BLOCKED, with every reason."""
    account = await load_account(ctx)
    result = master_gate(account)
    state = account.regime.state
    return {
        "success": True,
        "data": {
            **result.to_dict(),
            "status": "CLEAR TO TRADE" if result.clear else "BLOCKED",
            "regime": account.regime.to_dict(),
            "equity": account.equity,
            "min_equity": account.settings["min_equity"],
            "enforce_gate": account.settings["enforce_gate"],
            "layer_split": layer_split(state),
            "growth_locked": growth_locked(state),
        },
    }


@router.post("/check")
async def check_entry(
    payload: GateCheckRequest,
    ctx: Ctx = Depends(get_ctx),
    provider: SymbolDataProvider = Depends(get_symbol_data_provider),
) -> dict[str, Any]:
    """Dry run of the full entry gate for one candidate trade. Does not write to the logs."""
    entry_date = payload.entry_date or date.today()
    if is_backdated(entry_date):
        return {
            "success": True,
            "data": {
                "clear": True,
                "skipped": True,
                "status": "NOT GATED",
                "message": "Back-dated entries are record-keeping and are not gated.",
                "reasons": [],
                "checked": [],
                "not_evaluated": [],
            },
        }
    account = await load_account(ctx)
    result = await entry_gate(
        ctx,
        account,
        provider,
        symbol=normalize_symbol(payload.symbol),
        trade_type=payload.trade_type,
        layer=payload.layer,
        strike=payload.strike,
        expiry=payload.expiry,
    )
    return {
        "success": True,
        "data": {
            **result.to_dict(),
            "skipped": False,
            "status": "CLEAR TO TRADE" if result.clear else "BLOCKED",
            "regime_state": account.regime.state,
        },
    }
