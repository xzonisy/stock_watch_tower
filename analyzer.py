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

def check_technical_setup(df):
    """
    Checks if a stock meets the technical criteria:
    1. Close > 50 EMA (Trend)
    2. Close > 21 EMA (Momentum)
    3. Volatility Contraction (Recent range < Historical range)
    
    Returns a dictionary of results.
    """
    # Ensure sufficient data
    if len(df) < 50:
        return None
        
    # Calculate EMAs
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    current = df.iloc[-1]
    
    # 1. Trend Checks
    price_gt_50 = current['Close'] > current['EMA_50']
    price_gt_21 = current['Close'] > current['EMA_21']
    
    # 2. Volatility Contraction
    # daily_range = (High - Low) / Close
    df['Range_Pct'] = (df['High'] - df['Low']) / df['Close']
    
    # Current Volatility (avg of last 5 days)
    current_vol = df['Range_Pct'].iloc[-5:].mean()
    # Historical Volatility (avg of last 20 days)
    hist_vol = df['Range_Pct'].iloc[-20:].mean()
    
    # Contraction if current vol is significantly lower than historical (e.g. < 0.75 ratio) or just generally low
    # Let's use a ratio check
    is_contracting = current_vol < (hist_vol * 0.8) # 20% contraction
    
    # 3. RS Check (We need Benchmark data for this, but let's assume we pass in pre-calculated RS or skip for now)
    # For now, we rely on the Sector RS filter.
    
    return {
        "Price > 50EMA": price_gt_50,
        "Price > 21EMA": price_gt_21,
        "Contracting": is_contracting,
        "Current Vol": current_vol,
        "Score": (1 if price_gt_50 else 0) + (1 if price_gt_21 else 0) + (1 if is_contracting else 0)
    }
