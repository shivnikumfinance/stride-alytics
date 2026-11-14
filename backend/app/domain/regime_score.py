"""Market regime score, 0–100 (docs: FR-400–430, BR-100–104).

Three inputs, each turned into a 0–100 sub-score where **higher = friendlier to selling premium**:

* **trend**  — SPY vs its 50- and 200-day averages (50 pts above the 200-day, +30 above the
  50-day, +20 if the 50-day is above the 200-day).
* **vix**    — VIX level: 12 or lower scores 100, 40 or higher scores 0, linear in between.
* **iv_rank** — percentile of today's VIX within its last year (a market-wide stand-in for IV Rank):
  richer premium scores higher. It deliberately pulls against the VIX sub-score; the weights
  (default 40/30/30, tunable in Settings) decide the balance.

States: DEFENSIVE 0–40, NORMAL 40–70, GROWTH 70–100. If an input cannot be fetched it is left out
and the remaining weights are re-normalised; if nothing is available the state is UNKNOWN. No
placeholder data is ever substituted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

DEFENSIVE_BELOW = 40.0
GROWTH_AT = 70.0
VIX_BEST = 12.0  # sub-score 100 at or below this
VIX_WORST = 40.0  # sub-score 0 at or above this
MIN_IV_HISTORY = 100  # trading days needed for a meaningful percentile

DEFAULT_WEIGHTS: dict[str, float] = {"trend": 40.0, "vix": 30.0, "iv_rank": 30.0}

UNKNOWN = "UNKNOWN"


@dataclass
class RegimeScore:
    score: float | None
    state: str
    components: dict[str, float | None]
    weights: dict[str, float]
    missing: list[str] = field(default_factory=list)
    market_down: bool | None = None  # SPY below its 200-day average
    vix: float | None = None
    iv_rank: float | None = None
    as_of: str = ""
    source: str = "live"  # "live" | "stored" | "unavailable"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_row(self) -> dict[str, Any]:
        """Payload for the shared ``market_regime`` table (used by the scheduler)."""
        return {
            "as_of": self.as_of,
            "score": self.score,
            "state": self.state,
            "components": self.components,
            "weights": self.weights,
            "vix": self.vix,
            "iv_rank": self.iv_rank,
            "market_down": self.market_down,
            "source": self.source,
        }


def classify(score: float | None) -> str:
    """40 is NORMAL and 70 is GROWTH (the lower bound of each band is inclusive)."""
    if score is None:
        return UNKNOWN
    if score < DEFENSIVE_BELOW:
        return "DEFENSIVE"
    if score < GROWTH_AT:
        return "NORMAL"
    return "GROWTH"


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def trend_score(spy_closes: list[float] | None) -> tuple[float | None, bool | None]:
    """Return ``(sub_score, market_down)``; ``(None, None)`` if there is too little history."""
    if not spy_closes or len(spy_closes) < 200:
        return None, None
    last = spy_closes[-1]
    ma50 = _mean(spy_closes[-50:])
    ma200 = _mean(spy_closes[-200:])
    points = 0.0
    if last > ma200:
        points += 50
    if last > ma50:
        points += 30
    if ma50 > ma200:
        points += 20
    return points, last < ma200


def vix_score(vix: float | None) -> float | None:
    if vix is None:
        return None
    if vix <= VIX_BEST:
        return 100.0
    if vix >= VIX_WORST:
        return 0.0
    return 100.0 * (VIX_WORST - vix) / (VIX_WORST - VIX_BEST)


def iv_rank_from_history(vix_history: list[float] | None) -> float | None:
    """Percentile (0–100) of the latest VIX close within the history provided."""
    if not vix_history or len(vix_history) < MIN_IV_HISTORY:
        return None
    current = vix_history[-1]
    at_or_below = sum(1 for v in vix_history if v <= current)
    return 100.0 * at_or_below / len(vix_history)


def combine(
    components: dict[str, float | None], weights: dict[str, float]
) -> tuple[float | None, list[str]]:
    """Weighted average of the available components. Returns ``(score, missing_names)``."""
    missing = [k for k, v in components.items() if v is None]
    used = {k: weights.get(k, 0.0) for k, v in components.items() if v is not None}
    total = sum(used.values())
    if total <= 0:
        return None, missing
    score = sum(components[k] * w for k, w in used.items()) / total  # type: ignore[operator]
    return round(max(0.0, min(100.0, score)), 1), missing


def compute_regime(
    spy_closes: list[float] | None,
    vix_history: list[float] | None,
    weights: dict[str, float] | None = None,
    as_of: date | None = None,
    source: str = "live",
) -> RegimeScore:
    w = dict(DEFAULT_WEIGHTS if weights is None else weights)
    trend, market_down = trend_score(spy_closes)
    vix = vix_history[-1] if vix_history else None
    iv_rank = iv_rank_from_history(vix_history)
    components = {"trend": trend, "vix": vix_score(vix), "iv_rank": iv_rank}
    score, missing = combine(components, w)
    return RegimeScore(
        score=score,
        state=classify(score),
        components={k: None if v is None else round(v, 1) for k, v in components.items()},
        weights=w,
        missing=missing,
        market_down=market_down,
        vix=None if vix is None else round(vix, 2),
        iv_rank=None if iv_rank is None else round(iv_rank, 1),
        as_of=(as_of or date.today()).isoformat(),
        source=source if score is not None else "unavailable",
    )


def fetch_inputs() -> tuple[list[float] | None, list[float] | None]:
    """Fetch SPY (2y) and VIX (1y) daily closes from yfinance. ``None`` on any failure."""
    try:
        import yfinance as yf  # imported lazily so the pure functions need no network library
    except Exception:  # noqa: BLE001
        return None, None

    def closes(symbol: str, period: str) -> list[float] | None:
        try:
            hist = yf.Ticker(symbol).history(period=period)
            if hist.empty:
                return None
            return [float(c) for c in hist["Close"].dropna().tolist()]
        except Exception:  # noqa: BLE001
            return None

    return closes("SPY", "2y"), closes("^VIX", "1y")


def compute_live(weights: dict[str, float] | None = None) -> RegimeScore:
    spy, vix_hist = fetch_inputs()
    return compute_regime(spy, vix_hist, weights)
