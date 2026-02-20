
import yfinance as yf
import pandas as pd

def test_fetch(ticker):
    print(f"\nTesting {ticker}")
    etf = yf.Ticker(ticker)
    fd = etf.funds_data
    if fd and fd.top_holdings is not None:
        print("Columns:", fd.top_holdings.columns.tolist())
        print(fd.top_holdings.head(2))
    else:
        print("No holdings found")

if __name__ == "__main__":
    test_fetch("XLK")
