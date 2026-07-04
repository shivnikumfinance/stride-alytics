import os
import requests
import pandas as pd

FMP_API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"


def get_fundamentals(ticker: str) -> pd.DataFrame:
    """
    Fetch company profile / fundamentals from Financial Modeling Prep.

    Parameters
    ----------
    ticker : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Company profile data.
    """
    url = f"{BASE_URL}/profile/{ticker}"
    params = {"apikey": FMP_API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def get_key_metrics(ticker: str) -> pd.DataFrame:
    """
    Fetch key financial metrics from Financial Modeling Prep.

    Parameters
    ----------
    ticker : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Key metrics data.
    """
    url = f"{BASE_URL}/key-metrics/{ticker}"
    params = {"apikey": FMP_API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)
