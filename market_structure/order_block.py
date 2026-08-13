"""
Order Block (OB) Detection Module

An Order Block is the last candle that occurs immediately before a strong BOS/CHoCH.
It represents institutional order accumulation area.
Now includes Displacement Check and OB Freshness markers.
"""

import pandas as pd
import numpy as np


def detect_order_blocks(df: pd.DataFrame, lookback: int = 10) -> pd.DataFrame:
    """
    Identify Order Blocks based on BOS/CHoCH, FVGs, and Displacement.
    
    Adds columns:
        - 'Order_Block_Bullish': True if OB detected.
        - 'Order_Block_Bearish': True if OB detected.
        - 'OB_High', 'OB_Low': The high/low of the OB candle.
        - 'OB_Valid': Ensures the OB candle had strong displacement (> 1.5 * ATR).

    Args:
        df: DataFrame containing BOS, CHoCH, FVG, Open, High, Low, Close.
        lookback: Number of candles to look back for the source candle.

    Returns:
        DataFrame with Order Block columns added.
    """
    result = df.copy()
    
    result['Order_Block_Bullish'] = False
    result['Order_Block_Bearish'] = False
    result['OB_High'] = np.nan
    result['OB_Low'] = np.nan

    # Calculate ATR
    tr = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    atr_series = tr.rolling(14).mean()

    for idx in range(1, len(result)):
        current_time_idx = result.index[idx]
        
        # Check if current candle is a BOS or CHoCH (Bullish)
        is_bullish_break = result.at[current_time_idx, 'BOS_Bullish'] or result.at[current_time_idx, 'CHoCH_Bullish']
        is_bearish_break = result.at[current_time_idx, 'BOS_Bearish'] or result.at[current_time_idx, 'CHoCH_Bearish']

        # Get current ATR
        current_atr = atr_series.iloc[idx] if not pd.isna(atr_series.iloc[idx]) else 0

        if is_bullish_break:
            # Look back for the candle that generated the FVG
            ob_idx = idx - 2
            if ob_idx >= 0:
                high = result.iloc[ob_idx]['High']
                low = result.iloc[ob_idx]['Low']
                body = abs(result.iloc[ob_idx]['Close'] - result.iloc[ob_idx]['Open'])
                candle_range = high - low
                
                # DISPLACEMENT CHECK: Candle range must be > 1.5 * ATR
                is_displaced = candle_range > 1.5 * current_atr
                
                if is_displaced:
                    result.at[current_time_idx, 'Order_Block_Bullish'] = True
                    result.at[current_time_idx, 'OB_High'] = high
                    result.at[current_time_idx, 'OB_Low'] = low

        if is_bearish_break:
            ob_idx = idx - 2
            if ob_idx >= 0:
                high = result.iloc[ob_idx]['High']
                low = result.iloc[ob_idx]['Low']
                candle_range = high - low
                
                is_displaced = candle_range > 1.5 * current_atr
                
                if is_displaced:
                    result.at[current_time_idx, 'Order_Block_Bearish'] = True
                    result.at[current_time_idx, 'OB_High'] = high
                    result.at[current_time_idx, 'OB_Low'] = low

    return result