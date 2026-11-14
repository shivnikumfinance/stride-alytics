"""Layer allocation by regime (BR-023, BR-035–037).

DEFENSIVE 80/20, NORMAL 60/40, GROWTH 40/60 (Base/Growth). The Growth layer is locked in a
DEFENSIVE regime, and also when the regime is UNKNOWN (fail-safe).
"""

from __future__ import annotations

LAYER_SPLIT: dict[str, tuple[int, int]] = {
    "DEFENSIVE": (80, 20),
    "NORMAL": (60, 40),
    "GROWTH": (40, 60),
}


def layer_split(state: str) -> dict[str, int]:
    """Target percent of capital per layer. UNKNOWN is treated as DEFENSIVE."""
    base, growth = LAYER_SPLIT.get(state, LAYER_SPLIT["DEFENSIVE"])
    return {"base": base, "growth": growth}


def growth_locked(state: str) -> bool:
    return state not in ("NORMAL", "GROWTH")
