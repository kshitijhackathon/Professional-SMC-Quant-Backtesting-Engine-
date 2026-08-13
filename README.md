```markdown
# SMC Quant Backtester - Professional Multi-Timeframe Engine

A **production-grade** quantitative backtesting engine built purely in Python, implementing **Smart Money Concepts (SMC)** with institutional-grade risk management, multi-timeframe alignment, and dynamic position sizing.

This project is designed to showcase **Quant Development**, **Market Structure Analysis**, and **Algorithmic Trading** skills for interviews at top-tier quantitative trading firms.

---

## 🚀 Key Features

- **Multi-Timeframe Analysis (MTF):** 
  - `1H` (HTF) Chart for High-Probability Market Structure (Major FVG & Order Blocks).
  - `15M` (MTF) Chart for Structure Refinement.
  - `5M` (LTF) Chart for Precision Entries (Liquidity Sweeps & CHoCH).
- **Smart Money Concepts (SMC) Implementation:**
  - Automatic Swing High/Low detection.
  - Market Structure classification (HH, HL, LH, LL).
  - Liquidity Level detection & Raid identification.
  - Break of Structure (BOS) & Change of Character (CHoCH) detection.
  - Fair Value Gap (FVG) detection (Bullish & Bearish).
  - Order Block (OB) detection with **Displacement Check** (1.5 ATR).
- **Advanced Risk Management:**
  - **1% Fixed Fractional Risk** per trade (Adjustable via `config.py`).
  - **Dynamic Position Sizing** based on real-time Stop-Loss distance.
  - **Realistic Round-Trip Commission** (Entry + Exit).
- **Advanced Trade Management:**
  - **75% Position Booking** at Target 1 (Strict 3:1 Risk-Reward).
  - **Automatic Breakeven Stop-Loss** after TP1.
  - **Trailing Stop-Loss** based on new Swing Highs/Lows.
  - **25% Runner** to Target 2 (Next Liquidity Level).
- **Professional Visualization:**
  - Interactive Plotly Dashboard integrated with Streamlit.
  - Dark mode charts with clear SMC markers (FVGs, OBs, Liquidity, BOS/CHoCH).
- **Robust Backtesting Engine:**
  - Full trade log (Entry/Exit/Size/P&L).
  - Performance metrics (Win Rate, Profit Factor, Max Drawdown, Sharpe Ratio).

---

## 📁 Project Structure

```text
QuantBacktester/
│
├── app.py                          # Entry point (Legacy)
├── config.py                       # Configuration (Symbols, Timeframes, Risk)
├── README.md                       # Project Documentation
├── requirements.txt                # Python Dependencies
│
├── data/
│   └── loader.py                   # Yahoo Finance data loader (with fallback symbols)
│
├── market_structure/
│   ├── swing.py                    # Swing High/Low detection
│   ├── structure.py                # HH/HL/LH/LL classification
│   ├── liquidity.py                # Liquidity level detection
│   ├── bos.py                      # Break of Structure
│   ├── choch.py                    # Change of Character
│   ├── fvg.py                      # Fair Value Gap detection
│   ├── order_block.py              # Order Block detection (w/ Displacement)
│   └── trendline.py                # Support/Resistance Trendline detection
│
├── strategies/
│   └── smc_strategy.py             # Multi-Timeframe SMC Strategy (1H→5M)
│
├── risk/
│   ├── risk_manager.py             # Core risk logic
│   └── position_sizing.py          # Position size calculator
│
├── engine/
│   └── backtest.py                 # Advanced Backtesting Engine (1% Risk, 75% Book)
│
├── dashboard/
│   ├── chart.py                    # Plotly charting logic
│   └── streamlit_app.py            # Streamlit UI dashboard
│
└── reports/                        # (Auto-generated) Backtest results folder
```

---

## ⚙️ Installation & Setup (Step-by-Step)

### 1. Clone the Repository
Open your terminal (Git Bash / PowerShell / CMD) and run:

```bash
git clone https://github.com/kshitijhackathon/Professional-SMC-Quant-Backtesting-Engine-.git
cd Professional-SMC-Quant-Backtesting-Engine-
```

### 2. Create a Virtual Environment (Recommended)
Virtual environment ensures that your project dependencies don't conflict with other Python projects.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Create a file named `requirements.txt` in the root folder with the following content:

```text
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.28
plotly>=5.18.0
streamlit>=1.29.0
```

Then run the install command:

```bash
pip install -r requirements.txt
```

### 4. Configure Your Settings
Open `config.py` and change these parameters according to your preference:

```python
SYMBOL = "SPY"                  # Change to "GLD" (Gold), "BTC-USD" (Bitcoin), or "ES=F" (Futures)

