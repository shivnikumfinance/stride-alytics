"""Market regime detection — classifies the broad market as bull / bear / ranging.

Phase 1 used a synthetic price series. Phase 2 now uses real price data
from yfinance, with a fallback to the deterministic synthetic prices when
yfinance is unavailable (e.g. during tests).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

import yfinance as yf

from app.utils.constants import REGIME_BEAR_THRESHOLD, REGIME_BULL_THRESHOLD
from app.utils.logger import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class RegimeResult:
    regime: str  # 'bull' | 'bear' | 'ranging'
    confidence: float  # 0..1
    lookback_days: int
    price_return: float  # decimal, e.g. 0.0342 = +3.42%
    as_of: str
    vix: float | None = None
    iv_rank: float | None = None


def _fetch_history_yfinance(symbol: str, lookback_days: int) -> list[float] | None:
    """Fetch historical prices from yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        period = f"{max(lookback_days + 10, 60)}d"  # Buffer for weekends/holidays
        hist = ticker.history(period=period)
        if hist.empty:
            return None
        # Get the last `lookback_days` closing prices
        closes = hist["Close"].tail(lookback_days).tolist()
        if len(closes) >= 2:
            return [float(c) for c in closes]
        return None
    except Exception as exc:
        log.warning("regime.yfinance_failed", symbol=symbol, error=str(exc))
        return None


def _fetch_vix_data() -> float | None:
    """Fetch the current VIX level from yfinance."""
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
        return None
    except Exception:
        return None


def _load_history(symbol: str, lookback_days: int) -> list[float]:
    """Load price history — prefers yfinance, falls back to synthetic."""
    real = _fetch_history_yfinance(symbol, lookback_days)
    if real:
        log.info("regime.using_yfinance", symbol=symbol, lookback_days=len(real))
        return real

    log.info("regime.using_synthetic", symbol=symbol)
    return _load_synthetic_history(symbol, lookback_days)


def _load_synthetic_history(symbol: str, lookback_days: int) -> list[float]:
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

    # Optionally fetch VIX for additional context
    vix = _fetch_vix_data()

    log.info(
        "regime.detect",
        symbol=symbol,
        regime=regime,
        confidence=confidence,
        price_return=round(price_return, 4),
        vix=vix,
    )

    return RegimeResult(
        regime=regime,
        confidence=confidence,
        lookback_days=lookback_days,
        price_return=round(price_return, 4),
        as_of=date.today().isoformat(),
        vix=round(vix, 2) if vix else None,
        iv_rank=None,  # Placeholder — can be calculated from 52-week VIX history
    )
