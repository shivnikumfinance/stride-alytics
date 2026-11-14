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


class PortfolioUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
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

Layer = Literal["base", "growth"]
Band = Literal["A", "B", "C", "D", "E"]


class TradeCreate(BaseModel):
    portfolio_id: UUID
    symbol: str = Field(min_length=1, max_length=10)
    trade_type: Literal["call", "put", "stock"]
    direction: Literal["long", "short"]
    entry_price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    entry_date: date
    notes: str | None = Field(default=None, max_length=500)
    # Optional strategy detail (used for DTE, Greeks, risk and band caps)
    strike: float | None = Field(default=None, gt=0)
    expiry: date | None = None
    strategy: str | None = Field(default=None, max_length=64)
    layer: Layer | None = None
    band: Band | None = None
    risk_amount: float | None = Field(default=None, ge=0)
    credit: float | None = Field(default=None, ge=0)


class TradeClose(BaseModel):
    exit_price: float = Field(gt=0)
    exit_date: date


class TradeNotes(BaseModel):
    notes: str | None = Field(default=None, max_length=500)


class TradeOut(BaseModel):
    trade_id: str
    portfolio_id: str | None = None
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
    notes: str | None = None
    strike: float | None = None
    expiry: str | None = None
    strategy: str | None = None
    layer: Layer | None = None
    band: Band | None = None
    risk_amount: float | None = None
    credit: float | None = None


class TradePage(BaseModel):
    success: bool = True
    data: list[TradeOut]
    total: int
    limit: int
    offset: int
