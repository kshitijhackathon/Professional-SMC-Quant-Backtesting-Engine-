"""
Market Structure Classification Module

This module takes swing highs and swing lows from the swing detection module
and classifies them into Higher High (HH), Higher Low (HL), Lower High (LH),
and Lower Low (LL). It maintains the current trend state (Bullish/Bearish)
which serves as the foundation for Liquidity, BOS, CHoCH, FVG, and Order Blocks.

All functions are designed to be stateless or stateful as needed, with clear
separation of concerns.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple


class MarketStructureAnalyzer:
    """
    Analyzes market structure by labeling swing points and tracking trend.

    Attributes:
        swing_high_col (str): Name of boolean column for swing highs.
        swing_low_col (str): Name of boolean column for swing lows.
        _last_high (float): Price of the most recent swing high.
        _last_low (float): Price of the most recent swing low.
        _structure_points (List[Dict]): Chronological list of all structure points.
        _current_trend (str): Latest trend state ('Bullish', 'Bearish', or 'Neutral').
    """

    # Constants for structure labels
    HH = 'HH'   # Higher High
    HL = 'HL'   # Higher Low
    LH = 'LH'   # Lower High
    LL = 'LL'   # Lower Low

    # Trend states
    BULLISH = 'Bullish'
    BEARISH = 'Bearish'
    NEUTRAL = 'Neutral'

    def __init__(self, swing_high_col: str = 'Swing_High', swing_low_col: str = 'Swing_Low'):
        """
        Initialize the analyzer.

        Args:
            swing_high_col: Column name for swing high boolean indicator.
            swing_low_col: Column name for swing low boolean indicator.
        """
        self.swing_high_col = swing_high_col
        self.swing_low_col = swing_low_col
        self._reset_state()

    def _reset_state(self) -> None:
        """Reset internal state to start a fresh classification."""
        self._last_high: Optional[float] = None
        self._last_low: Optional[float] = None
        self._last_high_idx: Optional[int] = None
        self._last_low_idx: Optional[int] = None
        self._structure_points: List[Dict[str, Any]] = []
        self._current_trend: str = self.NEUTRAL

    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify all swing points in the DataFrame and add structure columns.

        Adds the following columns:
            - 'Structure_Type': HH, HL, LH, LL, or None (for non-swing rows).
            - 'Structure_Sequence': Integer sequence number for each swing point.
            - 'Trend': Trend at the time of each swing point.

        Args:
            df: DataFrame with OHLC and swing boolean columns.

        Returns:
            DataFrame with structure columns added.
        """
        result = df.copy()
        result['Structure_Type'] = None
        result['Structure_Sequence'] = np.nan
        result['Trend'] = self.NEUTRAL

        self._reset_state()
        swing_count = 0

        # Iterate through all rows chronologically
        for idx, row in result.iterrows():
            is_high = row.get(self.swing_high_col, False)
            is_low = row.get(self.swing_low_col, False)

            if not (is_high or is_low):
                continue

            # Determine price and label
            if is_high:
                price = row['High']
                label = self._classify_high(price)
            else:  # is_low
                price = row['Low']
                label = self._classify_low(price)

            # Update trend based on the new label
            self._update_trend(label)

            # Store the point in history
            point = {
                'index': idx,
                'timestamp': row.name,  # DataFrame index (usually datetime)
                'price': price,
                'type': 'High' if is_high else 'Low',
                'label': label,
                'trend': self._current_trend
            }
            self._structure_points.append(point)

            # Update last prices and indices
            if is_high:
                self._last_high = price
                self._last_high_idx = idx
            else:
                self._last_low = price
                self._last_low_idx = idx

            # Write to DataFrame
            swing_count += 1
            result.at[idx, 'Structure_Type'] = label
            result.at[idx, 'Structure_Sequence'] = swing_count
            result.at[idx, 'Trend'] = self._current_trend

        return result

    def _classify_high(self, price: float) -> str:
        """
        Classify a swing high relative to the previous swing high.

        Rules:
            - If no previous high exists, mark as HH (baseline).
            - If price > last high, mark as HH.
            - Otherwise, mark as LH.
        """
        if self._last_high is None:
            return self.HH
        return self.HH if price > self._last_high else self.LH

    def _classify_low(self, price: float) -> str:
        """
        Classify a swing low relative to the previous swing low.

        Rules:
            - If no previous low exists, mark as LL (baseline).
            - If price > last low, mark as HL.
            - Otherwise, mark as LL.
        """
        if self._last_low is None:
            return self.LL
        return self.HL if price > self._last_low else self.LL

    def _update_trend(self, label: str) -> None:
        """
        Update the trend state based on SMC rules.

        Rules:
            - HH or HL -> Bullish (price making higher highs or higher lows)
            - LL or LH -> Bearish (price making lower lows or lower highs)
        """
        if label in (self.HH, self.HL):
            self._current_trend = self.BULLISH
        elif label in (self.LL, self.LH):
            self._current_trend = self.BEARISH
        # Neutral is only initial state; it gets overwritten after first swing.

    # ------------------------------------------------------------------
    # Public accessors for downstream modules (Liquidity, BOS, etc.)
    # ------------------------------------------------------------------

    def get_structure_points(self) -> List[Dict[str, Any]]:
        """Return the complete chronological list of structure points."""
        return self._structure_points

    def get_current_trend(self) -> str:
        """Return the latest trend state."""
        return self._current_trend

    def get_last_point(self) -> Optional[Dict[str, Any]]:
        """Return the most recent structure point, or None if none exist."""
        return self._structure_points[-1] if self._structure_points else None

    def get_last_high(self) -> Tuple[Optional[float], Optional[int]]:
        """Return (price, index) of the last swing high."""
        return self._last_high, self._last_high_idx

    def get_last_low(self) -> Tuple[Optional[float], Optional[int]]:
        """Return (price, index) of the last swing low."""
        return self._last_low, self._last_low_idx


