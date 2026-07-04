import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def push_to_sheet(df: pd.DataFrame, sheet_name: str) -> None:
    """
    Push a DataFrame to a specific worksheet in the configured Google Sheet.

    Parameters
    ----------
    df : pd.DataFrame
        Data to push.
    sheet_name : str
        Name of the worksheet (e.g. "Screener", "Daily Candidates",
        "Weekly Watchlist").
    """
    spreadsheet_name = os.getenv(
        "GOOGLE_SHEETS_SPREADSHEET_NAME", "Option Trading System"
    )

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        "service_account.json", scopes=scopes
    )
    client = gspread.authorize(creds)

    sheet = client.open(spreadsheet_name).worksheet(sheet_name)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())