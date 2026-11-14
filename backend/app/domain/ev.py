"""Expected-value scoring (docs: FR-920, FR-1220) and calibration against realised results.

``EV = PoP x gain - (1 - PoP) x loss`` per contract (or per 100 shares). The probability of profit
(PoP) is approximated from delta for a short option: ``1 - |delta|`` is the chance it expires
worthless. For a pick without a delta, its stored confidence is used as PoP. It is a ranking aid,
not a forecast; the calibration report shows how realised results compare.
"""

from __future__ import annotations

from typing import Any

CONTRACT_MULTIPLIER = 100


def pop_from_delta(delta: float | None) -> float | None:
    """Probability a short option expires worthless, from its delta (clamped to 0-1)."""
    if delta is None:
        return None
    return min(1.0, max(0.0, 1.0 - abs(delta)))


def expected_value(pop: float | None, gain: float | None, loss: float | None) -> float | None:
    """EV in dollars; None when any input is missing. ``gain`` and ``loss`` are positive numbers."""
    if pop is None or gain is None or loss is None:
        return None
    if not 0.0 <= pop <= 1.0 or gain < 0 or loss < 0:
        return None
    return round(pop * gain - (1.0 - pop) * loss, 2)


def pick_ev(pick: dict[str, Any]) -> float | None:
    """EV per contract of a weekly pick, using its confidence as PoP.

    Gain = target - entry, loss = entry - stop (per share, long side), times the multiplier.
    A short-side pick (stop above entry) is handled by taking absolute distances.
    """
    entry, target, stop = pick.get("entry_price"), pick.get("target_price"), pick.get("stop_loss")
    if entry is None or target is None or stop is None:
        return None
    mult = 1 if pick.get("side") == "stock" else CONTRACT_MULTIPLIER
    return expected_value(
        pick.get("confidence"), abs(target - entry) * mult, abs(entry - stop) * mult
    )


def rank_picks(picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add ``ev`` to each pick and sort by it (picks without an EV go last, by confidence)."""
    scored = [{**p, "ev": pick_ev(p)} for p in picks]
    return sorted(
        scored,
        key=lambda p: (p["ev"] is None, -(p["ev"] or 0.0), -(p.get("confidence") or 0.0)),
    )


def calibration(closed: list[dict[str, Any]]) -> dict[str, Any]:
    """Realised results of closed trades, grouped by layer: win rate and average P&L.

    ``expected`` is the entry EV recorded on the trade when there is one. Closed trades without
    it are still counted in the realised figures.
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    for t in closed:
        groups.setdefault(t.get("layer") or "unassigned", []).append(t)

    rows = []
    for name, trades in sorted(groups.items()):
        pnls = [t["pnl"] for t in trades]
        wins = sum(1 for p in pnls if p > 0)
        evs = [t["expected"] for t in trades if t.get("expected") is not None]
        rows.append(
            {
                "group": name,
                "trades": len(trades),
                "win_rate": round(wins / len(trades) * 100, 1),
                "avg_pnl": round(sum(pnls) / len(pnls), 2),
                "total_pnl": round(sum(pnls), 2),
                "avg_expected": round(sum(evs) / len(evs), 2) if evs else None,
                "with_expected": len(evs),
            }
        )
    return {"groups": rows, "total_trades": len(closed)}
