"""Do-Not-Trade gate (docs: BR-010–021, BR-023, BR-042).

Two parts, combined by :func:`evaluate_entry`:

* **Master gate** — about the account and the market (regime, equity guardrail, alarms).
* **Symbol gate** — about the specific trade (liquidity, size, earnings, news flag, layer).

**Fail-safe:** if a rule needs data that could not be fetched, the trade is BLOCKED with a
"data unavailable" reason; it is never waved through on a guess. There is no override (BR-016).

Documented assumptions: the market counts as "down" when SPY is below its 200-day average
(BR-010); the regime counts as deteriorated below a score of 25 (BR-015). Rules about equities
(market cap, earnings) are skipped for ETFs and indices. BR-011 (assignment alarms) and BR-013
(correlation) are reported as *not evaluated* until the alert engine and risk analytics exist.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

from app.domain.allocation import growth_locked
from app.domain.portfolio_risk import entry_risk_reason
from app.domain.regime_score import UNKNOWN, RegimeScore

SPREAD_MAX_PCT = 10.0  # BR-017 (percent of mid price)
OPEN_INTEREST_MIN = 500  # BR-018
MARKET_CAP_MIN = 2_000_000_000  # BR-019
BASE_MARKET_CAP_MIN = 10_000_000_000  # BR-042: Conservative/Base layer profile
EARNINGS_WINDOW_DAYS = 14  # BR-020
REGIME_BLOCK_SCORE = 25.0  # BR-015

NON_EQUITY_TYPES = {"ETF", "INDEX", "MUTUALFUND", "CURRENCY", "CRYPTOCURRENCY", "FUTURE"}


@dataclass
class GateReason:
    rule_id: str
    message: str
    kind: str = "block"  # "block" = rule failed; "data" = could not verify (also blocks)


@dataclass
class GateResult:
    clear: bool
    reasons: list[GateReason] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)
    not_evaluated: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SymbolData:
    """What the gate needs to know about one candidate trade."""

    symbol: str
    fetched: bool = False
    quote_type: str | None = None
    market_cap: float | None = None
    next_earnings: date | None = None
    spread_pct: float | None = None
    open_interest: int | None = None


def _result(reasons: list[GateReason], checked: list[str], not_evaluated: list[str]) -> GateResult:
    return GateResult(
        clear=not reasons,
        reasons=reasons,
        checked=sorted(set(checked)),
        not_evaluated=not_evaluated,
    )


def evaluate_master(
    regime: RegimeScore | None,
    *,
    equity: float,
    min_equity: float,
    assignment_alarms: int | None = None,
    capital_at_risk: float | None = None,
) -> GateResult:
    """Account/market-level rules."""
    reasons: list[GateReason] = []
    checked: list[str] = ["BR-010", "BR-012", "BR-015"]
    not_evaluated = ["BR-013"]  # correlation: needs portfolio risk analytics

    if regime is None or regime.score is None:
        reasons.append(
            GateReason(
                "BR-015", "Data unavailable: the regime score could not be computed.", "data"
            )
        )
    else:
        if regime.market_down:
            reasons.append(
                GateReason(
                    "BR-010", "The broader market is down (SPY is below its 200-day average)."
                )
            )
        if regime.score < REGIME_BLOCK_SCORE:
            reasons.append(
                GateReason(
                    "BR-015",
                    f"Regime score {regime.score:g} is below the {REGIME_BLOCK_SCORE:g} baseline.",
                )
            )

    if min_equity > 0 and equity < min_equity:
        reasons.append(
            GateReason(
                "BR-012",
                f"Account equity ${equity:,.0f} is below the ${min_equity:,.0f} guardrail.",
            )
        )

    if assignment_alarms is None:
        not_evaluated.append("BR-011")
    else:
        checked.append("BR-011")
        if assignment_alarms > 0:
            reasons.append(
                GateReason(
                    "BR-011", f"{assignment_alarms} open trade(s) have an active assignment alarm."
                )
            )
    if capital_at_risk is not None:
        checked.append("BR-081")
        reason = entry_risk_reason(equity, capital_at_risk, None)
        if reason:
            reasons.append(GateReason("BR-081", reason))
    return _result(reasons, checked, not_evaluated)


def evaluate_symbol(
    data: SymbolData,
    *,
    trade_type: str,
    layer: str | None,
    news_flag: bool,
    today: date,
) -> GateResult:
    """Rules about the specific symbol/contract."""
    reasons: list[GateReason] = []
    checked: list[str] = ["BR-021"]

    def unknown(rule_id: str, what: str) -> None:
        reasons.append(GateReason(rule_id, f"Data unavailable: could not verify {what}.", "data"))

    if news_flag:
        reasons.append(GateReason("BR-021", f"{data.symbol} has a news flag set."))

    is_equity = data.fetched and (data.quote_type or "").upper() not in NON_EQUITY_TYPES
    if not data.fetched:
        # Nothing could be fetched: every data-dependent rule is unverifiable.
        unknown("BR-019", "market cap")
        unknown("BR-020", "the earnings date")
        checked += ["BR-019", "BR-020"]
    elif is_equity:
        checked += ["BR-019", "BR-020"]
        if data.market_cap is None:
            unknown("BR-019", "market cap")
        else:
            if data.market_cap < MARKET_CAP_MIN:
                reasons.append(
                    GateReason("BR-019", f"Market cap ${data.market_cap / 1e9:.1f}B is below $2B.")
                )
            if layer == "base":
                checked.append("BR-042")
                if data.market_cap < BASE_MARKET_CAP_MIN:
                    reasons.append(
                        GateReason(
                            "BR-042",
                            f"Base layer needs a market cap above $10B (this is ${data.market_cap / 1e9:.1f}B).",
                        )
                    )
        if data.next_earnings is None or data.next_earnings < today:
            unknown("BR-020", "the next earnings date")
        elif (data.next_earnings - today).days <= EARNINGS_WINDOW_DAYS:
            reasons.append(
                GateReason(
                    "BR-020",
                    f"Earnings on {data.next_earnings.isoformat()} are within {EARNINGS_WINDOW_DAYS} days.",
                )
            )

    if trade_type in ("call", "put"):
        checked += ["BR-017", "BR-018"]
        if data.spread_pct is None:
            unknown("BR-017", "the bid/ask spread")
        elif data.spread_pct > SPREAD_MAX_PCT:
            reasons.append(
                GateReason(
                    "BR-017",
                    f"Bid/ask spread {data.spread_pct:.1f}% is above {SPREAD_MAX_PCT:g}%.",
                )
            )
        if data.open_interest is None:
            unknown("BR-018", "open interest")
        elif data.open_interest < OPEN_INTEREST_MIN:
            reasons.append(
                GateReason(
                    "BR-018", f"Open interest {data.open_interest} is below {OPEN_INTEREST_MIN}."
                )
            )
    return _result(reasons, checked, [])


def evaluate_entry(
    *,
    regime: RegimeScore | None,
    equity: float,
    min_equity: float,
    symbol_data: SymbolData,
    trade_type: str,
    layer: str | None,
    news_flag: bool,
    today: date,
    assignment_alarms: int | None = None,
    capital_at_risk: float | None = None,
) -> GateResult:
    """Master gate + symbol gate + layer lock, merged."""
    master = evaluate_master(
        regime,
        equity=equity,
        min_equity=min_equity,
        assignment_alarms=assignment_alarms,
        capital_at_risk=capital_at_risk,
    )
    symbol = evaluate_symbol(
        symbol_data, trade_type=trade_type, layer=layer, news_flag=news_flag, today=today
    )
    reasons = master.reasons + symbol.reasons
    checked = master.checked + symbol.checked
    if layer == "growth":
        checked.append("BR-023")
        state = regime.state if regime is not None else UNKNOWN
        if growth_locked(state):
            reasons.append(GateReason("BR-023", f"The Growth layer is locked in a {state} regime."))
    return _result(reasons, checked, master.not_evaluated)
