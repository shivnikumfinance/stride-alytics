import yfinance as yf
import pandas as pd


def get_stock_data(ticker: str) -> pd.DataFrame:
    """
    Fetch 1 year of historical OHLCV data from Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Historical data with Date, Open, High, Low, Close, Volume.
    """
    t = yf.Ticker(ticker)
    hist = t.history(period="1y")
    hist.reset_index(inplace=True)
    return hist


def get_options_summary(ticker: str) -> pd.DataFrame:
    """
    Fetch options chain summary (calls & puts) for up to 3 nearest expiries.

    Parameters
    ----------
    ticker : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Combined calls and puts chain data.
    """
    t = yf.Ticker(ticker)
    expiries = t.options
    rows = []
    for exp in expiries[:3]:
        opt_chain = t.option_chain(exp)
        for side_name, side_df in [
            ("calls", opt_chain.calls),
            ("puts", opt_chain.puts),
        ]:
            side_df = side_df.copy()
            side_df["expiry"] = exp
            side_df["side"] = side_name
            rows.append(side_df)
    if rows:
        return pd.concat(rows, ignore_index=True)
    return pd.DataFrame()