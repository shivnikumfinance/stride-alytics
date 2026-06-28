"""Market data Pydantic schemas — request/response models for ``/api/v1/market``.

Mirrored on the frontend by ``frontend/src/types/market.ts``.
"""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class TickerData(BaseModel):
    """Single ticker snapshot returned by Yahoo Finance (proxy)."""

    symbol: str = Field(..., description="Ticker symbol, e.g. SPY")
    price: str = Field(..., description="Last regular‑market price, string‑formatted for client convenience")
    change: str = Field(..., description="Regular‑market price change, string‑formatted")
    changePercent: str = Field(..., description="Regular‑market percent change, string‑formatted")


class TickerEnvelope(BaseModel):
    """Standard success envelope: ``{ success: true, data: { SYM: TickerData, ... } }``."""

    success: bool = True
    data: Dict[str, TickerData]