# Date Range (Note: Intraday data like 5m/15m only supports the last 55 days)
START_DATE = "2026-06-01"
END_DATE = "2026-07-29"

# Multi-Timeframe Configuration
HTF_TIMEFRAME = "1h"            # Higher Timeframe (1 Hour for structure)
MTF_TIMEFRAME = "15m"           # Mid Timeframe (15 Minute for refinement)
LTF_TIMEFRAME = "5m"            # Lower Timeframe (5 Minute for precise entries)

INITIAL_CAPITAL = 1000000       # Starting account balance ($1,000,000)
COMMISSION = 0.00005            # 0.005% round-trip commission
RISK_REWARD = 3.0               # Fixed 3:1 Risk-to-Reward ratio for TP1
RISK_PER_TRADE_PERCENT = 1.0    # 1% risk per trade (of current capital)
```

---

## 🏃‍♂️ How to Run the Dashboard

Once everything is installed and configured, run the following command to start the Streamlit application:

```bash
streamlit run dashboard/streamlit_app.py
```

The app will automatically open in your browser at:

```text
http://localhost:8501
```

---

## 🧠 Strategy Logic (SMC MTF)

This engine implements a **3-Step Institutional SMC Flow**:

| Step | Timeframe | Action |
| :--- | :--- | :--- |
| **Step 1 (Structure)** | `1H` | Detect Major FVG, Major Order Block, and Market Structure (HH/HL). |
| **Step 2 (Refinement)** | `15M` | Wait for price to retrace into the `1H` OB/FVG zone. |
| **Step 3 (Entry)** | `5M` | Look for Liquidity Sweep + CHoCH/BOS on 5M. Trigger entry at FVG midpoint. |

**Trade Management:**
- **SL:** `Order Block Low/High - (0.25 * ATR)` with a strict minimum risk guard (0.15 points).
- **TP1:** 3:1 Risk-Reward. **75%** of position is booked here.
- **Trailing:** Once TP1 hits, SL moves to **Breakeven** and trails with every new Swing High/Low.
- **TP2:** Remaining **25%** position targets the next Liquidity Level.

---

## 📊 Backtest Metrics Explained

| Metric | Description |
| :--- | :--- |
| **Total Trades** | Number of executed trades. |
| **Win Rate** | Percentage of winning trades (including partial TP1). |
| **Profit Factor** | Gross Profit / Gross Loss. (>1.5 is good, >2.0 is excellent). |
| **Total P&L** | Net realized profit/loss in USD. |
| **Max Drawdown** | The largest peak-to-trough drop in equity. |
| **Sharpe Ratio** | Risk-adjusted return (Annualized). |

---

## 🛠️ Full Configuration Options (`config.py`)

You can easily tune the strategy without changing core code:

```python
SYMBOL = "SPY"                  # Ticker symbol
HTF_TIMEFRAME = "1h"            # Macro Structure Timeframe
MTF_TIMEFRAME = "15m"           # Refinement Timeframe
LTF_TIMEFRAME = "5m"            # Entry Timeframe

INITIAL_CAPITAL = 1000000       # 1M USD
COMMISSION = 0.00005            # 0.005% (Round trip)
RISK_REWARD = 3.0               # Target 1 RR ratio
RISK_PER_TRADE_PERCENT = 1.0    # 1% risk per trade
SWING_LOOKBACK = 5              # Lookback for detecting Swing Highs/Lows
```

---

## 📌 Future Roadmap

- [x] Swing Detection
- [x] SMC Structure (HH/HL/LH/LL)
- [x] Liquidity & Raids
- [x] BOS & CHoCH
- [x] FVG & Order Blocks (Displacement Check)
- [x] Multi-Timeframe Strategy (1H → 5M)
- [x] Advanced Position Sizing (1% Risk)
- [x] 75% Partial Booking & Trailing SL
- [ ] Walk-forward optimization
- [ ] Trade journal export (CSV/JSON)
- [ ] Telegram trade alerts

---

## 🤝 Contributing

This project is built for demonstration and educational purposes. Contributions are welcome. Feel free to fork and submit a Pull Request.

---

## 📜 License

MIT License. Free to use for personal and commercial projects.
```
<img width="1918" height="968" alt="image" src="https://github.com/user-attachments/assets/4088998b-ad23-4354-9221-1645b2774e4c" />
<img width="1918" height="971" alt="image" src="https://github.com/user-attachments/assets/3870f388-589c-4293-bad6-b8f5380d0f01" />
<img width="1918" height="970" alt="image" src="https://github.com/user-attachments/assets/fa712be7-b82d-462c-8e95-a7c0e575a5ac" />
<img width="1917" height="967" alt="image" src="https://github.com/user-attachments/assets/a1e65690-ad1c-4801-b0f0-568b950d38f5" />




