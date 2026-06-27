"""Portfolio & trade request/response models."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# --- Portfolios ---


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class PortfolioSummary(BaseModel):
    portfolio_id: str
    name: str
    total_trades: int
    open_trades: int
    closed_trades: int
    total_pnl: float
    win_rate: float
    winners: int
    losers: int


# --- Trades ---


class TradeCreate(BaseModel):
    portfolio_id: UUID
    symbol: str = Field(min_length=1, max_length=10)
    trade_type: Literal["call", "put", "stock"]
    direction: Literal["long", "short"]
    entry_price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    entry_date: date
    notes: str | None = Field(default=None, max_length=500)


class TradeClose(BaseModel):
    exit_price: float = Field(gt=0)
    exit_date: date


class TradeOut(BaseModel):
    trade_id: str
    symbol: str
    trade_type: Literal["call", "put", "stock"]
    direction: Literal["long", "short"]
    quantity: int
    entry_price: float
    exit_price: float | None
    entry_date: str
    exit_date: str | None
    pnl: float
    open: bool
