"""Cached access to the regime score inputs (SPY and VIX history).

The fetch is slow and rate-limited, so the raw inputs are cached for ``REGIME_CACHE_TTL_SECONDS``
and the score is recomputed from them per request (it depends on the user's weights). A failed
fetch is never cached, so the next request retries.
"""

from __future__ import annotations

import threading
import time

from app.domain import regime_score as rs
from app.utils.constants import REGIME_CACHE_TTL_SECONDS
from app.utils.logger import get_logger

log = get_logger(__name__)

_lock = threading.Lock()
_cache: dict[str, object] = {"at": 0.0, "spy": None, "vix": None}


def clear_cache() -> None:
    with _lock:
        _cache.update(at=0.0, spy=None, vix=None)


def get_inputs() -> tuple[list[float] | None, list[float] | None]:
    """SPY and VIX closes, from cache when fresh. Blocking (network): call from a thread."""
    with _lock:
        fresh = time.monotonic() - float(_cache["at"]) < REGIME_CACHE_TTL_SECONDS
        if fresh and (_cache["spy"] is not None or _cache["vix"] is not None):
            return _cache["spy"], _cache["vix"]  # type: ignore[return-value]

    spy, vix = rs.fetch_inputs()
    if spy is None and vix is None:
        log.warning("regime.inputs_unavailable")
        return None, None
    with _lock:
        _cache.update(at=time.monotonic(), spy=spy, vix=vix)
    return spy, vix


def current_regime(weights: dict[str, float] | None = None) -> rs.RegimeScore:
    """The live regime score with the given weights (default weights if None)."""
    spy, vix = get_inputs()
    return rs.compute_regime(spy, vix, weights)
