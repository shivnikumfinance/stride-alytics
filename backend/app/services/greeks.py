"""Black-Scholes options pricing & Greeks engine.

Pure functions — no I/O, no FastAPI imports — so they can be reused by
``api/v1/endpoints/greeks.py`` AND ``scheduler/scripts/calculate_greeks.py``.

Reference formulas:
    https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy import stats

from app.utils.constants import DEFAULT_RISK_FREE_RATE, DEFAULT_VOLATILITY


@dataclass(frozen=True)
class GreeksResult:
    """All Black-Scholes outputs for a single option contract."""

    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    price_call: float
    price_put: float


def _d1_d2(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> tuple[float, float]:
    if time_to_expiry <= 0:
        raise ValueError("time_to_expiry must be > 0")
    if volatility <= 0:
        raise ValueError("volatility must be > 0")
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be > 0")

    sqrt_t = math.sqrt(time_to_expiry)
    d1 = (
        math.log(spot / strike)
        + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry
    ) / (volatility * sqrt_t)
    d2 = d1 - volatility * sqrt_t
    return d1, d2


def _norm_cdf(x: float) -> float:
    """Standard normal CDF narrowed to ``float`` (scipy returns ``np.floating``)."""
    return float(stats.norm.cdf(x))


def _norm_pdf(x: float) -> float:
    """Standard normal PDF narrowed to ``float`` (scipy returns ``np.floating``)."""
    return float(stats.norm.pdf(x))


def calculate_option_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str = "call",
) -> float:
    """Return the Black-Scholes theoretical option price."""
    d1, d2 = _d1_d2(spot, strike, time_to_expiry, risk_free_rate, volatility)
    discount = math.exp(-risk_free_rate * time_to_expiry)

    if option_type == "call":
        return spot * _norm_cdf(d1) - strike * discount * _norm_cdf(d2)
    if option_type == "put":
        return strike * discount * _norm_cdf(-d2) - spot * _norm_cdf(-d1)
    raise ValueError(f"option_type must be 'call' or 'put', got: {option_type!r}")


def calculate_greeks(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    volatility: float = DEFAULT_VOLATILITY,
    option_type: str = "call",
) -> GreeksResult:
    """Return delta, gamma, theta, vega, rho, plus both call & put prices.

    Theta is expressed **per calendar day** (divided by 365).
    Vega is expressed **per 1% change in IV**.
    Rho is expressed **per 1% change in the risk-free rate**.
    """
    d1, d2 = _d1_d2(spot, strike, time_to_expiry, risk_free_rate, volatility)
    sqrt_t = math.sqrt(time_to_expiry)
    nd1 = _norm_cdf(d1)
    nd2 = _norm_cdf(d2)
    npd1 = _norm_pdf(d1)
    discount = math.exp(-risk_free_rate * time_to_expiry)

    # --- Greeks (common across call & put) ---
    gamma = npd1 / (spot * volatility * sqrt_t)
    vega = spot * npd1 * sqrt_t / 100.0

    if option_type == "call":
        delta = nd1
        theta = (
            -spot * npd1 * volatility / (2 * sqrt_t)
            - risk_free_rate * strike * discount * nd2
        ) / 365.0
        rho = strike * time_to_expiry * discount * nd2 / 100.0
    elif option_type == "put":
        delta = nd1 - 1
        theta = (
            -spot * npd1 * volatility / (2 * sqrt_t)
            + risk_free_rate * strike * discount * (1 - nd2)
        ) / 365.0
        rho = -strike * time_to_expiry * discount * (1 - nd2) / 100.0
    else:
        raise ValueError(f"option_type must be 'call' or 'put', got: {option_type!r}")

    price_call = calculate_option_price(
        spot, strike, time_to_expiry, risk_free_rate, volatility, "call"
    )
    price_put = calculate_option_price(
        spot, strike, time_to_expiry, risk_free_rate, volatility, "put"
    )

    return GreeksResult(
        delta=round(delta, 4),
        gamma=round(gamma, 6),
        theta=round(theta, 4),
        vega=round(vega, 4),
        rho=round(rho, 4),
        price_call=round(price_call, 4),
        price_put=round(price_put, 4),
    )


def calculate_greeks_dict(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    volatility: float = DEFAULT_VOLATILITY,
    option_type: str = "call",
) -> dict:
    """Convenience wrapper returning a plain ``dict`` (JSON-friendly)."""
    result = calculate_greeks(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
        option_type=option_type,
    )
    return {
        "delta": result.delta,
        "gamma": result.gamma,
        "theta": result.theta,
        "vega": result.vega,
        "rho": result.rho,
        "price_call": result.price_call,
        "price_put": result.price_put,
    }
