"""Watchlist endpoints (FR-120, FR-200–230)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import Ctx, get_ctx, to_csv
from app.api.v1.schemas.settings import SymbolAdd, WatchlistCreate

router = APIRouter()


def _not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Watchlist not found")


@router.get("")
async def list_watchlists(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    return {"success": True, "data": await ctx.repo.list_watchlists(ctx.user_id)}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_watchlist(payload: WatchlistCreate, ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    try:
        data = await ctx.repo.create_watchlist(ctx.user_id, payload.name, payload.symbols)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return {"success": True, "data": data}


@router.get("/{watchlist_id}")
async def get_watchlist(watchlist_id: UUID, ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    try:
        return {"success": True, "data": await ctx.repo.get_watchlist(ctx.user_id, watchlist_id)}
    except KeyError as exc:
        raise _not_found() from exc


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(watchlist_id: UUID, ctx: Ctx = Depends(get_ctx)) -> Response:
    try:
        await ctx.repo.delete_watchlist(ctx.user_id, watchlist_id)
    except KeyError as exc:
        raise _not_found() from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{watchlist_id}/symbols")
async def add_symbol(
    watchlist_id: UUID, payload: SymbolAdd, ctx: Ctx = Depends(get_ctx)
) -> dict[str, Any]:
    try:
        data = await ctx.repo.add_symbol(ctx.user_id, watchlist_id, payload.symbol)
    except KeyError as exc:
        raise _not_found() from exc
    return {"success": True, "data": data}


@router.delete("/{watchlist_id}/symbols/{symbol}")
async def remove_symbol(
    watchlist_id: UUID, symbol: str, ctx: Ctx = Depends(get_ctx)
) -> dict[str, Any]:
    try:
        data = await ctx.repo.remove_symbol(ctx.user_id, watchlist_id, symbol)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Watchlist or symbol not found") from exc
    return {"success": True, "data": data}


@router.get("/{watchlist_id}/export.csv")
async def export_watchlist(watchlist_id: UUID, ctx: Ctx = Depends(get_ctx)) -> Response:
    try:
        wl = await ctx.repo.get_watchlist(ctx.user_id, watchlist_id)
    except KeyError as exc:
        raise _not_found() from exc
    flags = await ctx.repo.get_symbol_flags(ctx.user_id, wl["symbols"])
    rows = [
        {"symbol": s, "news_flag": flags.get(s, {}).get("news_flag", False)} for s in wl["symbols"]
    ]
    return Response(
        content=to_csv(["symbol", "news_flag"], rows),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="watchlist.csv"'},
    )
