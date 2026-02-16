from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init()

def print_sector_ranking(ranked_df):
    """
    Prints the sector ranking in a tabular format.
    Highlights Top 3 in Green and Bottom 3 in Red.
    """
    print("\n" + Style.BRIGHT + "每週板塊輪動監測" + Style.RESET_ALL)
    print("=" * 40)
    
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
        
        # Color coding
        color = ""
        if rank <= 3:
            color = Fore.GREEN
        elif rank > len(ranked_df) - 3:
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
