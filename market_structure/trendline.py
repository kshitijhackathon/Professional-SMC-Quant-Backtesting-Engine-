"""
Trendline & Support/Resistance Detection Module

Combines traditional technical analysis with SMC by computing
slope-based support and resistance lines from recent swing points.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

class TrendlineAnalyzer:
    """
    Detects ascending (support) and descending (resistance) trendlines
    using the last N swing highs and swing lows.
    """

    def __init__(self, n_points: int = 2):
        """
        Args:
            n_points: Number of recent swings to connect for the trendline.
        """
        self.n_points = n_points

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trendline slopes for every candle.

        Adds the following columns:
            - 'Support_Trendline_Price': The price level of the ascending trendline at this time.
            - 'Resistance_Trendline_Price': The price level of the descending trendline at this time.

        Args:
            df: DataFrame containing Swing_High, Swing_Low, Close.

        Returns:
            DataFrame with trendline columns.
        """
        result = df.copy()
        result['Support_Trendline_Price'] = np.nan
        result['Resistance_Trendline_Price'] = np.nan

        # Gather indices of swing points
        swing_high_idx = list(result[result['Swing_High'] == True].index)
        swing_low_idx = list(result[result['Swing_Low'] == True].index)

        # Convert index to integer position for math calculations
        data_len = len(result)

        # Loop through the DataFrame to calculate dynamic trendlines
        for i in range(data_len):
            current_time_idx = i

            # === Ascending Support Trendline (Connecting Swing Lows) ===
            lows_before = [x for x in swing_low_idx if x < i]
            if len(lows_before) >= self.n_points:
                last_lows = lows_before[-self.n_points:]
                # Calculate slope (m) and intercept (c) using linear regression
                x_coords = np.array([result.index.get_loc(l) for l in last_lows])
                y_coords = np.array([result.loc[l, 'Low'] for l in last_lows])
                
                if len(x_coords) > 1:
                    slope, intercept = np.polyfit(x_coords, y_coords, 1)
                    # Project price at current point
                    projected_price = slope * current_time_idx + intercept
                    result.at[result.index[i], 'Support_Trendline_Price'] = projected_price

            # === Descending Resistance Trendline (Connecting Swing Highs) ===
            highs_before = [x for x in swing_high_idx if x < i]
            if len(highs_before) >= self.n_points:
                last_highs = highs_before[-self.n_points:]
                x_coords = np.array([result.index.get_loc(h) for h in last_highs])
                y_coords = np.array([result.loc[h, 'High'] for h in last_highs])
                
                if len(x_coords) > 1:
                    slope, intercept = np.polyfit(x_coords, y_coords, 1)
                    projected_price = slope * current_time_idx + intercept
                    result.at[result.index[i], 'Resistance_Trendline_Price'] = projected_price

        return result