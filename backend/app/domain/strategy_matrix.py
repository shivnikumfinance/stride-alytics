"""Strategy Design Matrix (docs: BR-090–094, FR-1100–1160).

Rows are strategies, columns are regime states. Each cell says whether the strategy is Available,
Limited or Blocked in that regime, which layers (Base/Growth) and capital bands (A-E) suit it, and
the current gate status. The suitability table is a documented default (a design judgement, not a
market forecast); the gate overlay is live.
"""

from __future__ import annotations

from typing import Any

REGIMES = ("DEFENSIVE", "NORMAL", "GROWTH")
AVAILABLE, LIMITED, BLOCKED = "available", "limited", "blocked"

# strategy -> (description, {regime: (availability, layers, bands, note)})
_STRATEGIES: dict[str, tuple[str, dict[str, tuple[str, tuple[str, ...], tuple[str, ...], str]]]] = {
    "Iron Condor": (
        "Short call and put spreads around the price; profits if it stays in a range.",
        {
            "DEFENSIVE": (LIMITED, ("base",), ("A", "B"), "Wide wings only; halved size."),
            "NORMAL": (AVAILABLE, ("base", "growth"), ("A", "B", "C"), "Core range strategy."),
            "GROWTH": (LIMITED, ("base",), ("B", "C"), "Trends can run through the range."),
        },
    ),
    "Put Credit Spread": (
        "Sell a put, buy a lower put; profits if the price stays above the short strike.",
        {
            "DEFENSIVE": (LIMITED, ("base",), ("A",), "Far out of the money only."),
            "NORMAL": (AVAILABLE, ("base", "growth"), ("A", "B", "C"), "Core income strategy."),
            "GROWTH": (AVAILABLE, ("base", "growth"), ("B", "C", "D"), "Bullish tilt suits it."),
        },
    ),
    "Call Credit Spread": (
        "Sell a call, buy a higher call; profits if the price stays below the short strike.",
        {
            "DEFENSIVE": (AVAILABLE, ("base",), ("A", "B"), "Bearish tilt suits it."),
            "NORMAL": (AVAILABLE, ("base", "growth"), ("A", "B", "C"), "Core income strategy."),
            "GROWTH": (LIMITED, ("base",), ("A", "B"), "Rising markets work against it."),
        },
    ),
    "Butterfly": (
        "Defined-risk bet that the price pins one level at expiry.",
        {
            "DEFENSIVE": (BLOCKED, (), (), "Low odds when volatility is high."),
            "NORMAL": (LIMITED, ("growth",), ("C", "D"), "Small size; low win rate."),
            "GROWTH": (BLOCKED, (), (), "Trending markets rarely pin."),
        },
    ),
    "Jade Lizard": (
        "Short put plus a short call spread: no upside risk if the credit exceeds the spread.",
        {
            "DEFENSIVE": (BLOCKED, (), (), "Undefined downside risk."),
            "NORMAL": (LIMITED, ("growth",), ("C", "D"), "Needs high implied volatility."),
            "GROWTH": (AVAILABLE, ("growth",), ("C", "D", "E"), "Bullish with premium to sell."),
        },
    ),
    "Straddle/Strangle": (
        "Short both a call and a put; large premium, large risk if the price moves.",
        {
            "DEFENSIVE": (BLOCKED, (), (), "Undefined risk in a falling regime."),
            "NORMAL": (LIMITED, ("growth",), ("D", "E"), "Undefined risk; small size only."),
            "GROWTH": (LIMITED, ("growth",), ("D", "E"), "Watch for breakouts."),
        },
    ),
}


def _gate_label(gate_clear: bool | None) -> str:
    if gate_clear is None:
        return "unknown"
    return "clear" if gate_clear else "blocked"


def build_matrix(
    current_regime: str | None,
    *,
    gate_clear: bool | None,
    layer: str | None = None,
    band: str | None = None,
) -> dict[str, Any]:
    """The matrix, with the current regime marked and the gate overlaid on it.

    When the gate is blocked, every cell of the current regime is shown as blocked (FR-1150).
    ``layer`` / ``band`` filter out cells that do not suit them (FR-1120): the cell is kept but
    flagged ``filtered`` so the grid keeps its shape.
    """
    rows = []
    for name, (description, regimes) in _STRATEGIES.items():
        cells = {}
        for regime in REGIMES:
            availability, layers, bands, note = regimes[regime]
            is_current = regime == current_regime
            effective = availability
            if is_current and gate_clear is False:
                effective = BLOCKED
            filtered = (
                bool((layer and layer not in layers) or (band and band not in bands))
                and availability != BLOCKED
            )
            cells[regime] = {
                "availability": effective,
                "base_availability": availability,
                "layers": list(layers),
                "bands": list(bands),
                "note": note,
                "gate": _gate_label(gate_clear) if is_current else None,
                "current": is_current,
                "filtered": filtered,
            }
        rows.append({"strategy": name, "description": description, "cells": cells})
    return {
        "regimes": list(REGIMES),
        "current_regime": current_regime,
        "gate_clear": gate_clear,
        "rows": rows,
    }


def strategy_names() -> list[str]:
    return list(_STRATEGIES)
