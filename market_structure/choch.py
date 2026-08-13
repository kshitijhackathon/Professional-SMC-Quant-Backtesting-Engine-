"""
Change of Character (CHoCH) Detection Module

CHoCH occurs when price breaks the last liquidity level in the OPPOSITE direction 
of the current trend, signaling a potential trend reversal.
- Bullish CHoCH: In a downtrend, a Swing High closes above the Liquidity High.
- Bearish CHoCH: In an uptrend, a Swing Low closes below the Liquidity Low.
"""

import pandas as pd
import numpy as np


def detect_choch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify Change of Character (CHoCH) signals strictly based on Swing Points.

    Adds the following columns:
        - 'CHoCH_Bullish': True if Swing High breaks Liquidity_High while Trend is Bearish.
        - 'CHoCH_Bearish': True if Swing Low breaks Liquidity_Low while Trend is Bullish.

    Args:
        df: DataFrame containing 'Liquidity_High', 'Liquidity_Low', 'Trend', 
            'Close', 'Swing_High', 'Swing_Low'.

    Returns:
        DataFrame with CHoCH columns added.
    """
    result = df.copy()
    
    result['CHoCH_Bullish'] = False
    result['CHoCH_Bearish'] = False

    for idx, row in result.iterrows():
        trend = row.get('Trend')
        high_level = row.get('Liquidity_High')
        low_level = row.get('Liquidity_Low')
        close = row['Close']
        is_swing_high = row.get('Swing_High', False)
        is_swing_low = row.get('Swing_Low', False)

        # Bullish CHoCH: Bearish trend mein Swing High, Liquidity High ko tod raha hai
        if trend == 'Bearish' and is_swing_high and not pd.isna(high_level) and close > high_level:
            result.at[idx, 'CHoCH_Bullish'] = True

        # Bearish CHoCH: Bullish trend mein Swing Low, Liquidity Low ko tod raha hai
        if trend == 'Bullish' and is_swing_low and not pd.isna(low_level) and close < low_level:
            result.at[idx, 'CHoCH_Bearish'] = True

    return result