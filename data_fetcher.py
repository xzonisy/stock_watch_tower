import yfinance as yf
import pandas as pd
import config

def fetch_data(tickers, period="6mo"):
    """
    Fetches historical data for the given tickers.
    """
    print(f"Fetching data for {len(tickers)} tickers...")
    # Fetch full data
    data = yf.download(tickers, period=period, progress=False)
    
    # If we only have one level of columns (single ticker), yfinance might return simple DF.
    # If multiple tickers, it returns MultiIndex columns (Price, Ticker).
    
    # For compatibility with existing code which expects just 'Close' for sectors:
    # We can add a flag or just return 'Close' by default, but we need OHLC for stocks.
    
    return data
