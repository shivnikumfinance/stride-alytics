"""Position sizing and capital-band caps (docs: FR-600–670, BR-030–034).

Risk budget = account size × risk % for the layer (Base 1–1.5%, Growth 2–3%; the defaults 1.25% and
2.5% are in Settings). Quantity:

* **max-loss mode** (preferred for defined-risk spreads): ``floor(budget / max_loss_per_contract)``
* **credit mode** (FR-670 taken literally): ``floor(budget / (credit × 100))`` — this sizes by
  premium, not by what you can lose, so it is flagged with a warning.

In a DEFENSIVE (or UNKNOWN) regime the budget is halved ("tightens sizing", BR-023) and the Growth
layer is locked. Band caps limit the share of account capital committed to one band; max-loss mode
reduces the quantity to fit, otherwise the trade is blocked.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any

from app.domain.allocation import growth_locked

CONTRACT_MULTIPLIER = 100
RISK_RANGE: dict[str, tuple[float, float]] = {"base": (1.0, 1.5), "growth": (2.0, 3.0)}
DEFENSIVE_SIZING_FACTOR = 0.5
BAND_WARN_FRACTION = 0.8


@dataclass
class SizingResult:
    mode: str  # "max_loss" | "credit" | "none"
    risk_pct: float
    risk_budget: float
    quantity: int = 0
    risk_amount: float | None = None  # capital at risk (max-loss mode only)
    blocked: bool = False
    reasons: list[dict[str, str]] = field(default_factory=list)  # [{rule_id, message}]
    warnings: list[str] = field(default_factory=list)
    band: str | None = None
    band_cap_pct: float | None = None
    band_exposure_after_pct: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def calculate_sizing(
    *,
    account_size: float,
    layer: str,
    risk_pct: float,
    regime_state: str,
    credit: float | None = None,
    max_loss_per_contract: float | None = None,
    band: str | None = None,
    band_caps: dict[str, float] | None = None,
    band_exposure_dollars: float = 0.0,
) -> SizingResult:
    result = SizingResult(mode="none", risk_pct=risk_pct, risk_budget=0.0, band=band)

    def block(rule_id: str, message: str) -> SizingResult:
        result.blocked = True
        result.quantity = 0
        result.reasons.append({"rule_id": rule_id, "message": message})
        return result

    if account_size <= 0:
        return block("FR-600", "Account size must be greater than zero (set it in Settings).")
    if layer not in RISK_RANGE:
        return block("FR-610", "Layer must be 'base' or 'growth'.")

    if layer == "growth" and growth_locked(regime_state):
        return block("BR-023", f"The Growth layer is locked in a {regime_state} regime.")

    low, high = RISK_RANGE[layer]
    if not low <= risk_pct <= high:
        result.warnings.append(
            f"Risk {risk_pct:g}% is outside the documented {layer} range of {low:g}–{high:g}%."
        )

    budget = account_size * risk_pct / 100.0
    if regime_state not in ("NORMAL", "GROWTH"):
        budget *= DEFENSIVE_SIZING_FACTOR
        result.warnings.append(
            f"Regime is {regime_state}: risk budget cut to {DEFENSIVE_SIZING_FACTOR:.0%} of normal."
        )
    result.risk_budget = round(budget, 2)

    if max_loss_per_contract is not None and max_loss_per_contract > 0:
        result.mode = "max_loss"
        per_contract = max_loss_per_contract
    elif credit is not None and credit > 0:
        result.mode = "credit"
        per_contract = credit * CONTRACT_MULTIPLIER
        result.warnings.append(
            "Sized by premium (Risk / Credit), not by maximum loss. Provide the max loss per "
            "contract for defined-risk spreads."
        )
    else:
        result.warnings.append("Provide the credit or the max loss per contract to get a quantity.")
        return result

    quantity = math.floor(budget / per_contract)

    # Band cap: share of account capital committed to the band (risk_amount is the capital basis).
    cap = (band_caps or {}).get(band) if band else None
    if band and cap is None:
        result.warnings.append(f"No cap is configured for band {band}.")
    elif band is None:
        result.warnings.append("No band assigned: the band cap was not checked.")
    if cap is not None:
        result.band_cap_pct = float(cap)
        capacity = account_size * cap / 100.0 - band_exposure_dollars
        if result.mode == "max_loss":
            fits = max(0, math.floor(capacity / per_contract))
            if fits < quantity:
                result.warnings.append(
                    f"Band {band} cap ({cap:g}%) limits the quantity from {quantity} to {fits}."
                )
                quantity = fits
            if quantity == 0:
                return block(
                    "BR-034", f"Band {band} is at its {cap:g}% capital cap; no room for this trade."
                )
        else:
            committed = band_exposure_dollars + budget
            if committed > account_size * cap / 100.0:
                return block("BR-034", f"Band {band} would exceed its {cap:g}% capital cap.")

    if quantity < 1:
        return block("FR-630", "The risk budget is smaller than the cost of one contract.")

    result.quantity = quantity
    if result.mode == "max_loss":
        result.risk_amount = round(quantity * per_contract, 2)
    if cap is not None:
        added = result.risk_amount if result.risk_amount is not None else budget
        after = (band_exposure_dollars + added) / account_size * 100.0
        result.band_exposure_after_pct = round(after, 2)
        if after >= cap * BAND_WARN_FRACTION:
            result.warnings.append(
                f"Band {band} would be at {after:.1f}% of capital (cap {cap:g}%): near its limit."
            )
    return result


def band_status(
    *, account_size: float, band_caps: dict[str, float], exposure_by_band: dict[str, float]
) -> list[dict[str, Any]]:
    """Per-band capital use for the portfolio view (FR-640)."""
    rows = []
    for band, cap in band_caps.items():
        exposure = exposure_by_band.get(band, 0.0)
        pct = exposure / account_size * 100.0 if account_size > 0 else 0.0
        if pct > cap:
            status = "over"
        elif pct >= cap * BAND_WARN_FRACTION:
            status = "near"
        else:
            status = "ok"
        rows.append(
            {
                "band": band,
                "exposure": round(exposure, 2),
                "exposure_pct": round(pct, 2),
                "cap_pct": float(cap),
                "status": status,
            }
        )
    return sorted(rows, key=lambda r: r["band"])
