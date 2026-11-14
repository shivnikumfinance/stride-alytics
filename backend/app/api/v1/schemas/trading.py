"""Gate and sizing request models."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.api.v1.schemas.portfolio import Band, Layer


class GateCheckRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    trade_type: Literal["call", "put", "stock"] = "put"
    layer: Layer | None = None
    strike: float | None = Field(default=None, gt=0)
    expiry: date | None = None
    entry_date: date | None = None  # defaults to today


class SizingRequest(BaseModel):
    layer: Literal["base", "growth"]
    credit: float | None = Field(default=None, ge=0, description="Credit per share ($)")
    max_loss_per_contract: float | None = Field(default=None, ge=0, description="$ per contract")
    band: Band | None = None
    risk_pct: float | None = Field(default=None, gt=0, le=10, description="Override the setting")
