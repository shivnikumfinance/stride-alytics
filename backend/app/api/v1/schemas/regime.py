"""Regime detector request/response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RegimeResponse(BaseModel):
    symbol: str
    regime: Literal["bull", "bear", "ranging"]
    confidence: float = Field(ge=0, le=1)
    lookback_days: int
    price_return: float
    as_of: str
