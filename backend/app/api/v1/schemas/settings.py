"""Watchlist, settings and log request models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

BANDS = ("A", "B", "C", "D", "E")
REGIME_WEIGHT_KEYS = ("trend", "vix", "iv_rank")


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    symbols: list[str] = Field(default_factory=list, max_length=200)


class SymbolAdd(BaseModel):
    symbol: str = Field(min_length=1, max_length=16)


class SymbolFlagUpdate(BaseModel):
    news_flag: bool
    note: str | None = Field(default=None, max_length=500)


class SettingsUpdate(BaseModel):
    """Partial update: only fields that are sent are changed (FR-110, FR-130, FR-140)."""

    notify_weekly_picks: bool | None = None
    notify_market_regime: bool | None = None
    default_symbol: str | None = Field(default=None, min_length=1, max_length=16)
    theme: Literal["light", "dark", "system"] | None = None
    screener_preset: dict | None = None
    account_size: float | None = Field(default=None, ge=0, le=1e10)
    base_risk_pct: float | None = Field(default=None, gt=0, le=10)
    growth_risk_pct: float | None = Field(default=None, gt=0, le=10)
    min_equity: float | None = Field(default=None, ge=0, le=1e10)
    band_caps: dict[str, float] | None = None
    regime_weights: dict[str, float] | None = None
    widget_toggles: dict[str, bool] | None = None
    enforce_gate: bool | None = None

    @field_validator("band_caps")
    @classmethod
    def _check_band_caps(cls, v: dict[str, float] | None) -> dict[str, float] | None:
        if v is None:
            return v
        if set(v) != set(BANDS):
            raise ValueError(f"band_caps must have exactly the keys {list(BANDS)}")
        if any(not 0 <= cap <= 100 for cap in v.values()):
            raise ValueError("each band cap must be between 0 and 100 (percent)")
        return v

    @field_validator("regime_weights")
    @classmethod
    def _check_weights(cls, v: dict[str, float] | None) -> dict[str, float] | None:
        if v is None:
            return v
        if set(v) != set(REGIME_WEIGHT_KEYS):
            raise ValueError(
                f"regime_weights must have exactly the keys {list(REGIME_WEIGHT_KEYS)}"
            )
        if any(w < 0 for w in v.values()) or sum(v.values()) <= 0:
            raise ValueError("regime weights must be non-negative and not all zero")
        return v
