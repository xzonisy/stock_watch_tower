from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init()

def generate_sector_report(ranked_df):
    """
    Generates the sector ranking report as a string.
    """
    output = []
    output.append("每週板塊輪動監測")
    output.append("=" * 40)
    
    table_data = []
    
    # We expect columns: ['4w', '12w', 'RS_4w', 'RS_12w', 'Score']
    # We want to show Rank, Ticker, 4w%, 12w%, Score
    
    # Reset index to get the ticker as a column
    ranked_df = ranked_df.reset_index()
    # The first column is the ticker, rename it to 'Sector' regardless of its original name
    ranked_df.rename(columns={ranked_df.columns[0]: 'Sector'}, inplace=True)
    
    for i, row in ranked_df.iterrows():
        rank = i + 1
        ticker = row['Sector']
        perf_4w = f"{row['4w']:.2%}" if row['4w'] else "N/A"
        perf_12w = f"{row['12w']:.2%}" if row['12w'] else "N/A"
        score = f"{row['Score']:.4f}"
        
        # Color coding (removed for string output to Discord/File, keep simple text or just emojis if needed)
        # For console print we can add color, but for Discord we need plain text or markdown code blocks
        
        row_data = [
            rank,
            ticker,
            perf_4w,
            perf_12w,
            score
        ]
        table_data.append(row_data)
        
    headers = ["排名", "板塊", "4週表現", "12週表現", "RS分數"]
    
    output.append(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    
    output.append("\n前三名：關注區域 (Focus Area)")
    output.append("後三名：避免/黑名單 (Avoid/Blacklist)")
    
    return "\n".join(output)

def print_sector_ranking(ranked_df):
    """
    Prints the sector ranking in a tabular format (Wrapped version with color).
    """
    # For simplicity, we just print the colored version directly as before, 
    # OR we use the generate function and print it. 
    # Let's keep the colored version for console and use generate for Discord.
    # Actually, to avoid code duplication, we could have one source of truth, but colorama complicates string return.
    # Let's keep the original logic for console printing and add the string generator.
    
    print("\n" + Style.BRIGHT + "每週板塊輪動監測" + Style.RESET_ALL)
    print("=" * 40)
    
    table_data = []
    
    # Check if already reset (depends on how it's passed) -> It is passed as index=Ticker usually.
    # But generate_sector_report resets it. We should pass a copy or handle it.
    df = ranked_df.copy()
    df = df.reset_index()
    df.rename(columns={df.columns[0]: 'Sector'}, inplace=True)
    
    for i, row in df.iterrows():
        rank = i + 1
        ticker = row['Sector']
        perf_4w = f"{row['4w']:.2%}" if row['4w'] else "N/A"
        perf_12w = f"{row['12w']:.2%}" if row['12w'] else "N/A"
        score = f"{row['Score']:.4f}"
        
        # Color coding
        color = ""
        if rank <= 3:
            color = Fore.GREEN
        elif rank > len(df) - 3:
            color = Fore.RED
            
        row_data = [
            f"{color}{rank}{Style.RESET_ALL}",
            f"{color}{ticker}{Style.RESET_ALL}",
            f"{color}{perf_4w}{Style.RESET_ALL}",
            f"{color}{perf_12w}{Style.RESET_ALL}",
            f"{color}{score}{Style.RESET_ALL}"
        ]
        table_data.append(row_data)
        
    headers = ["排名", "板塊", "4週表現", "12週表現", "RS分數"]
    
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    
    print("\n" + Fore.GREEN + "前三名：關注區域 (Focus Area)" + Style.RESET_ALL)
    print(Fore.RED + "後三名：避免/黑名單 (Avoid/Blacklist)" + Style.RESET_ALL)

def generate_stock_report(sector_results):
    """
    Generates the stock analysis report as a string.
    """
    output = []
    output.append("\n領先板塊個股篩選 (Top Sector Stock Screen)")
    output.append("篩選標準: 價格 > 50EMA & 21EMA (趨勢), 波動收縮 (Coiling)")
    output.append("=" * 60)
    
    for sector, stocks in sector_results.items():
        output.append(f"\n板塊: {sector}")
        
        good_setups = [s for s in stocks if s['results'] and s['results']['Score'] >= 2]
        
        if not good_setups:
            output.append("  無符合條件的個股 (No setups found)")
            continue
            
        table_data = []
        for s in good_setups:
            res = s['results']
            
            trend = "O" if res['Price > 50EMA'] and res['Price > 21EMA'] else "X"
            if res['Price > 50EMA'] and not res['Price > 21EMA']: trend = ">50,<21"
            
            coil = "Tight" if res['Contracting'] else "Normal"
            
            row = [
                s['ticker'],
                trend,
                coil,
                f"{res['Current Vol']:.2%}"
            ]
            table_data.append(row)
            
        headers = ["Ticker", "Trend", "Vol", "Vol %"]
        output.append(tabulate(table_data, headers=headers, tablefmt="simple"))
        
    return "\n".join(output)

def print_stock_analysis(sector_results):
    """
    Prints the analysis of individual stocks within the top sectors (Console version).
    """
    print("\n" + Style.BRIGHT + "領先板塊個股篩選 (Top Sector Stock Screen)" + Style.RESET_ALL)
    print("篩選標準: 價格 > 50EMA & 21EMA (趨勢), 波動收縮 (Coiling)")
    print("=" * 60)
    
    for sector, stocks in sector_results.items():
        print(f"\n{Style.BRIGHT}{Fore.YELLOW}板塊: {sector}{Style.RESET_ALL}")
        
        # Filter for "good" setups (Score >= 2)
        good_setups = [s for s in stocks if s['results'] and s['results']['Score'] >= 2]
        
        if not good_setups:
            print("  無符合條件的個股 (No setups found)")
            continue
            
        table_data = []
        for s in good_setups:
            res = s['results']
            
            # Trend Status
            trend = "✅" if res['Price > 50EMA'] and res['Price > 21EMA'] else "⚠️"
            if res['Price > 50EMA'] and not res['Price > 21EMA']: trend = "Above 50, Below 21"
            
            # Contraction
            coil = "🔥 Tight" if res['Contracting'] else "Normal"
            
            row = [
                s['ticker'],
                trend,
                coil,
                f"{res['Current Vol']:.2%}"
            ]
            table_data.append(row)
            
        headers = ["Ticker", "Trend (>21/50)", "Volatility", "Vol %"]
        print(tabulate(table_data, headers=headers, tablefmt="simple"))
