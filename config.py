# Configuration for the Sector Rotation Monitor

# Sector ETFs
SECTORS = [
    "XLK",  # Technology
    "XLF",  # Financials
    "XLE",  # Energy
    "XLV",  # Health Care
    "XLY",  # Consumer Discretionary
    "XLP",  # Consumer Staples
    "XLI",  # Industrials
    "XLC",  # Communication Services
    "XLRE", # Real Estate
    "XLB",  # Materials
    "XLU"   # Utilities
]

# Benchmarks
BENCHMARKS = ["SPY", "QQQ"]

# Analysis Parameters
PERIODS = {
    "4w": 20,   # Approx 4 trading weeks
    "12w": 60   # Approx 12 trading weeks
}

# Top Holdings per Sector (Snapshot)
SECTOR_HOLDINGS = {
    "XLK": ["MSFT", "AAPL", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "AMD", "QCOM", "TXN"],
    "XLF": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "MS", "GS", "SCHW", "SPGI"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO", "OXY", "WMB"],
    "XLV": ["LLY", "UNH", "JNJ", "MRK", "ABBV", "TMO", "AMGN", "ISRG", "PFE", "DHR"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "MAR"],
    "XLP": ["PG", "COST", "PEP", "WMT", "KO", "PM", "MDLZ", "CL", "MO", "TGT"],
    "XLI": ["GE", "CAT", "UBER", "UNP", "HON", "BA", "ADP", "RTX", "DE", "LMT"],
    "XLC": ["GOOGL", "META", "NFLX", "DIS", "CMCSA", "VZ", "T", "TMUS", "CHTR", "WBD"],
    "XLRE": ["PLD", "AMT", "EQIX", "CCI", "O", "PSA", "SPG", "VIC", "DLR", "EQR"],
    "XLB": ["LIN", "SHW", "FCX", "APD", "ECL", "NEM", "DOW", "CTVA", "ALB", "PPG"],
    "XLU": ["NEE", "SO", "DUK", "SRE", "AEP", "D", "PEG", "ED", "EXC", "PCG"]
}
