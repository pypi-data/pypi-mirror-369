import sqlite3
import os
from typing import List, Optional
from datetime import datetime
import yfinance as yf
import pandas as pd
# Path to the SQLite database inside the package
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'earnings.db')

def get_connection():
    """Returns a connection to the earnings database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Database not found. Ensure 'earnings.db' exists in the 'data' folder.")
    return sqlite3.connect(DB_PATH)

def get_earnings(ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[str]:
    """
    Retrieves the earnings dates for a given stock ticker.

    Args:
        ticker (str): Stock ticker (e.g., "AAPL", "MSFT").
        start_date (str, optional): Filter results starting from this date ("YYYY-MM-DD").
        end_date (str, optional): Filter results ending at this date ("YYYY-MM-DD").

    Returns:
        List[str]: A list of earnings dates in "YYYY-MM-DD" format.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be a non-empty string.")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT Earnings_Date FROM earnings WHERE Ticker = ?"
        params = [ticker.upper()]

        if start_date:
            query += " AND Earnings_Date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND Earnings_Date <= ?"
            params.append(end_date)

        query += " ORDER BY Earnings_Date DESC"
        cursor.execute(query, tuple(params))

        results = cursor.fetchall()
        return [row[0] for row in results]

    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def list_all_tickers() -> List[str]:
    """
    Returns a sorted list of all tickers available in the database.

    Returns:
        List[str]: A list of unique ticker symbols.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Ticker FROM earnings ORDER BY Ticker ASC")
        results = cursor.fetchall()
        return [row[0] for row in results]

    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
def get_earnings_price_reactions(ticker: str, min_days_ago: int = 0) -> List[dict]:
    """
    Returns a list of dictionaries with earnings dates and percentage price movements:
        - Close→Next Open (%)
        - Close→Next Close (%)
        - Next Open→Next Close (%)

    Args:
        ticker (str): Stock ticker symbol.
        min_days_ago (int): Ignore earnings dates less than this many days ago.
    Returns:
        List[dict]: List of price movement info per earnings date.
    """
    earnings_dates = get_earnings(ticker)
    if not earnings_dates:
        return []

    earnings_dates = pd.to_datetime(earnings_dates)
    earnings_dates = sorted([
        d for d in earnings_dates
        if (pd.Timestamp.now() - d).days >= min_days_ago
    ], reverse=True)

    if not earnings_dates:
        return []

    ticker_data = yf.Ticker(ticker)
    try:
        data = ticker_data.history(
            start=min(earnings_dates) - pd.Timedelta(days=2),
            end=max(earnings_dates) + pd.Timedelta(days=3)
        )
    except Exception as e:
        raise RuntimeError(f"Failed to fetch stock data: {e}")

    if data.empty:
        return []

    data.index = data.index.tz_localize(None)
    data["Next_Open"] = data["Open"].shift(-1)
    data["Next_Close"] = data["Close"].shift(-1)
    data.reset_index(inplace=True)
    data["Date"] = pd.to_datetime(data["Date"]).dt.normalize()

    results = []
    for date in earnings_dates:
        row = data[data["Date"] == date]
        if not row.empty:
            close = row["Close"].values[0]
            next_open = row["Next_Open"].values[0]
            next_close = row["Next_Close"].values[0]

            if pd.notna(next_open) and pd.notna(next_close) and close != 0 and next_open != 0:
                results.append({
                    "date": date.date().isoformat(),
                    "close_to_open_pct": round((next_open - close) / close * 100, 2),
                    "close_to_close_pct": round((next_close - close) / close * 100, 2),
                    "open_to_close_pct": round((next_close - next_open) / next_open * 100, 2)
                })

    return results

