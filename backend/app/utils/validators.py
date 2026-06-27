"""Lightweight validators shared across services and endpoints."""

from __future__ import annotations

from typing import Literal

OptionType = Literal["call", "put"]
TradeType = Literal["call", "put", "stock"]
Direction = Literal["long", "short"]
SubscriptionPlan = Literal["free", "pro"]


def is_positive(value: float) -> bool:
    return value > 0


def is_valid_iv(iv: float) -> bool:
    """Implied volatility must be between 0.1% and 500%."""
    return 0.001 <= iv <= 5.0


def normalize_symbol(symbol: str) -> str:
    """Upper-case, strip whitespace from a ticker symbol."""
    return symbol.strip().upper()


def validate_option_type(value: str) -> OptionType:
    value = value.strip().lower()
    if value not in {"call", "put"}:
        raise ValueError(f"option_type must be 'call' or 'put', got: {value!r}")
    return value  # type: ignore[return-value]
