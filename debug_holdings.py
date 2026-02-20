
import yfinance as yf
import pandas as pd

def test_fetch(ticker):
    print(f"\n{'='*20}")
    print(f"Testing {ticker}")
    print(f"{'='*20}")
    
    try:
        etf = yf.Ticker(ticker)
        fd = etf.funds_data
        
        if fd and fd.top_holdings is not None:
            df = fd.top_holdings
            print("Columns:", df.columns)
            print("Index Name:", df.index.name)
            print(df.head())
        else:
            print("funds_data.top_holdings is None")
            
    except Exception as e:
        print(f"Error accessing funds_data: {e}")

if __name__ == "__main__":
    test_fetch("XLK")
