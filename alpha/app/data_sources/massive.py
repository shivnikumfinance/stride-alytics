"""
Alpha Option Trading System — Massive API Data Source

This module fetches stock/option data from Massive's Stock Market API
and returns a pandas DataFrame suitable for the Alpha business logic.

Assumes:
- MASSIVE_API_KEY is set in .env and loaded via app.config.Config
"""

from typing import List, Dict, Any
import os
import requests
import pandas as pd

from app.config import config


BASE_URL = "https://api.massive.com"  # Adjust if Massive uses a different base URL


class MassiveClientError(Exception):
    """Custom exception for Massive API errors."""

    pass


def _get_headers() -> Dict[str, str]:
    api_key = config.MASSIVE_API_KEY or os.getenv("MASSIVE_API_KEY")
    if not api_key:
        raise MassiveClientError("MASSIVE_API_KEY is not set in environment or config.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }


def fetch_massive_data_for_tickers(tickers: List[str]) -> pd.DataFrame:
    """
    Fetch data from Massive for a list of tickers.

    Returns:
        DataFrame indexed by ticker with columns suitable for Alpha:
        - price
        - option_volume
        - max_oi_near_exp
        - bid_ask_spread_pct
        - iv_30d
        - iv_rank_1y
        - hv_30d
        - atr
        - next_earnings_date
        - short_interest_pct
        - sector
        - revenue_growth_yoy
        - debt_equity
        - quality_score
        - ema20
        - ema50
        - ema200

    NOTE: Field mapping depends on Massive's actual API response.
    Adjust the keys in `parse_massive_response_row` accordingly.
    """

    headers = _get_headers()
    rows: List[Dict[str, Any]] = []

    for ticker in tickers:
        url = f"{BASE_URL}/stocks/{ticker}"  # Example endpoint; adjust to real Massive path
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code != 200:
            raise MassiveClientError(
                f"Failed to fetch data for {ticker}: {resp.status_code} {resp.text}"
            )

        data = resp.json()
        parsed = parse_massive_response_row(ticker, data)
        rows.append(parsed)

    df = pd.DataFrame(rows).set_index("ticker")
    return df


def parse_massive_response_row(ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Massive API response for a single ticker into Alpha's schema.

    This is where you adapt Massive's actual JSON fields to Alpha's expected columns.
    Replace the placeholder keys below with the real ones from Massive's docs.
    """

    # Placeholder mappings — update these once you inspect Massive's actual JSON
    return {
        "ticker": ticker,
        "price": data.get("price"),
        "option_volume": data.get("option_volume"),
        "max_oi_near_exp": data.get("max_oi_near_exp"),
        "bid_ask_spread_pct": data.get("bid_ask_spread_pct"),
        "iv_30d": data.get("iv_30d"),
        "iv_rank_1y": data.get("iv_rank_1y"),
        "hv_30d": data.get("hv_30d"),
        "atr": data.get("atr"),
        "next_earnings_date": data.get("next_earnings_date"),
        "short_interest_pct": data.get("short_interest_pct"),
        "sector": data.get("sector"),
        "revenue_growth_yoy": data.get("revenue_growth_yoy"),
        "debt_equity": data.get("debt_equity"),
        "quality_score": data.get("quality_score"),
        "ema20": data.get("ema20"),
        "ema50": data.get("ema50"),
        "ema200": data.get("ema200"),
    }


if __name__ == "__main__":
    # Simple manual test harness
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    try:
        df = fetch_massive_data_for_tickers(test_tickers)
        print("\n✅ Massive data fetched successfully:")
        print(df.head())
    except MassiveClientError as e:
        print(f"\n❌ MassiveClientError: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
