"""Date utilities for the Alpha application."""
import pandas as pd
from datetime import datetime, date


def format_date_mmm_dd_yyyy(date_val) -> str:
    """Format date to MMM-DD-YYYY style (e.g., Jul-07-2026).
    
    Parameters
    ----------
    date_val : str, date, datetime, or pd.Timestamp
        The date value to format.
    
    Returns
    -------
    str
        Formatted date string like "Jul-07-2026".
    """
    if pd.isna(date_val):
        return ""
    try:
        if isinstance(date_val, str):
            # Parse string date (YYYY-MM-DD or ISO format)
            # Take just the date part if it's a full ISO string
            if "T" in date_val:
                date_val = date_val.split("T")[0]
            if len(date_val) > 10:
                date_val = date_val[:10]
            date_obj = pd.to_datetime(date_val)
        elif isinstance(date_val, (datetime, date)):
            date_obj = pd.to_datetime(date_val)
        else:
            date_obj = pd.to_datetime(date_val)
        return date_obj.strftime("%b-%d-%Y")
    except Exception:
        return str(date_val)


def normalize_date_for_merge(date_val) -> str:
    """Normalize date to YYYY-MM-DD string format for database merging.
    
    Parameters
    ----------
    date_val : str, date, datetime, or pd.Timestamp
        The date value to normalize.
    
    Returns
    -------
    str
        Normalized date string like "2026-07-07".
    """
    if pd.isna(date_val):
        return ""
    try:
        if isinstance(date_val, str):
            if "T" in date_val:
                date_val = date_val.split("T")[0]
            if len(date_val) > 10:
                date_val = date_val[:10]
        else:
            date_val = pd.to_datetime(date_val).strftime("%Y-%m-%d")
        return str(date_val)
    except Exception:
        return str(date_val)
