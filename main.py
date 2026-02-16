import config
import data_fetcher
import analyzer
import reporter
import sys
import os # Added for env var check
import pandas as pd # Added for type checking logic

import notifier # Add import

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
        
        # Collect report for Discord
        full_report = reporter.generate_sector_report(ranked_sectors)
        
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
        
        # Append stock report to Discord message
        stock_report = reporter.generate_stock_report(sector_results)
        full_report += "\n" + stock_report
        
        # 7. Web Report & PIN (Phase 4)
        import random
        pin = str(random.randint(1000, 9999))
        print(f"\nGenerated PIN: {pin}")
        
        html_content = reporter.generate_html(full_report, pin)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("Generated index.html with PIN protection.")
        
        # Automate Deployment (Git Push)
        # Only run this if NOT in GitHub Actions (or if configured to do so explicitly)
        # In GitHub Actions, we might want to let the workflow handle the push to avoid auth issues or conflicts,
        # OR we can do it here if we set up the remote correctly.
        # But typically, workflows use a specific step for pushing.
        
        if not os.getenv("GITHUB_ACTIONS"):
            import subprocess
            try:
                print("Deploying to GitHub Pages (Local mode)...")
                subprocess.run(["git", "add", "index.html"], check=True)
                subprocess.run(["git", "commit", "-m", f"Update report for {pd.Timestamp.now().date()}"], check=False) # Check=False in case nothing changed
                subprocess.run(["git", "push"], check=True)
                print("Deployment successful.")
            except Exception as e:
                print(f"Deployment failed: {e}")
        else:
            print("Running in GitHub Actions. Skipping internal git push (Workflow will handle it).")

        
        # 8. Notify Discord
        print("\nSending report to Discord...")
        # GitHub Pages URL (Replace with actual user's URL if known, else usage guide says 'xzonisy.github.io/stock_watch_tower')
        # Based on remote origin: https://github.com/xzonisy/stock_watch_tower
        github_pages_url = "https://xzonisy.github.io/stock_watch_tower/"
        
        notifier.send_discord_report(full_report, pin=pin, url=github_pages_url)


        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
