import yfinance as yf
import pandas as pd
import config
import time
import concurrent.futures

def fetch_data(tickers, period="6mo", retries=3):
    """
    Fetches historical data for the given tickers with retry logic.
    """
    print(f"Fetching data for {len(tickers)} tickers...")
    
    for attempt in range(retries):
        try:
            # Fetch full data
            # auto_adjust=True fixes some data issues, but careful with existing logic
            # progress=False hides the tqdm bar
            data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
            
            # yfinance recent versions might return empty DF on fail without raising
            if data.empty:
                 raise ValueError("Empty dataframe returned")
                 
            # Reformat if necessary:
            # If group_by='ticker', columns are MultiIndex (Ticker, Price)
            # We might want valid data.
            return data
            
        except Exception as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt+1} failed ({e}). Retrying in 2s...")
                time.sleep(2)
            else:
                print(f"Failed to fetch data after {retries} attempts: {e}")
                return pd.DataFrame()

def fetch_etf_holdings(ticker, retries=3):
    """
    Fetches the top 10 holdings for an ETF with retry logic.
    Returns a list of dicts: [{'symbol': 'AAPL', 'name': 'Apple Inc', 'percent': 0.15}, ...]
    """
    for attempt in range(retries):
        try:
            etf = yf.Ticker(ticker)
            # funds_data.top_holdings is a pandas dataframe if available
            
            holdings_df = etf.funds_data.top_holdings
            if holdings_df is not None and not holdings_df.empty:
                # Structure usually: Index=Symbol, Columns=['Name', 'Holding %']
                holdings = []
                
                percent_col = next((c for c in holdings_df.columns if '%' in c or 'holding' in c.lower()), None)
                name_col = next((c for c in holdings_df.columns if 'name' in c.lower()), None)
                
                for symbol, row in holdings_df.iterrows():
                    name = row[name_col] if name_col else "Unknown"
                    percent = row[percent_col] if percent_col else 0
                    
                    holdings.append({
                        'symbol': symbol,
                        'name': name,
                        'percent': percent
                    })
                return holdings
            else:
                 # If empty, maybe just no data, don't retry unless exception
                 print(f"No holdings data found for {ticker}")
                 return []
                 
        except Exception as e:
            if attempt < retries - 1:
                 time.sleep(1)
            else:
                print(f"Error fetching holdings for {ticker}: {e}")
                return []
    return []

def fetch_all_etf_holdings(tickers):
    """
    Fetches holdings for multiple ETFs in parallel.
    Returns a dict: {ticker: [holdings_list]}
    """
    print(f"Fetching holdings for {len(tickers)} ETFs in parallel...")
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_ticker = {executor.submit(fetch_etf_holdings, ticker): ticker for ticker in tickers}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                data = future.result()
                results[ticker] = data
            except Exception as e:
                print(f"Exception for {ticker}: {e}")
                results[ticker] = []
                
    return results
