"""
Break of Structure (BOS) Detection Module

BOS occurs when a new swing point breaks the last liquidity level in the direction of the trend.
- Bullish BOS: A new Swing High closes above the Liquidity High level.
- Bearish BOS: A new Swing Low closes below the Liquidity Low level.

This confirms the continuation of the current trend.
"""

import pandas as pd
import numpy as np


def detect_bos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify Break of Structure (BOS) signals based strictly on Swing Points.

    Adds the following columns:
        - 'BOS_Bullish': True if a Swing High closes above Liquidity_High.
        - 'BOS_Bearish': True if a Swing Low closes below Liquidity_Low.

    Args:
        df: DataFrame containing 'Liquidity_High', 'Liquidity_Low', 
            'Close', 'Swing_High', 'Swing_Low'.

    Returns:
        DataFrame with BOS columns added.
    """
    result = df.copy()
    
    result['BOS_Bullish'] = False
    result['BOS_Bearish'] = False

    for idx, row in result.iterrows():
        high_level = row.get('Liquidity_High')
        low_level = row.get('Liquidity_Low')
        close = row['Close']
        is_swing_high = row.get('Swing_High', False)
        is_swing_low = row.get('Swing_Low', False)

        # Bullish BOS: Only trigger if it is a Swing High breaking the level
        if not pd.isna(high_level) and is_swing_high and close > high_level:
            result.at[idx, 'BOS_Bullish'] = True

        # Bearish BOS: Only trigger if it is a Swing Low breaking the level
        if not pd.isna(low_level) and is_swing_low and close < low_level:
            result.at[idx, 'BOS_Bearish'] = True

    return result