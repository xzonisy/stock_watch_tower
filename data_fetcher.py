import yfinance as yf
import pandas as pd
import config

def fetch_data(tickers, period="6mo"):
    """
    Fetches historical data for the given tickers.
    """
    print(f"Fetching data for {len(tickers)} tickers...")
    data = yf.download(tickers, period=period, progress=False)['Close']
    
    # Ensure data is a DataFrame even if single ticker (though we expect multiple)
    if isinstance(data, pd.Series):
        data = data.to_frame()
    
    return data
