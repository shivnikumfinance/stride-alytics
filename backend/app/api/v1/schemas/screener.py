"""Screener request/response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ScreenerQuery(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    min_strike: float | None = Field(default=None, gt=0)
    max_strike: float | None = Field(default=None, gt=0)
    expiry_days_min: int = Field(default=0, ge=0, le=365)
    expiry_days_max: int = Field(default=60, ge=0, le=730)
    option_type: Literal["call", "put"] | None = None
    min_volume: int = Field(default=0, ge=0)
    min_open_interest: int = Field(default=0, ge=0)
    max_iv: float | None = Field(default=None, gt=0, le=5)
    min_iv: float | None = Field(default=None, gt=0, le=5)
    limit: int = Field(default=50, ge=1, le=500)


class ScreenerResultRow(BaseModel):
    symbol: str
    strike: float
    expiry: str
    option_type: Literal["call", "put"]
    bid: float
    ask: float
    last_price: float
    implied_vol: float
    delta: float
    gamma: float
    theta: float
    vega: float
    open_interest: int
    volume: int


class ScreenerResponse(BaseModel):
    success: bool = True
    symbol: str
    spot: float
    count: int
    results: list[ScreenerResultRow]
