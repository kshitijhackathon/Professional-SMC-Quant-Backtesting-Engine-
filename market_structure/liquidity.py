"""
Liquidity Detection Module

This module identifies liquidity levels (previous swing highs and lows) based on
the market structure. It tracks where the smart money is likely to target
and detects when price raids these levels (Liquidity Raid).
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

class LiquidityAnalyzer:
    """
    Analyzes liquidity levels from market structure points.

    Attributes:
        _last_structure_high (float): Price of the last swing high (HH or LH).
        _last_structure_low (float): Price of the last swing low (HL or LL).
        _last_high_idx (int): Index of the last swing high.
        _last_low_idx (int): Index of the last swing low.
    """

    def __init__(self):
        """Initialize the liquidity analyzer."""
        self._reset_state()

    def _reset_state(self) -> None:
        """Reset internal state."""
        self._last_structure_high: Optional[float] = None
        self._last_structure_low: Optional[float] = None
        self._last_high_idx: Optional[int] = None
        self._last_low_idx: Optional[int] = None

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect liquidity levels and liquidity raids in the DataFrame.

        Adds the following columns:
            - 'Liquidity_High': Price of the last significant swing high.
            - 'Liquidity_Low': Price of the last significant swing low.
            - 'Liquidity_Raid_High': True if High crosses the Liquidity_High level.
            - 'Liquidity_Raid_Low': True if Low crosses the Liquidity_Low level.

        Args:
            df: DataFrame containing 'Structure_Type', 'High', 'Low' columns.

        Returns:
            DataFrame with liquidity columns added.
        """
        result = df.copy()
        
        # Initialize columns
        result['Liquidity_High'] = np.nan
        result['Liquidity_Low'] = np.nan
        result['Liquidity_Raid_High'] = False
        result['Liquidity_Raid_Low'] = False

        self._reset_state()

        # Iterate through the dataframe
        for idx, row in result.iterrows():
            structure_type = row.get('Structure_Type')
            current_high = row['High']
            current_low = row['Low']

            # 1. Update Liquidity levels based on new structure points
            if structure_type in ['HH', 'LH']:
                # This is a new swing high. The previous high becomes liquidity.
                if self._last_structure_high is not None:
                    # Store the previous high as liquidity for future bars
                    result.at[idx, 'Liquidity_High'] = self._last_structure_high
                
                # Update the last structure high to current
                self._last_structure_high = current_high
                self._last_high_idx = idx

            elif structure_type in ['HL', 'LL']:
                # This is a new swing low. The previous low becomes liquidity.
                if self._last_structure_low is not None:
                    # Store the previous low as liquidity for future bars
                    result.at[idx, 'Liquidity_Low'] = self._last_structure_low
                
                # Update the last structure low to current
                self._last_structure_low = current_low
                self._last_low_idx = idx

            else:
                # If not a structure point, carry forward the last known levels
                if self._last_structure_high is not None:
                    result.at[idx, 'Liquidity_High'] = self._last_structure_high
                if self._last_structure_low is not None:
                    result.at[idx, 'Liquidity_Low'] = self._last_structure_low

            # 2. Check for Liquidity Raids
            # If current high crosses the last liquidity high level
            if self._last_structure_high is not None and current_high > self._last_structure_high:
                result.at[idx, 'Liquidity_Raid_High'] = True

            # If current low crosses the last liquidity low level
            if self._last_structure_low is not None and current_low < self._last_structure_low:
                result.at[idx, 'Liquidity_Raid_Low'] = True

        return result

# =========================================================================
# Convenience Functions
# =========================================================================

def detect_liquidity(df: pd.DataFrame) -> pd.DataFrame:
    """
    One-liner to add liquidity columns to a structure-classified DataFrame.

    Args:
        df: DataFrame with Structure_Type, High, Low columns.

    Returns:
        DataFrame with Liquidity_High, Liquidity_Low, Raid columns.
    """
    analyzer = LiquidityAnalyzer()
    return analyzer.detect(df)