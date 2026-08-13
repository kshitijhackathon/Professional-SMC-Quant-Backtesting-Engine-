# ==========================
# DATA SETTINGS
# ==========================

# 🔥 CHANGED TO GLD (Gold ETF) for testing
SYMBOL = "SPY"

# 5m, 15m data only available for last 55 days
START_DATE = "2026-06-01"
END_DATE = "2026-07-29"

# Multi-Timeframe Strategy
HTF_TIMEFRAME = "1h"
MTF_TIMEFRAME = "15m"
LTF_TIMEFRAME = "5m"

# ==========================
# MARKET STRUCTURE
# ==========================

SWING_LOOKBACK = 5

# ==========================
# BACKTEST SETTINGS
# ==========================

INITIAL_CAPITAL = 1000000        # 10 Lakh capital
COMMISSION = 0.00005             # 0.005% (10x kam, GLD ke liye realistic)

# ==========================
# RISK MANAGEMENT
# ==========================

RISK_REWARD = 3.0
RISK_PER_TRADE_PERCENT = 1.0     # 1% risk per trade (out of 10 Lakh)