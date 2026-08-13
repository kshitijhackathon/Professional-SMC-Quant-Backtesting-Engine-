# SMC Quant Backtester - Professional Multi-Timeframe Engine

A **production-grade** quantitative backtesting engine built purely in Python, implementing **Smart Money Concepts (SMC)** with institutional-grade risk management, multi-timeframe alignment, and dynamic position sizing.

This project is designed to showcase **Quant Development**, **Market Structure Analysis**, and **Algorithmic Trading** skills for interviews at top-tier quantitative trading firms.

---

## 🚀 Key Features

- **Multi-Timeframe Analysis (MTF):** 
  - `1H` Chart for High-Probability Market Structure (Major FVG & Order Blocks).
  - `5M` Chart for Precision Entries (Refinement & Liquidity Sweeps).
- **Smart Money Concepts (SMC) Implementation:**
  - Automatic Swing High/Low detection.
  - Market Structure classification (HH, HL, LH, LL).
  - Liquidity Level detection & Raid identification.
  - Break of Structure (BOS) & Change of Character (CHoCH) detection.
  - Fair Value Gap (FVG) detection (Bullish & Bearish).
  - Order Block (OB) detection with **Displacement Check** (1.5 ATR).
- **Advanced Risk Management:**
  - **1% Fixed Fractional Risk** per trade (Adjustable via `config.py`).
  - **Dynamic Position Sizing** based on Stop-Loss distance.
  - **Realistic Commission** (Entry + Exit Round Trip).
- **Advanced Trade Management:**
  - **75% Position Booking** at Target 1 (Strict 3:1 Risk-Reward).
  - **Automatic Breakeven Stop-Loss** after TP1.
  - **Trailing Stop-Loss** based on new Swing Highs/Lows.
  - **25% Runner** to Target 2 (Next Liquidity Level).
- **Professional Visualization:**
  - Interactive Plotly Dashboard integrated with Streamlit.
  - Dark mode charts with clear SMC markers (FVGs, OBs, Liquidity, BOS/CHoCH).
- **Backtesting Engine:**
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
└── reports/                        # (Auto-generated) Backtest results
