from tabulate import tabulate
from colorama import Fore, Style, init
import config
import pandas as pd
import json
import base64
import os

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
            color = Fore.RED
        elif rank > len(df) - 3:
            color = Fore.GREEN
            
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
    
    print("\n" + Fore.RED + "前三名：關注區域 (Focus Area)" + Style.RESET_ALL)
    print(Fore.GREEN + "後三名：避免/黑名單 (Avoid/Blacklist)" + Style.RESET_ALL)

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
            

import base64
import json

def simple_encrypt(text, pin):
    """
    Simple XOR encryption with the PIN to prevent casual 'View Source' peeking.
    """
    # Simply convert PIN to string for key
    pin_str = str(pin)
    if not pin_str:
        return text 
        
    # Expand PIN to match text length
    key = (pin_str * (len(text) // len(pin_str) + 1))[:len(text)]
    
    encrypted_chars = []
    for t, k in zip(text, key):
        # XOR and keep within printable range if possible, or just use ordained values
        # We will base64 encode the result anyway, so raw bytes are fine.
        # However, to be safe with unicode strings, let's work with utf-8 bytes
        # Standard XOR on string characters might produce invalid unicode.
        pass
    
    # Better approach: XOR bytes
    text_bytes = text.encode('utf-8')
    key_bytes = key.encode('utf-8')
    
    encrypted_bytes = bytearray()
    for t, k in zip(text_bytes, key_bytes):
        encrypted_bytes.append(t ^ k)
        
    # Return as base64 string for safe embedding in HTML
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def generate_etf_detail_page(ticker, holdings_data, chinese_name):
    """
    Generates a detailed HTML page for a specific ETF.
    """
    
    # Format holdings table rows
    holdings_rows = ""
    for h in holdings_data:
        holdings_rows += f"<tr><td>{h['symbol']}</td><td>{h['name']}</td><td>{h['percent']:.2%}</td></tr>"
        
    html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ticker} - {chinese_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: #2d2d2d; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        h1 {{ color: #4caf50; border-bottom: 2px solid #444; padding-bottom: 10px; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #64b5f6; text-decoration: none; font-size: 1.1em; }}
        .back-link:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #444; }}
        th {{ background-color: #333; color: #4caf50; }}
        tr:hover {{ background-color: #383838; }}
    </style>
    <script>
        // Check if user is authorized (simple session check)
        if (!sessionStorage.getItem('unlocked')) {{
            window.location.href = '../index.html';
        }}
    </script>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">← Back to Main Report</a>
        
        <h1>{ticker} - {chinese_name}</h1>
        
        <h3>Top 10 Holdings</h3>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>% Assets</th>
                </tr>
            </thead>
            <tbody>
                {holdings_rows}
            </tbody>
        </table>
    </div>
</body>
</html>
    """
    return html

def generate_html(report_text, pin, ranked_df=None, sector_results=None):
    """
    Generates a password-protected HTML file with Interactive DataTables.
    """
    
    # Prepare structured data if available
    sectors_data = []
    if ranked_df is not None:
        df = ranked_df.copy()
        # Ensure Ticker is a column
        if 'Sector' not in df.columns:
            df = df.reset_index()
            # Assuming first col is Ticker if not named Sector
            if df.columns[0] != 'Sector':
                df.rename(columns={df.columns[0]: 'Sector'}, inplace=True)
                
        for i, row in df.iterrows():
            ticker = row['Sector']
            chinese_name = config.SECTOR_NAMES.get(ticker, ticker)
            sectors_data.append({
                'rank': i + 1,
                'ticker': ticker,
                'name': chinese_name,
                'perf_4w': row['4w'] if pd.notnull(row['4w']) else 0,
                'perf_12w': row['12w'] if pd.notnull(row['12w']) else 0,
                'score': row['Score']
            })
            
    frontend_data = {
        'sectors': sectors_data,
        'report_text': report_text
    }
    
    json_data = json.dumps(frontend_data)
    encrypted_content = simple_encrypt(json_data, pin)
    
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Watch Tower - 每週板塊監測 report</title>
    
    <!-- DataTables CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background-color: #2d2d2d; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        h1 {{ text-align: center; color: #4caf50; }}
        
        /* Login Area */
        #login-area {{ text-align: center; margin-top: 50px; }}
        input {{ padding: 10px; font-size: 1.2rem; border-radius: 5px; border: 1px solid #444; background: #333; color: white; width: 150px; text-align: center; }}
        button {{ padding: 10px 20px; font-size: 1.2rem; border-radius: 5px; border: none; background-color: #4caf50; color: white; cursor: pointer; margin-left: 10px; }}
        button:hover {{ background-color: #45a049; }}
        .error {{ color: #ff5252; margin-top: 10px; display: none; }}
        
        /* Content Area */
        #content-area {{ display: none; }}
        
        /* Table Styles */
        .table-container {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
        table.dataTable tbody tr {{ background-color: #2d2d2d; color: #e0e0e0; }}
        table.dataTable tbody tr:hover {{ background-color: #383838; }}
        table.dataTable thead th {{ border-bottom: 1px solid #444; color: #4caf50; }}
        table.dataTable td {{ border-bottom: 1px solid #444; }}
        
        /* Links */
        a {{ color: #64b5f6; text-decoration: none; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
        
        /* Utilities */
        .hidden-data {{ display: none; }}
        .metric-pos {{ color: #ff5252; }}
        .metric-neg {{ color: #81c784; }}
        
        /* Chart container */
        .chart-container {{ position: relative; height: 400px; width: 100%; margin-bottom: 30px; }}
    </style>
    
    <!-- jQuery & DataTables JS -->
    <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
</head>
<body>
    <div class="container">
        <h1>🔐 每週板塊輪動監測</h1>
        
        <div id="login-area">
            <p>請輸入 4 位數 PIN 碼以解鎖報告。</p>
            <input type="password" id="pin-input" maxlength="4" placeholder="PIN" inputmode="numeric" pattern="[0-9]*" autofocus>
            <button onclick="unlock()">解鎖</button>
            <p class="error" id="error-msg">PIN 碼錯誤</p>
        </div>

        <div id="content-area">
            <h3>📊 板塊表現概覽 (Sector Performance)</h3>
            <div class="chart-container">
                <canvas id="perfChart"></canvas>
            </div>
            
            <h3>📋 板塊輪動排名 (Rotation Ranking)</h3>
            <div class="table-container">
                <table id="sector-table" class="display" style="width:100%">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>代碼</th>
                            <th>名稱</th>
                            <th>4週表現</th>
                            <th>12週表現</th>
                            <th>RS 分數</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <hr style="margin: 30px 0; border-color: #444;">
            
            <h3>📝 完整文字報告 (Detailed Report)</h3>
            <pre id="raw-report" style="background: #111; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: Consolas;"></pre>
        </div>
    </div>
    
    <div id="encrypted-data" class="hidden-data">{encrypted_content}</div>

    <script>
        function unlock() {{
            const pin = document.getElementById('pin-input').value;
            const encryptedData = document.getElementById('encrypted-data').innerText;
            const errorMsg = document.getElementById('error-msg');
            
            try {{
                const decryptedJSON = simple_decrypt(encryptedData, pin);
                const data = JSON.parse(decryptedJSON);
                
                // If parse successful, show content
                document.getElementById('login-area').style.display = 'none';
                document.getElementById('content-area').style.display = 'block';
                
                // Set session storage for detail pages
                sessionStorage.setItem('unlocked', 'true');
                
                // Populate Raw Report
                document.getElementById('raw-report').innerText = data.report_text;
                
                // Populate Table
                const tableBody = document.querySelector('#sector-table tbody');
                data.sectors.forEach(sector => {{
                    const tr = document.createElement('tr');
                    
                    const p4Class = sector.perf_4w >= 0 ? 'metric-pos' : 'metric-neg';
                    const p12Class = sector.perf_12w >= 0 ? 'metric-pos' : 'metric-neg';
                    const scoreClass = sector.score > 0 ? 'metric-pos' : 'metric-neg';
                    
                    tr.innerHTML = `
                        <td>${{sector.rank}}</td>
                        <td><a href="pages/${{sector.ticker}}.html">${{sector.ticker}}</a></td>
                        <td>${{sector.name}}</td>
                        <td class="${{p4Class}}">${{(sector.perf_4w * 100).toFixed(2)}}%</td>
                        <td class="${{p12Class}}">${{(sector.perf_12w * 100).toFixed(2)}}%</td>
                        <td class="${{scoreClass}}"><strong>${{sector.score.toFixed(4)}}</strong></td>
                    `;
                    tableBody.appendChild(tr);
                }});
                
                // Initialize DataTables
                $('#sector-table').DataTable({{
                    paging: false,
                    searching: true,
                    info: false,
                    order: [[ 0, "asc" ]] // Sort by Rank by default
                }});
                
                // Render Chart
                renderChart(data.sectors);
                
                errorMsg.style.display = 'none';
                
            }} catch (e) {{
                errorMsg.style.display = 'block';
                console.error(e);
            }}
        }}

        function simple_decrypt(base64Text, pin) {{
            const encryptedBytes = Uint8Array.from(atob(base64Text), c => c.charCodeAt(0));
            const encoder = new TextEncoder();
            const pinBytes = encoder.encode(pin);
            const keyBytes = new Uint8Array(encryptedBytes.length);
            
            for (let i = 0; i < encryptedBytes.length; i++) {{
                keyBytes[i] = pinBytes[i % pinBytes.length];
            }}
            
            const decryptedBytes = new Uint8Array(encryptedBytes.length);
            for (let i = 0; i < encryptedBytes.length; i++) {{
                decryptedBytes[i] = encryptedBytes[i] ^ keyBytes[i];
            }}
            
            const decoder = new TextDecoder();
            return decoder.decode(decryptedBytes);
        }}
        
        function renderChart(sectors) {{
            // Sort by RS Score descending for chart visual
            // const sortedSectors = [...sectors].sort((a, b) => b.score - a.score); # Already sorted by rank
            const tags = sectors.map(s => s.ticker);
            const perf4w = sectors.map(s => s.perf_4w * 100);
            const perf12w = sectors.map(s => s.perf_12w * 100);
            
            const ctx = document.getElementById('perfChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: tags,
                    datasets: [
                        {{
                            label: '4週表現 %',
                            data: perf4w,
                            backgroundColor: 'rgba(255, 82, 82, 0.7)',
                            borderColor: 'rgba(255, 82, 82, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: '12週表現 %',
                            data: perf12w,
                            backgroundColor: 'rgba(76, 175, 80, 0.7)',
                            borderColor: 'rgba(76, 175, 80, 1)',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            grid: {{ color: '#444' }},
                            ticks: {{ color: '#e0e0e0' }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#e0e0e0' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#e0e0e0' }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Auto-login via session
        if (sessionStorage.getItem('unlocked')) {{
             const storedPin = sessionStorage.getItem('session_pin');
             if (storedPin) {{
                 document.getElementById('pin-input').value = storedPin;
             }}
        }}
        
        document.getElementById('pin-input').addEventListener('keypress', function (e) {{
            if (e.key === 'Enter') {{
                unlock();
                sessionStorage.setItem('session_pin', document.getElementById('pin-input').value);
            }}
        }});
        
        // Also save pin on click
        document.querySelector('button').addEventListener('click', function() {{
             sessionStorage.setItem('session_pin', document.getElementById('pin-input').value);
        }});
    </script>
</body>
</html>
    """
    return html_template
    """
    Generates a password-protected HTML file.
    The content is encrypted with the PIN, so 'View Source' shows garbage.
    """
    encrypted_content = simple_encrypt(report_text, pin)
    
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Watch Tower - Weekly Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
        .container {{ background-color: #2d2d2d; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); max-width: 800px; width: 100%; }}
        h1 {{ text-align: center; color: #4caf50; }}
        #login-area {{ text-align: center; }}
        input {{ padding: 10px; font-size: 1.2rem; border-radius: 5px; border: 1px solid #444; background: #333; color: white; width: 150px; text-align: center; }}
        button {{ padding: 10px 20px; font-size: 1.2rem; border-radius: 5px; border: none; background-color: #4caf50; color: white; cursor: pointer; margin-left: 10px; }}
        button:hover {{ background-color: #45a049; }}
        #content-area {{ white-space: pre-wrap; font-family: 'Consolas', 'Courier New', monospace; display: none; line-height: 1.5; }}
        .error {{ color: #ff5252; margin-top: 10px; display: none; }}
        pre {{ background: #111; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .hidden-data {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Weekly Analysis Report</h1>
        
        <div id="login-area">
            <p>Please enter the 4-digit PIN from Discord to view the report.</p>
            <input type="password" id="pin-input" maxlength="4" placeholder="PIN">
            <button onclick="unlock()">Unlock</button>
            <p class="error" id="error-msg">Incorrect PIN</p>
        </div>

        <div id="content-area"></div>
    </div>
    
    <div id="encrypted-data" class="hidden-data">{encrypted_content}</div>

    <script>
        function unlock() {{
            const pin = document.getElementById('pin-input').value;
            const encryptedData = document.getElementById('encrypted-data').innerText;
            const errorMsg = document.getElementById('error-msg');
            
            try {{
                const decryptedHTML = simple_decrypt(encryptedData, pin);
                
                // Simple validation check: Report usually starts with specific headers
                if (decryptedHTML.includes("每週板塊輪動監測")) {{
                    document.getElementById('login-area').style.display = 'none';
                    const contentArea = document.getElementById('content-area');
                    contentArea.style.display = 'block';
                    contentArea.innerHTML = '<pre>' + decryptedHTML + '</pre>';
                    errorMsg.style.display = 'none';
                }} else {{
                    throw new Error("Decryption failed");
                }}
            }} catch (e) {{
                errorMsg.style.display = 'block';
                console.error(e);
            }}
        }}

        function simple_decrypt(base64Text, pin) {{
            // Decode Base64
            const encryptedBytes = Uint8Array.from(atob(base64Text), c => c.charCodeAt(0));
            
            // Prepare Key Bytes
            const encoder = new TextEncoder();
            const pinBytes = encoder.encode(pin);
            const keyBytes = new Uint8Array(encryptedBytes.length);
            
            for (let i = 0; i < encryptedBytes.length; i++) {{
                keyBytes[i] = pinBytes[i % pinBytes.length];
            }}
            
            // XOR Decrypt
            const decryptedBytes = new Uint8Array(encryptedBytes.length);
            for (let i = 0; i < encryptedBytes.length; i++) {{
                decryptedBytes[i] = encryptedBytes[i] ^ keyBytes[i];
            }}
            
            // Decode UTF-8
            const decoder = new TextDecoder();
            return decoder.decode(decryptedBytes);
        }}
        
        // Allow Enter key
        document.getElementById('pin-input').addEventListener('keypress', function (e) {{
            if (e.key === 'Enter') {{
                unlock();
            }}
        }});
    </script>
</body>
</html>
    """
    return html_template
