import os
import requests
import pandas as pd

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

BASE_URL = "https://api.polygon.io"


def get_option_chain(ticker: str) -> pd.DataFrame:
    """
    Fetch option contracts for a ticker from Polygon.io.

    Parameters
    ----------
    ticker : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Option contracts data.
    """
    url = f"{BASE_URL}/v3/reference/options/contracts"
    params = {
        "underlying_ticker": ticker,
        "limit": 1000,
        "apiKey": POLYGON_API_KEY,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json().get("results", [])
    return pd.DataFrame(data)


def get_aggregates(ticker: str) -> pd.DataFrame:
    """
    Fetch daily OHLCV aggregates for a ticker from Polygon.io.

    Parameters
    ----------
    ticker : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Aggregated bars data.
    """
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/2024-01-01/2024-12-31"
    params = {"apiKey": POLYGON_API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json().get("results", [])
    return pd.DataFrame(data)
