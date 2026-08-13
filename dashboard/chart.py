"""
Charting module for 1-Hour structure visualization.
"""

import plotly.graph_objects as go
import pandas as pd


def plot_chart(df: pd.DataFrame):
    """
    Plot 1H candlestick chart with 1H Structure, FVG and Order Blocks.
    """
    fig = go.Figure()

    # 1. Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="1H Price"
        )
    )

    # 2. 1H Structure Labels (HH/HL/LH/LL)
    if "Structure_Type" in df.columns:
        hh = df[df["Structure_Type"] == "HH"]
        hl = df[df["Structure_Type"] == "HL"]
        lh = df[df["Structure_Type"] == "LH"]
        ll = df[df["Structure_Type"] == "LL"]

        if not hh.empty:
            fig.add_trace(go.Scatter(x=hh.index, y=hh["High"], mode="markers", name="1H HH", marker=dict(symbol="diamond", size=12, color="gold")))
        if not hl.empty:
            fig.add_trace(go.Scatter(x=hl.index, y=hl["Low"], mode="markers", name="1H HL", marker=dict(symbol="diamond", size=12, color="cyan")))
        if not lh.empty:
            fig.add_trace(go.Scatter(x=lh.index, y=lh["High"], mode="markers", name="1H LH", marker=dict(symbol="diamond", size=12, color="orange")))
        if not ll.empty:
            fig.add_trace(go.Scatter(x=ll.index, y=ll["Low"], mode="markers", name="1H LL", marker=dict(symbol="diamond", size=12, color="purple")))

    # 3. 1H FVG Visualization (3-candle gap)
    if "FVG_Bullish" in df.columns and "FVG_High" in df.columns and "FVG_Low" in df.columns:
        fvg_bull = df[df["FVG_Bullish"]]
        if not fvg_bull.empty:
            for idx in fvg_bull.index:
                fig.add_shape(
                    type="rect",
                    x0=idx - pd.Timedelta(hours=1),
                    x1=idx + pd.Timedelta(hours=1),
                    y0=fvg_bull.loc[idx, "FVG_Low"],
                    y1=fvg_bull.loc[idx, "FVG_High"],
                    fillcolor="rgba(0, 255, 0, 0.2)",
                    line=dict(width=2, color="lime"),
                    layer="below"
                )

    if "FVG_Bearish" in df.columns and "FVG_High" in df.columns and "FVG_Low" in df.columns:
        fvg_bear = df[df["FVG_Bearish"]]
        if not fvg_bear.empty:
            for idx in fvg_bear.index:
                fig.add_shape(
                    type="rect",
                    x0=idx - pd.Timedelta(hours=1),
                    x1=idx + pd.Timedelta(hours=1),
                    y0=fvg_bear.loc[idx, "FVG_Low"],
                    y1=fvg_bear.loc[idx, "FVG_High"],
                    fillcolor="rgba(255, 0, 0, 0.2)",
                    line=dict(width=2, color="red"),
                    layer="below"
                )

    # 4. 1H Order Block Visualization
    if "Order_Block_Bullish" in df.columns and "OB_High" in df.columns and "OB_Low" in df.columns:
        ob_bull = df[df["Order_Block_Bullish"]]
        if not ob_bull.empty:
            for idx in ob_bull.index:
                fig.add_shape(
                    type="rect",
                    x0=idx - pd.Timedelta(hours=2),
                    x1=idx + pd.Timedelta(hours=2),
                    y0=ob_bull.loc[idx, "OB_Low"],
                    y1=ob_bull.loc[idx, "OB_High"],
                    fillcolor="rgba(255, 255, 255, 0.1)",
                    line=dict(width=2, color="white", dash="dash"),
                    layer="below"
                )
    if "Order_Block_Bearish" in df.columns and "OB_High" in df.columns and "OB_Low" in df.columns:
        ob_bear = df[df["Order_Block_Bearish"]]
        if not ob_bear.empty:
            for idx in ob_bear.index:
                fig.add_shape(
                    type="rect",
                    x0=idx - pd.Timedelta(hours=2),
                    x1=idx + pd.Timedelta(hours=2),
                    y0=ob_bear.loc[idx, "OB_Low"],
                    y1=ob_bear.loc[idx, "OB_High"],
                    fillcolor="rgba(255, 255, 255, 0.1)",
                    line=dict(width=2, color="white", dash="dash"),
                    layer="below"
                )

    fig.update_layout(
        title="1H SMC Structure (Major OB & FVG)",
        template="plotly_dark",
        height=850,
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )

    fig.show()