"""Market regime detection — classifies the broad market as bull / bear / ranging.

Uses a deterministic synthetic price series in Phase 1 so the endpoint
contract is exercisable without a market-data vendor. Phase 2 will swap
``_load_history()`` for yfinance + a Supabase cache.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta

from app.utils.constants import REGIME_BEAR_THRESHOLD, REGIME_BULL_THRESHOLD
from app.utils.logger import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class RegimeResult:
    regime: str          # 'bull' | 'bear' | 'ranging'
    confidence: float    # 0..1
    lookback_days: int
    price_return: float  # decimal, e.g. 0.0342 = +3.42%
    as_of: str


def _load_history(symbol: str, lookback_days: int) -> list[float]:
    """Synthetic daily closes. Deterministic per (symbol, lookback)."""
    seed = (hash((symbol, lookback_days)) & 0xFFFFFFFF) / 1e9
    prices: list[float] = []
    price = 100.0 + 50.0 * math.sin(seed * 6.28)
    drift = 0.0006 * math.cos(seed * 12.0)
    for _ in range(lookback_days):
        # Simple deterministic walk
        price *= 1.0 + drift + 0.01 * math.sin(seed * 3.14)
        prices.append(round(price, 4))
    return prices


def detect_regime(symbol: str, lookback_days: int = 30) -> RegimeResult:
    """Classify the recent regime for ``symbol`` over the lookback window."""
    history = _load_history(symbol, lookback_days)
    if len(history) < 2:
        raise ValueError("not enough history to classify regime")

    start, end = history[0], history[-1]
    price_return = (end - start) / start if start else 0.0

    if price_return >= REGIME_BULL_THRESHOLD:
        regime = "bull"
    elif price_return <= REGIME_BEAR_THRESHOLD:
        regime = "bear"
    else:
        regime = "ranging"

    # Confidence scales with how far the return is from the neutral band
    magnitude = abs(price_return)
    confidence = round(min(1.0, magnitude / 0.10), 3)

    log.info(
        "regime.detect",
        symbol=symbol,
        regime=regime,
        confidence=confidence,
        price_return=round(price_return, 4),
    )

    return RegimeResult(
        regime=regime,
        confidence=confidence,
        lookback_days=lookback_days,
        price_return=round(price_return, 4),
        as_of=date.today().isoformat(),
    )
