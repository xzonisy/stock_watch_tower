# 每週板塊輪動監測 (Weekly Sector Rotation Monitor)

這是一個 Python 腳本，用於監測美股板塊 ETF ($XLK, $XLF 等)，根據過去 4 週和 12 週相對於 $SPY 和 $QQQ 的表現進行排名。

## 安裝設定 (Setup)

1.  **安裝依賴套件 (Dependencies)**：確保已安裝所需的套件：
    ```bash
    pip install -r requirements.txt
    ```


2.  **設定 (Configuration)**：
    *   修改 `config.py` 來新增/移除板塊或調整分析週期。
    *   **Discord 通知 (可選)**：
        1.  在專案根目錄建立一個 `.env` 檔案。
        2.  加入您的 Webhook URL： `DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...`
    *   **啟用 GitHub Pages (重要)**：
        1.  進入 GitHub 專案頁面 > **Settings** (設定) > **Pages** (頁面)。
        2.  在 **Build and deployment** 下的 **Source** 選擇 **Deploy from a branch**。
        3.  在 **Branch** 選擇 **main** 以及 **/(root)**，然後點擊 **Save**。
        4.  等待幾分鐘，GitHub 會顯示您的網頁連結 (例如 `https://xzonisy.github.io/stock_watch_tower/`)。
    *   **啟用 GitHub Actions 自動化 (重要)**：
        1.  進入 GitHub 專案頁面 > **Settings** > **Secrets and variables** > **Actions**。
        2.  點擊 **New repository secret**。
        3.  **Name** 輸入 `DISCORD_WEBHOOK_URL`。
        4.  **Secret** 輸入您的 Discord Webhook URL。
        5.  點擊 **Add secret**。
        6.  現在系統會在每週六早上自動執行並更新網頁報告。



## 執行監測 (Running the Monitor)

要執行每週分析，請在終端機中執行以下指令：

```bash
python main.py
```

## 解讀輸出結果 (Interpreting the Output)

腳本將獲取最新數據並顯示板塊排名表。

-   **前三名 (綠色)**：相對於大盤表現最強的板塊。這些是您尋找個別股票機會（第一階段底部）的重點區域。
-   **後三名 (紅色)**：表現最弱的板塊。避免在這些區域持有多頭部位。

### 輸出範例 (Example Output)

- **Discord 通知**: 程式會發送一個包含連結與 PIN 碼的訊息到您的 Discord。
- **網頁報告**: 點擊連結並輸入 PIN 碼即可查看完整報告。

```text
========================================
每週板塊輪動監測
========================================
╒══════╤══════════╤═══════════╤════════════╤════════════╕
│ 排名 │ 板塊     │ 4週表現   │ 12週表現   │ RS分數     │
╞══════╪══════════╪═══════════╪════════════╪════════════╡
│ 1    │ XLK      │ 5.20%     │ 15.30%     │ 0.0450     │
├──────┼──────────┼───────────┼────────────┼────────────┤
│ 2    │ XLC      │ 4.80%     │ 12.10%     │ 0.0320     │
├──────┼──────────┼───────────┼────────────┼────────────┤
...
│ 11   │ XLE      │ -2.10%    │ -5.40%     │ -0.0850    │
╘══════╧══════════╧═══════════╧════════════╧════════════╛

前三名：關注區域 (Focus Area)
後三名：避免/黑名單 (Avoid/Blacklist)
```

## 個股篩選 (Individual Stock Screening)

腳本會自動分析前三大領先板塊中的主要成分股，並根據以下技術指標進行篩選：
-   **趨勢**: 股價 > 50 EMA 且 > 21 EMA。
-   **波動收縮 (Coiling)**: 檢查近期波動率是否低於歷史平均，尋找盤整待突破的標的。

### 個股輸出範例 (Stock Screen Output)

```text
領先板塊個股篩選 (Top Sector Stock Screen)
篩選標準: 價格 > 50EMA & 21EMA (趨勢), 波動收縮 (Coiling)
============================================================

板塊: XLK
Ticker    Trend (>21/50)    Volatility    Vol %
--------  ----------------  ------------  -------
MSFT      ✅                Normal        1.25%
NVDA      ✅                🔥 Tight      1.80%
...
```

## 下一步 (Next Steps)

-   **深入研究 (Drill Down)**：一旦程式篩選出潛在標的，請打開圖表確認是否符合「第一階段底部」型態。
-   **風險管理 (Risk Management)**：注意板塊輪動的警訊，如果領先板塊開始轉弱，應減少曝險。
