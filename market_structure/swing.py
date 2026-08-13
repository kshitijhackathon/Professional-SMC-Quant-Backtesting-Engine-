"""
Swing High / Swing Low Detection

Detects raw swing points using a lookback window.
Outputs boolean columns 'Swing_High' and 'Swing_Low'.
"""

import pandas as pd


def detect_swings(df, lookback=3):
    """
    Identify swing highs and lows using a simple rolling window method.

    A bar is a swing high if its High is greater than all Highs in the lookback
    period on both left and right sides. Similarly for swing low.

    Args:
        df (pd.DataFrame): DataFrame with columns 'High' and 'Low'.
        lookback (int): Number of bars to check on each side.

    Returns:
        pd.DataFrame: Original DataFrame with two new boolean columns:
                      'Swing_High' and 'Swing_Low'.
    """
    df = df.copy()

    df["Swing_High"] = False
    df["Swing_Low"] = False

    for i in range(lookback, len(df) - lookback):
        current_high = df.iloc[i]["High"]
        current_low = df.iloc[i]["Low"]

        left_highs = df.iloc[i - lookback:i]["High"]
        right_highs = df.iloc[i + 1:i + lookback + 1]["High"]

        left_lows = df.iloc[i - lookback:i]["Low"]
        right_lows = df.iloc[i + 1:i + lookback + 1]["Low"]

        if current_high > left_highs.max() and current_high > right_highs.max():
            df.at[df.index[i], "Swing_High"] = True

        if current_low < left_lows.min() and current_low < right_lows.min():
            df.at[df.index[i], "Swing_Low"] = True

    return df