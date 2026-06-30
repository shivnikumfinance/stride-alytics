"""Greeks calculator request/response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GreeksRequest(BaseModel):
    spot: float = Field(gt=0, description="Current underlying price")
    strike: float = Field(gt=0, description="Option strike price")
    time_to_expiry: float = Field(gt=0, le=10, description="Time to expiry in years (e.g. 30/365)")
    risk_free_rate: float = Field(default=0.05, ge=0, le=1, description="Annualized risk-free rate")
    volatility: float = Field(
        default=0.20, gt=0, le=5, description="Implied volatility as decimal (0.20 = 20%)"
    )
    option_type: Literal["call", "put"] = "call"


class GreeksResponse(BaseModel):
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    price_call: float
    price_put: float
    inputs: GreeksRequest
