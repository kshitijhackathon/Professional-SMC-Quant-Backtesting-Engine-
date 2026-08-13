import plotly.graph_objects as go
import streamlit as st


def plot_chart(df):

    fig = go.Figure()

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        )
    )

    # Swing High
    swing_high = df[df["Swing_High"]]

    fig.add_trace(
        go.Scatter(
            x=swing_high.index,
            y=swing_high["High"],
            mode="markers",
            marker=dict(
                color="red",
                size=10,
                symbol="triangle-up"
            ),
            name="Swing High"
        )
    )

    # Swing Low
    swing_low = df[df["Swing_Low"]]

    fig.add_trace(
        go.Scatter(
            x=swing_low.index,
            y=swing_low["Low"],
            mode="markers",
            marker=dict(
                color="lime",
                size=10,
                symbol="triangle-down"
            ),
            name="Swing Low"
        )
    )

    fig.update_layout(
        title="Swing Detection",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=800
    )

    st.plotly_chart(fig, use_container_width=True)