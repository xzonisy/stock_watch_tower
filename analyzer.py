import pandas as pd
import config

def calculate_returns(data):
    """
    Calculates returns over specified periods.
    """
    returns = pd.DataFrame(index=data.columns)
    
    # Calculate returns for each period in config
    for period_name, days in config.PERIODS.items():
        # Make sure we have enough data
        if len(data) > days:
            # pct_change is (curr - prev) / prev
            # We want change over 'days' periods
            # Data is daily, so we shift by 'days'
            # Note: 4 weeks is approx 20 trading days
            
            # current price
            current = data.iloc[-1]
            # price 'days' ago
            past = data.iloc[-days-1] 
            
            # Simple return
            ret = (current - past) / past
            returns[period_name] = ret
        else:
            returns[period_name] = None
            
    return returns

def rank_sectors(returns_df, benchmarks):
    """
    Ranks sectors based on relative strength vs benchmarks.
    Strategy: 
    1. Calculate average rank across 4w and 12w performance? 
    OR
    2. Rank by a composite score.
    
    The prompt says: "I rank them by relative strength against $SPY and $QQQ over the past 4 and 12 weeks."
    This is slightly ambiguous. Common RS usage: 
    (Sector % Change) - (Benchmark % Change)
    
    Let's calculate Excess Return vs SPY for both periods.
    Then rank by the average of (4w Excess + 12w Excess).
    """
    
    # Filter only sectors (exclude benchmarks from the ranking list itself, but use them for calculation)
    sector_tickers = config.SECTORS
    
    # Calculate RS vs SPY (primary benchmark)
    spy_ret = returns_df.loc['SPY']
    
    df = returns_df.loc[sector_tickers].copy()
    
    df['RS_4w'] = df['4w'] - spy_ret['4w']
    df['RS_12w'] = df['12w'] - spy_ret['12w']
    
    # Composite Score: Simple average of the two RS metrics
    # You could weight them, but equal weight is a good start.
    df['Score'] = (df['RS_4w'] + df['RS_12w']) / 2
    
    # Rank
    df = df.sort_values(by='Score', ascending=False)
    
    return df
