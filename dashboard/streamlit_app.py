import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from config import *
from data.loader import load_data
from market_structure.swing import detect_swings
from market_structure.structure import classify_market_structure
from market_structure.liquidity import detect_liquidity
from market_structure.bos import detect_bos
from market_structure.choch import detect_choch
from market_structure.fvg import detect_fvg
from market_structure.order_block import detect_order_blocks
from strategies.smc_strategy import generate_mtf_signals
from engine.backtest import BacktestEngine
from dashboard.chart import plot_chart

# -------------------- PAGE CONFIG & CUSTOM CSS --------------------
st.set_page_config(
    page_title="SMC Quant Backtester | Professional",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional dark theme with TradingView-inspired styling
st.markdown("""
<style>
    /* Global dark theme */
    .stApp {
        background-color: #0E1117;
        color: #EAEAEA;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1E2130 0%, #252A3A 100%);
        border: 1px solid #2D3548;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #4F9DFF;
    }
    div[data-testid="metric-container"] label {
        color: #8B95A8 !important;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFFFFF;
        font-size: 1.6rem;
        font-weight: 700;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4F9DFF, #2E6BFF);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6BB2FF, #4F9DFF);
        box-shadow: 0 4px 15px rgba(79, 157, 255, 0.4);
        transform: translateY(-1px);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1117 0%, #161B22 100%);
        border-right: 1px solid #2D3548;
    }
    [data-testid="stSidebar"] .st-bq {
        background-color: #1C2230;
        border-radius: 8px;
    }

    /* Chart containers */
    .chart-container {
        background: #151A23;
        border: 1px solid #2D3548;
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }

    /* DataFrame styling */
    .stDataFrame {
        border: 1px solid #2D3548;
        border-radius: 12px;
        overflow: hidden;
    }
    .stDataFrame table {
        background-color: #151A23;
    }
    .stDataFrame thead tr th {
        background-color: #1E2532 !important;
        color: #8B95A8 !important;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stDataFrame tbody tr {
        background-color: #151A23;
        color: #EAEAEA;
    }
    .stDataFrame tbody tr:hover {
        background-color: #1F2838;
    }

    /* Progress & spinner */
    .stProgress > div > div > div > div {
        background-color: #4F9DFF;
    }

    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        border-left: 4px solid #4F9DFF;
        padding-left: 15px;
        margin: 30px 0 15px 0;
    }

    /* Info boxes */
    .info-box {
        background: #1C2333;
        border-left: 4px solid #FFA726;
        border-radius: 0 8px 8px 0;
        padding: 15px;
        margin: 10px 0;
        color: #CFD8DC;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    with st.expander("🔍 Market Settings", expanded=True):
        st.metric("Symbol", SYMBOL)
        st.metric("Higher Timeframe", HTF_TIMEFRAME)
        st.metric("Lower Timeframe", LTF_TIMEFRAME)
        st.metric("Date Range", f"{START_DATE} → {END_DATE}")

    with st.expander("📐 Strategy Parameters", expanded=True):
        st.metric("Swing Lookback", SWING_LOOKBACK)
        st.metric("Risk:Reward", f"1:{RISK_REWARD}")
        st.metric("Risk per Trade", f"{RISK_PER_TRADE_PERCENT}%")
        st.metric("Initial Capital", f"${INITIAL_CAPITAL:,.0f}")
        st.metric("Commission", f"{COMMISSION:.2%}")

    st.markdown("---")
    st.caption("© 2025 QuantBacktester Pro | SMC Edition")

# -------------------- MAIN DASHBOARD --------------------
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 2.8rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px;">
        📊 SMC <span style="color: #4F9DFF;">Quant</span> Backtester
    </h1>
    <p style="font-size: 1.1rem; color: #8B95A8; margin-top: -10px;">
        1H Chart Structure • 5M Precision Entries • 1% Risk Management
    </p>
</div>
""", unsafe_allow_html=True)

# Status bar with current operation
status_placeholder = st.empty()

# -------------------- DATA PROCESSING --------------------
with st.spinner("🔄 Loading & analyzing market data..."):
    status_placeholder.info("📥 Loading 1H data & detecting structure...")
    df_1h = load_data(SYMBOL, START_DATE, END_DATE, interval=HTF_TIMEFRAME)
    df_1h = detect_swings(df_1h, SWING_LOOKBACK)
    df_1h = classify_market_structure(df_1h)
    df_1h = detect_liquidity(df_1h)
    df_1h = detect_bos(df_1h)
    df_1h = detect_choch(df_1h)
    df_1h = detect_fvg(df_1h)
    df_1h = detect_order_blocks(df_1h)

    status_placeholder.info("📥 Loading 5M data & detecting structure...")
    df_5m = load_data(SYMBOL, START_DATE, END_DATE, interval=LTF_TIMEFRAME)
    df_5m = detect_swings(df_5m, SWING_LOOKBACK)
    df_5m = classify_market_structure(df_5m)
    df_5m = detect_liquidity(df_5m)
    df_5m = detect_bos(df_5m)
    df_5m = detect_choch(df_5m)
    df_5m = detect_fvg(df_5m)
    df_5m = detect_order_blocks(df_5m)

    status_placeholder.info("⚡ Generating MTF signals & running backtest...")
    df_5m_signals = generate_mtf_signals(df_1h, df_5m, rr=RISK_REWARD)

status_placeholder.empty()  # remove status bar

# -------------------- 1H CHART SECTION --------------------
st.markdown('<div class="section-header">📈 1H Structure – Major FVG & Order Blocks</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    plot_chart(df_1h)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- BACKTEST METRICS --------------------
st.markdown('<div class="section-header">📊 5M Entry Backtest Summary (1% Risk/Trade)</div>', unsafe_allow_html=True)

engine = BacktestEngine(
    initial_capital=INITIAL_CAPITAL,
    commission=COMMISSION,
    risk_percent=RISK_PER_TRADE_PERCENT / 100.0
)
results = engine.run(df_5m_signals)

metrics = results['metrics']
trades_df = results['trades']

# Metric cards in a 3x2 grid
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    st.metric("📋 Total Trades", metrics['Total Trades'])
with col2:
    st.metric("🏆 Win Rate", f"{metrics['Win Rate']}%",
              delta=f"{metrics['Win Rate'] - 50:.1f}% vs 50%", delta_color="normal")
with col3:
    st.metric("📈 Profit Factor", metrics['Profit Factor'])
with col4:
    st.metric("💰 Total P&L", f"${metrics['Total P&L']:,.2f}",
              delta=f"{'Profit' if metrics['Total P&L'] > 0 else 'Loss'}", delta_color="normal")
with col5:
    st.metric("📉 Max Drawdown", f"{metrics['Max Drawdown']}%")
with col6:
    st.metric("📊 Sharpe Ratio", metrics['Sharpe Ratio'])

# Additional context
if metrics['Total Trades'] == 0:
    st.warning("No 5M entries triggered within the 1H OB zones. Try adjusting date range or lookback parameters.")

# -------------------- TRADE LOG --------------------
if not trades_df.empty:
    st.markdown('<div class="section-header">📜 5M Entry Trade Log</div>', unsafe_allow_html=True)

    # Color-code P&L column for quick visual feedback
    def color_pnl(val):
        color = '#4CAF50' if val > 0 else '#F44336' if val < 0 else '#8B95A8'
        return f'color: {color}; font-weight: 600'

    # Format the dataframe for display
    styled_df = trades_df.style.applymap(color_pnl, subset=['PnL']).format({
        'Entry Price': '{:.5f}',
        'Exit Price': '{:.5f}',
        'PnL': '${:.2f}',
        'Return %': '{:.2f}%'
    })

    # Use interactive table with column configuration
    st.dataframe(
        trades_df,
        use_container_width=True,
        height=450,
        column_config={
            "Entry Time": st.column_config.DatetimeColumn("Entry Time", format="DD/MM/YYYY HH:mm"),
            "Exit Time": st.column_config.DatetimeColumn("Exit Time", format="DD/MM/YYYY HH:mm"),
            "Entry Price": st.column_config.NumberColumn("Entry Price", format="%.5f"),
            "Exit Price": st.column_config.NumberColumn("Exit Price", format="%.5f"),
            "PnL": st.column_config.NumberColumn("PnL", format="$%.2f"),
            "Return %": st.column_config.NumberColumn("Return %", format="%.2f%%"),
            "Win": st.column_config.CheckboxColumn("Win", disabled=True)
        },
        hide_index=True
    )

    # Download button for trade log
    csv = trades_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Trade Log (CSV)",
        data=csv,
        file_name='smc_trade_log.csv',
        mime='text/csv',
    )
else:
    st.info("ℹ️ No trades were executed during the selected period.")

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #4F5B6B;'>"
    "Built with ❤️ using Streamlit | SMC Strategy • Multi-Timeframe Precision • Professional Risk Analytics"
    "</p>",
    unsafe_allow_html=True
)