import config
import data_fetcher
import analyzer
import reporter
import sys

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
        returns = analyzer.calculate_returns(data)
        
        # 4. Rank Sectors
        ranked_sectors = analyzer.rank_sectors(returns, config.BENCHMARKS)
        
        # 5. Report
        reporter.print_sector_ranking(ranked_sectors)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
