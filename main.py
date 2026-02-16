import config
import data_fetcher
import analyzer
import reporter
import sys
import pandas as pd # Added for type checking logic

def main():
    try:
        # 1. Define Tickers
        all_tickers = config.SECTORS + config.BENCHMARKS
        
        # 2. Fetch Data
        # We need enough data for 12 weeks calculation. 
        # 12 weeks = ~60 trading days. '6mo' is safe.
        data = data_fetcher.fetch_data(all_tickers, period="6mo")
        
        if data.empty:
            print("No data fetched. Exiting.")
            sys.exit(1)
            
        # 3. Calculate Returns
        # We need to handle the fact that 'data' might be MultiIndex (if >1 ticker) or single index
        # For sector analysis, we only want 'Close' prices.
        
        sector_data = data
        if isinstance(data.columns, pd.MultiIndex):
            # Extract 'Close' level
            sector_data = data['Close']
        else:
            # Single ticker or flat index, assume it has 'Close' if fetched with OHLC, 
            # or if it was just Close (old behavior), but we changed fetch_data to return full.
            if 'Close' in data.columns:
                 sector_data = data['Close'].to_frame() # This might be wrong if multiple tickers but flat? Unlikely with new yf.
                 # Actually if flat, it's one ticker. 
                 pass
        
        # calculate_returns expects a DataFrame where columns are Tickers and values are Prices.
        # If we passed multiple tickers to yf.download, data['Close'] matches this (Cols=Tickers).
        
        returns = analyzer.calculate_returns(sector_data)
        
        # 4. Rank Sectors
        ranked_sectors = analyzer.rank_sectors(returns, config.BENCHMARKS)
        
        # 5. Report
        reporter.print_sector_ranking(ranked_sectors)
        
        # 6. Drill Down (Phase 2)
        # Get Top 3 Sectors
        # ranked_sectors has a column 'Sector' after reset_index in reporter, but here it is the index
        top_3_sectors = ranked_sectors.index[:3].tolist()
        
        sector_results = {}
        
        print("\n正在分析領先板塊成分股 (Analyzing Top Sector Components)...")
        
        for sector in top_3_sectors:
            print(f"  Fetching {sector} holdings...")
            holdings = config.SECTOR_HOLDINGS.get(sector, [])
            if not holdings:
                continue
                
            # Fetch data for holdings
            stock_data = data_fetcher.fetch_data(holdings, period="1y") # Need > 200 days for 200SMA, user asked for 50SMA so 6mo is fine, but 1y safest.
            
            sector_res = []
            
            # Interact with the data structure
            is_multi = isinstance(stock_data.columns, pd.MultiIndex)
            
            for ticker in holdings:
                try:
                    if is_multi:
                        # Extract dataframe for single ticker
                        # Columns are (Price, Ticker) -> We want just Price cols
                        # xs might fail if ticker not found
                        try:
                            df = stock_data.xs(ticker, axis=1, level=1)
                        except KeyError:
                            continue
                    else:
                        # If single ticker in holdings (unlikely)
                        if len(holdings) == 1 and ticker == holdings[0]:
                             df = stock_data
                        else:
                             continue
                    
                    # Analyze
                    res = analyzer.check_technical_setup(df)
                    if res:
                        sector_res.append({'ticker': ticker, 'results': res})
                except Exception as e:
                    # print(f"Error analyzing {ticker}: {e}")
                    continue
                    
            sector_results[sector] = sector_res
            
        reporter.print_stock_analysis(sector_results)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
