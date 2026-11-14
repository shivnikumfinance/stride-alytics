"""Exit and risk alerts for open positions (docs: BR-050–054, BR-095–098, FR-500, FR-1210/1230).

Each open trade is rated ``normal`` / ``watch`` / ``warning`` / ``critical`` with the reasons and a
suggested action (``hold`` / ``roll`` / ``close`` / ``hedge``). Rules that need live prices (delta,
moneyness, P&L) are skipped, and the position is flagged, when market data is unavailable; rules
based on dates alone (days to expiry) always run.

Thresholds are documented defaults (see ``docs/BUSINESS/05-IMPLEMENTATION-STATUS.md``): delta of
0.70 or more on a short option is an assignment alarm (BR-052); a short option in the money is a
warning; profit of 50% / 80% of the credit suggests closing; loss of 50% / 100% / 200% of the
credit (or of the capital at risk, when known) escalates; days to expiry of 7 / 3 / past due
escalate. Regime deterioration (score below 25) warns on every open position (BR-051).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

SEVERITIES = ("normal", "watch", "warning", "critical")
CONTRACT_MULTIPLIER = 100

DTE_WATCH = 7
DTE_WARNING = 3
DELTA_ASSIGNMENT = 0.70  # BR-052: assignment alarm
DELTA_WARNING = 0.50
DELTA_WATCH = {"base": 0.30, "growth": 0.40}  # per-layer tolerance (BR-053)
DEEP_ITM_PCT = 5.0  # percent in the money counted as an assignment alarm even without a delta
PROFIT_WATCH = 0.50  # captured share of the credit
PROFIT_WARNING = 0.80
SHORT_LOSS = (0.5, 1.0, 2.0)  # loss as a share of the credit: watch, warning, critical
LONG_LOSS = (0.5, 0.75, 0.9)  # loss as a share of the premium paid
RISK_LOSS = (0.25, 0.5, 1.0)  # loss as a share of the capital at risk: watch, warning, critical
REGIME_FLOOR = 25.0  # same floor the gate uses (BR-015)

# Higher number = more urgent; used to pick the suggested action when several rules fire.
_ACTION_PRIORITY = {"close": 3, "roll": 2, "hedge": 1, "hold": 0}


def rank(severity: str) -> int:
    return SEVERITIES.index(severity)


@dataclass
class PositionInput:
    trade_id: str
    symbol: str
    trade_type: str  # call | put | stock
    direction: str  # long | short
    quantity: int
    entry_price: float
    strike: float | None = None
    expiry: date | None = None
    layer: str | None = None
    band: str | None = None
    risk_amount: float | None = None
    credit: float | None = None


@dataclass
class MarketInput:
    """Live numbers for one position. ``available=False`` means nothing could be fetched."""

    available: bool = False
    spot: float | None = None  # underlying price
    mark: float | None = None  # current price of the option (or the stock) per share
    delta: float | None = None  # per contract, signed (calls +, puts -)
    theta: float | None = None  # per contract per day
    iv: float | None = None


@dataclass
class AlertReason:
    code: str
    severity: str
    message: str
    action: str = "hold"
    rule_id: str | None = None


@dataclass
class PositionAlert:
    trade_id: str
    symbol: str
    trade_type: str
    direction: str
    quantity: int
    strategy_detail: dict[str, Any]
    severity: str
    action: str
    reasons: list[AlertReason] = field(default_factory=list)
    dte: int | None = None
    pnl: float | None = None
    pnl_pct: float | None = None
    delta: float | None = None
    position_delta: float | None = None
    theta: float | None = None
    spot: float | None = None
    mark: float | None = None
    itm: bool | None = None
    assignment_risk: bool = False
    data_available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_option(pos: PositionInput) -> bool:
    return pos.trade_type in ("call", "put")


def _is_short(pos: PositionInput) -> bool:
    return pos.direction == "short"


def _scale(pos: PositionInput) -> int:
    return CONTRACT_MULTIPLIER if _is_option(pos) else 1


def evaluate_position(
    pos: PositionInput,
    market: MarketInput,
    *,
    today: date,
    regime_score: float | None = None,
) -> PositionAlert:
    reasons: list[AlertReason] = []

    def add(
        code: str, severity: str, message: str, action: str = "hold", rule_id: str | None = None
    ):
        reasons.append(AlertReason(code, severity, message, action, rule_id))

    option = _is_option(pos)
    short = _is_short(pos)
    dte = (pos.expiry - today).days if (option and pos.expiry) else None

    # ---- time (dates only: always evaluated)
    if dte is not None:
        if dte < 0:
            add(
                "expired",
                "critical",
                f"Expired {-dte} day(s) ago but still open: close it or record the outcome.",
                "close",
                "BR-050",
            )
        elif dte <= DTE_WARNING:
            add("dte", "warning", f"Only {dte} day(s) to expiry.", "roll", "BR-050")
        elif dte <= DTE_WATCH:
            add("dte", "watch", f"{dte} days to expiry.", "hold", "BR-050")

    # ---- live data rules
    spot, mark, delta = market.spot, market.mark, market.delta
    itm: bool | None = None
    pnl = pnl_pct = None

    if market.available and mark is not None:
        per_share = (pos.entry_price - mark) if short else (mark - pos.entry_price)
        pnl = round(per_share * pos.quantity * _scale(pos), 2)
        pnl_pct = round(per_share / pos.entry_price, 4) if pos.entry_price else None

    if market.available and option and spot is not None and pos.strike:
        itm = spot < pos.strike if pos.trade_type == "put" else spot > pos.strike
        if short and itm:
            depth = abs(spot - pos.strike) / pos.strike * 100
            if depth >= DEEP_ITM_PCT:
                add(
                    "assignment_risk",
                    "critical",
                    f"Short {pos.trade_type} is {depth:.1f}% in the money: assignment risk.",
                    "roll" if (dte or 0) > 0 else "close",
                    "BR-052",
                )
            else:
                add(
                    "itm",
                    "warning",
                    f"Short {pos.trade_type} is in the money ({spot:g} vs strike {pos.strike:g}).",
                    "roll",
                    "BR-052",
                )

    if market.available and option and delta is not None:
        magnitude = abs(delta)
        if short and magnitude >= DELTA_ASSIGNMENT:
            add(
                "assignment_risk",
                "critical",
                f"Delta {magnitude:.2f} is at or above {DELTA_ASSIGNMENT:g}: assignment alarm.",
                "roll" if (dte or 0) > 0 else "close",
                "BR-052",
            )
        elif magnitude >= DELTA_WARNING:
            add(
                "delta_high",
                "warning",
                f"Delta {magnitude:.2f} is above {DELTA_WARNING:g}.",
                "roll",
                "BR-053",
            )
        elif magnitude >= DELTA_WATCH.get(pos.layer or "base", DELTA_WATCH["base"]):
            add(
                "delta_watch",
                "watch",
                f"Delta {magnitude:.2f} is above the {pos.layer or 'base'}-layer tolerance.",
                "hold",
                "BR-053",
            )

    if pnl_pct is not None and pnl is not None:
        if short and pnl_pct >= PROFIT_WARNING:
            add(
                "profit_target",
                "warning",
                f"{pnl_pct:.0%} of the credit is captured: take profits.",
                "close",
                "BR-050",
            )
        elif short and pnl_pct >= PROFIT_WATCH:
            add(
                "profit_target",
                "watch",
                f"{pnl_pct:.0%} of the credit is captured: consider closing.",
                "close",
                "BR-050",
            )

        loss = -pnl
        if loss > 0:
            if pos.risk_amount and pos.risk_amount > 0:
                ratio, tiers, basis = loss / pos.risk_amount, RISK_LOSS, "capital at risk"
            else:
                ratio, tiers, basis = (
                    -pnl_pct,
                    (SHORT_LOSS if short else LONG_LOSS),
                    ("credit" if short else "premium paid"),
                )
            if ratio >= tiers[2]:
                add(
                    "stop_loss",
                    "critical",
                    f"Loss is {ratio:.0%} of the {basis}: stop-loss breached.",
                    "close",
                    "BR-050",
                )
            elif ratio >= tiers[1]:
                add(
                    "stop_loss",
                    "warning",
                    f"Loss is {ratio:.0%} of the {basis}.",
                    "close",
                    "BR-050",
                )
            elif ratio >= tiers[0]:
                add("stop_loss", "watch", f"Loss is {ratio:.0%} of the {basis}.", "hold", "BR-050")

    if option and not market.available and (dte is None or dte >= 0):
        add(
            "no_market_data",
            "watch",
            "Live prices are unavailable, so delta, moneyness and P&L were not checked.",
            "hold",
        )

    # ---- regime (BR-051)
    if regime_score is not None and regime_score < REGIME_FLOOR:
        add(
            "regime",
            "warning",
            f"The market regime has deteriorated (score {regime_score:g}).",
            "close" if pos.layer == "growth" else "hedge",
            "BR-051",
        )

    severity = max((r.severity for r in reasons), key=rank, default="normal")
    top = [r for r in reasons if r.severity == severity]
    action = max((r.action for r in top), key=lambda a: _ACTION_PRIORITY[a]) if top else "hold"
    if severity == "normal":
        action = "hold"

    return PositionAlert(
        trade_id=pos.trade_id,
        symbol=pos.symbol,
        trade_type=pos.trade_type,
        direction=pos.direction,
        quantity=pos.quantity,
        strategy_detail={
            "strike": pos.strike,
            "expiry": pos.expiry.isoformat() if pos.expiry else None,
            "layer": pos.layer,
            "band": pos.band,
            "entry_price": pos.entry_price,
            "risk_amount": pos.risk_amount,
        },
        severity=severity,
        action=action,
        reasons=sorted(reasons, key=lambda r: -rank(r.severity)),
        dte=dte,
        pnl=pnl,
        pnl_pct=pnl_pct,
        delta=delta,
        position_delta=(
            None
            if delta is None
            else round(delta * pos.quantity * CONTRACT_MULTIPLIER * (-1 if short else 1), 2)
        ),
        theta=market.theta,
        spot=spot,
        mark=mark,
        itm=itm,
        assignment_risk=any(r.code == "assignment_risk" for r in reasons),
        data_available=market.available,
    )


def summarize(alerts: list[PositionAlert]) -> dict[str, int]:
    counts = {s: 0 for s in SEVERITIES}
    for a in alerts:
        counts[a.severity] += 1
    return counts
