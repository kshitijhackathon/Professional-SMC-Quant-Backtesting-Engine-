"""
Fair Value Gap (FVG) Detection Module

FVG is a 3-candle pattern where there is a gap between the first and third candle.
- Bullish FVG: Candle 1's Low > Candle 3's High.
- Bearish FVG: Candle 1's High < Candle 3's Low.
These gaps act as high-probability support/resistance zones.
"""

import pandas as pd
import numpy as np


def detect_fvg(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify Fair Value Gaps (FVGs) in the price data.

    Adds the following columns:
        - 'FVG_Bullish': True if a Bullish FVG is detected.
        - 'FVG_Bearish': True if a Bearish FVG is detected.
        - 'FVG_High': The high price of the FVG zone.
        - 'FVG_Low': The low price of the FVG zone.

    Args:
        df: DataFrame with 'High' and 'Low' columns.

    Returns:
        DataFrame with FVG columns added.
    """
    result = df.copy()
    
    result['FVG_Bullish'] = False
    result['FVG_Bearish'] = False
    result['FVG_High'] = np.nan
    result['FVG_Low'] = np.nan

    # We need at least 3 candles to form an FVG
    for i in range(2, len(result)):
        # Candle 1 (i-2), Candle 2 (i-1), Candle 3 (i)
        high_prev_2 = result.iloc[i-2]['High']
        low_prev_2 = result.iloc[i-2]['Low']
        high_curr = result.iloc[i]['High']
        low_curr = result.iloc[i]['Low']

        # Bullish FVG: Low of candle 1 > High of candle 3
        if low_prev_2 > high_curr:
            result.at[result.index[i], 'FVG_Bullish'] = True
            result.at[result.index[i], 'FVG_High'] = low_prev_2
            result.at[result.index[i], 'FVG_Low'] = high_curr

        # Bearish FVG: High of candle 1 < Low of candle 3
        if high_prev_2 < low_curr:
            result.at[result.index[i], 'FVG_Bearish'] = True
            result.at[result.index[i], 'FVG_High'] = low_curr
            result.at[result.index[i], 'FVG_Low'] = high_prev_2

    return result