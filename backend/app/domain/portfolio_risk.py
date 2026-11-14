"""Portfolio-level risk (docs: BR-080, BR-081, FR-540, FR-550).

Pure functions. Without a broker feed there is no real margin figure, so **Margin %** is the
capital at risk (the sum of ``risk_amount`` of open trades) as a share of account equity. Net Delta
is the share-equivalent delta of all priced positions; positions that could not be priced are
counted and reported, never assumed to be zero.

Limits are documented defaults (see ``docs/BUSINESS/05-IMPLEMENTATION-STATUS.md``).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

MAX_CAPITAL_AT_RISK_PCT = 50.0  # of equity; new entries beyond this are blocked (BR-081)
MAX_SECTOR_RISK_PCT = 25.0  # capital at risk in one sector, as % of equity
MAX_NET_DELTA_PCT = 100.0  # |net delta in dollars| as % of equity
UNKNOWN_SECTOR = "Unknown"


@dataclass
class PositionRisk:
    symbol: str
    risk_amount: float = 0.0
    sector: str | None = None
    position_delta: float | None = None  # share-equivalent, signed (short put = positive)
    spot: float | None = None


@dataclass
class Breach:
    rule_id: str
    code: str
    message: str


@dataclass
class PortfolioRisk:
    equity: float
    capital_at_risk: float
    margin_pct: float | None
    net_delta: float
    net_delta_dollars: float
    net_delta_pct: float | None
    unpriced_positions: int
    sectors: list[dict[str, Any]] = field(default_factory=list)
    breaches: list[Breach] = field(default_factory=list)
    limits: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _pct(part: float, whole: float) -> float | None:
    return round(part / whole * 100, 1) if whole > 0 else None


def calculate_portfolio_risk(positions: list[PositionRisk], equity: float) -> PortfolioRisk:
    at_risk = round(sum(max(p.risk_amount, 0.0) for p in positions), 2)

    priced = [p for p in positions if p.position_delta is not None and p.spot is not None]
    net_delta = round(sum(p.position_delta or 0.0 for p in priced), 2)
    net_dollars = round(sum((p.position_delta or 0.0) * (p.spot or 0.0) for p in priced), 2)

    by_sector: dict[str, float] = {}
    for p in positions:
        key = p.sector or UNKNOWN_SECTOR
        by_sector[key] = by_sector.get(key, 0.0) + max(p.risk_amount, 0.0)
    sectors = [
        {
            "sector": name,
            "capital_at_risk": round(value, 2),
            "pct_of_equity": _pct(value, equity),
            "pct_of_risk": _pct(value, at_risk),
        }
        for name, value in sorted(by_sector.items(), key=lambda kv: -kv[1])
    ]

    margin_pct = _pct(at_risk, equity)
    net_pct = _pct(abs(net_dollars), equity)
    # Limits are compared on the unrounded values so a tiny excess is not hidden by rounding.
    raw_margin = at_risk / equity * 100 if equity > 0 else None
    raw_net = abs(net_dollars) / equity * 100 if equity > 0 else None

    breaches: list[Breach] = []
    if raw_margin is not None and raw_margin > MAX_CAPITAL_AT_RISK_PCT:
        breaches.append(
            Breach(
                "BR-081",
                "total_risk",
                f"Capital at risk is {margin_pct}% of equity (limit {MAX_CAPITAL_AT_RISK_PCT:g}%).",
            )
        )
    for s in sectors:
        pct = s["pct_of_equity"]
        raw = s["capital_at_risk"] / equity * 100 if equity > 0 else None
        if s["sector"] != UNKNOWN_SECTOR and raw is not None and raw > MAX_SECTOR_RISK_PCT:
            breaches.append(
                Breach(
                    "BR-080",
                    "sector",
                    f"{s['sector']} holds {pct}% of equity at risk (limit {MAX_SECTOR_RISK_PCT:g}%).",
                )
            )
    if raw_net is not None and raw_net > MAX_NET_DELTA_PCT:
        breaches.append(
            Breach(
                "BR-080",
                "net_delta",
                f"Net delta exposure is {net_pct}% of equity (limit {MAX_NET_DELTA_PCT:g}%).",
            )
        )

    return PortfolioRisk(
        equity=round(equity, 2),
        capital_at_risk=at_risk,
        margin_pct=margin_pct,
        net_delta=net_delta,
        net_delta_dollars=net_dollars,
        net_delta_pct=net_pct,
        unpriced_positions=len(positions) - len(priced),
        sectors=sectors,
        breaches=breaches,
        limits={
            "capital_at_risk_pct": MAX_CAPITAL_AT_RISK_PCT,
            "sector_risk_pct": MAX_SECTOR_RISK_PCT,
            "net_delta_pct": MAX_NET_DELTA_PCT,
        },
    )


def entry_risk_reason(equity: float, committed: float, new_risk: float | None) -> str | None:
    """BR-081: reason to block new entries because total risk is over the limit, else None.

    With ``new_risk`` it projects the total after that trade; without it, it checks the current
    total (the master gate uses this form).
    """
    if equity <= 0:
        return None  # the equity guardrail handles this case
    pct = (committed + max(new_risk or 0.0, 0.0)) / equity * 100
    if pct <= MAX_CAPITAL_AT_RISK_PCT:
        return None
    when = "would be" if new_risk else "is"
    tail = " after this trade" if new_risk else ""
    return (
        f"Total capital at risk {when} {pct:.1f}% of equity{tail} "
        f"(limit {MAX_CAPITAL_AT_RISK_PCT:g}%)."
    )
