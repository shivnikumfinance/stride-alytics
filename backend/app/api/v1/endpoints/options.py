"""Option chain for the chain page (FR-300–320)."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from app.api.middleware.auth import CurrentUser, get_current_user
from app.services.screener import ChainProvider, get_chain_provider
from app.utils.validators import normalize_symbol

router = APIRouter()


def _side(row: dict[str, Any]) -> dict[str, Any]:
    delta = row.get("delta")
    return {
        "bid": row["bid"],
        "ask": row["ask"],
        "last": row["last_price"],
        "iv": row["implied_vol"],
        "delta": delta,
        "gamma": row.get("gamma"),
        "theta": row.get("theta"),
        "vega": row.get("vega"),
        "open_interest": row["open_interest"],
        "volume": row["volume"],
        # Probability a short option expires worthless (delta approximation, FR-300).
        "pop_short": None if delta is None else round(1 - min(abs(delta), 1.0), 4),
    }


@router.get("/chain")
async def chain(
    symbol: str = Query(min_length=1, max_length=12),
    expiry: date | None = Query(default=None, description="Default: the nearest expiry"),
    _user: CurrentUser = Depends(get_current_user),
    provider: ChainProvider = Depends(get_chain_provider),
) -> dict[str, Any]:
    """Calls and puts per strike for one expiry. ``source`` is ``live`` or ``synthetic``."""
    sym = normalize_symbol(symbol)
    spot, rows, source = await run_in_threadpool(provider, sym)
    if not rows:
        raise HTTPException(status_code=404, detail=f"No option chain found for {sym}")

    expiries = sorted({r["expiry"] for r in rows})
    chosen = expiry.isoformat() if expiry else expiries[0]
    if chosen not in expiries:
        raise HTTPException(status_code=404, detail=f"No chain for {sym} expiring {chosen}")

    strikes: dict[float, dict[str, Any]] = {}
    for r in rows:
        if r["expiry"] != chosen:
            continue
        slot = strikes.setdefault(r["strike"], {"strike": r["strike"], "call": None, "put": None})
        slot[r["option_type"]] = _side(r)

    return {
        "success": True,
        "data": {
            "symbol": sym,
            "spot": spot,
            "source": source,
            "expiry": chosen,
            "dte": (date.fromisoformat(chosen) - date.today()).days,
            "expiries": expiries,
            "strikes": [strikes[k] for k in sorted(strikes)],
        },
    }