# =========================================================================
# Convenience Functions (for quick integration)
# =========================================================================

def classify_market_structure(
    df: pd.DataFrame,
    swing_high_col: str = 'Swing_High',
    swing_low_col: str = 'Swing_Low'
) -> pd.DataFrame:
    """
    One-liner to classify market structure on a DataFrame.

    Args:
        df: DataFrame containing OHLC and swing boolean columns.
        swing_high_col: Name of swing high boolean column.
        swing_low_col: Name of swing low boolean column.

    Returns:
        DataFrame with Structure_Type, Structure_Sequence, and Trend columns.
    """
    analyzer = MarketStructureAnalyzer(swing_high_col, swing_low_col)
    return analyzer.classify(df)


def get_latest_trend(df: pd.DataFrame) -> str:
    """
    Extract the most recent trend from a structure-classified DataFrame.

    Args:
        df: DataFrame that has been processed by classify_market_structure.

    Returns:
        'Bullish', 'Bearish', or 'Neutral' based on the last non-null Trend.
    """
    trend_series = df['Trend'].dropna()
    if trend_series.empty:
        return MarketStructureAnalyzer.NEUTRAL
    return trend_series.iloc[-1]


# -------------------------------------------------------------------------
# Standalone test (optional, can be removed in production)
# -------------------------------------------------------------------------
if __name__ == '__main__':
    # Quick test with dummy data
    data = {
        'High': [100, 102, 101, 105, 104, 106, 103],
        'Low':  [90,  92,  91,  95,  94,  96,  93],
        'Swing_High': [False, True, False, True, False, True, False],
        'Swing_Low':  [False, False, True, False, True, False, True]
    }
    dummy_df = pd.DataFrame(data)
    result = classify_market_structure(dummy_df)
    print(result[['High', 'Low', 'Swing_High', 'Swing_Low', 'Structure_Type', 'Trend']].dropna())