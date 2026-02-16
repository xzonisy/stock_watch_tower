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

def fetch_etf_holdings(ticker):
    """
    Fetches the top 10 holdings for an ETF.
    Returns a list of dicts: [{'symbol': 'AAPL', 'name': 'Apple Inc', 'percent': 0.15}, ...]
    """
    try:
        etf = yf.Ticker(ticker)
        # funds_data.top_holdings is a pandas dataframe if available
        # Columns might be 'Name', 'Symbol', '% Assets', etc.
        # But yfinance API changes often.
        # funds_data might not exist or be empty.
        
        # New yfinance structure for funds
        # It seems .funds_data is the way
        
        # Let's try to get it, usually it's a dataframe with index as Symbol
        holdings_df = etf.funds_data.top_holdings
        if holdings_df is not None and not holdings_df.empty:
            # Structure usually: Index=Symbol, Columns=['Name', 'Holding %']
            # We want to convert to list of dicts
            holdings = []
            for symbol, row in holdings_df.iterrows():
                holdings.append({
                    'symbol': symbol,
                    'name': row['Name'],
                    'percent': row['Holding %']
                })
            return holdings
        else:
             print(f"No holdings data found for {ticker}")
             return []
             
    except Exception as e:
        print(f"Error fetching holdings for {ticker}: {e}")
        return []
