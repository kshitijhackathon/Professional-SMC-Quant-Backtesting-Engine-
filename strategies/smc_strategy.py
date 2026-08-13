"""
SMC Multi-Timeframe Strategy (1H - 15M - 5M)
- TP1 = STRICT 3:1 (Only executes if 3:1 is achievable before next Resistance/Support)
- SL = Structural Support/Resistance (Liquidity Lows/Highs)
- TP2 = Liquidity Level (Remaining 50% book)
"""

import pandas as pd
import numpy as np


def generate_mtf_signals(df_1h, df_5m, rr=3.0):
    """
    Takes 1H DataFrame (with OB/FVG detected) and 5M DataFrame.
    """
    result = df_5m.copy()
    result['Signal'] = 'NONE'
    result['Entry_Price'] = np.nan
    result['Stop_Loss'] = np.nan
    result['TP_1'] = np.nan   # TP1 = 3:1
    result['TP_2'] = np.nan   # TP2 = Next Liquidity Level

    # Calculate 5M ATR and SMAs
    high = result['High']
    low = result['Low']
    close = result['Close']
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    atr_5m = tr.rolling(14).mean()
    result['SMA_50'] = result['Close'].rolling(50).mean()
    result['SMA_200'] = result['Close'].rolling(200).mean()

    # Map 1H OB levels to 5M timeframe
    active_zones = []

    for idx, row in df_1h.iterrows():
        if row.get('BOS_Bullish', False) or row.get('CHoCH_Bullish', False):
            ob_high = row.get('OB_High')
            ob_low = row.get('OB_Low')
            if not pd.isna(ob_high) and not pd.isna(ob_low):
                active_zones.append({'start_time': idx, 'entry_type': 'BUY', 'ob_high': ob_high, 'ob_low': ob_low})
        
        if row.get('BOS_Bearish', False) or row.get('CHoCH_Bearish', False):
            ob_high = row.get('OB_High')
            ob_low = row.get('OB_Low')
            if not pd.isna(ob_high) and not pd.isna(ob_low):
                active_zones.append({'start_time': idx, 'entry_type': 'SELL', 'ob_high': ob_high, 'ob_low': ob_low})

    for idx_5m, row_5m in result.iterrows():
        current_atr = atr_5m.loc[idx_5m] if not pd.isna(atr_5m.loc[idx_5m]) else 1.5
        sma_50 = row_5m.get('SMA_50')
        sma_200 = row_5m.get('SMA_200')
        current_close = row_5m['Close']
        
        # STRICT REGIME FILTER (Only trade in trend direction)
        is_bullish_regime = (not pd.isna(sma_50) and not pd.isna(sma_200) and sma_50 > sma_200 and current_close > sma_200)
        is_bearish_regime = (not pd.isna(sma_50) and not pd.isna(sma_200) and sma_50 < sma_200 and current_close < sma_200)

        for zone in reversed(active_zones):
            
            low_5m = row_5m['Low']
            high_5m = row_5m['High']
            ob_high = zone['ob_high']
            ob_low = zone['ob_low']
            
            # ----------------------------------------------------
            # BUY LOGIC
            # ----------------------------------------------------
            if zone['entry_type'] == 'BUY' and is_bullish_regime:
                if low_5m <= ob_high and high_5m >= ob_low:
                    entry = current_close
                    
                    # 1. 🔥 STRUCTURAL SL: Previous Swing Low (Support)
                    sl = row_5m.get('Liquidity_Low')
                    if pd.isna(sl) or sl >= entry:
                        sl = ob_low - (0.4 * current_atr) # fallback
                    
                    risk = entry - sl
                    if risk <= 0: continue
                    
                    # 2. 🔥 CHECK TARGET 1 (3:1) vs RESISTANCE
                    next_liq_high = row_5m.get('Liquidity_High')
                    rr_to_liq = (next_liq_high - entry) / risk if not pd.isna(next_liq_high) and next_liq_high > entry else 99
                    
                    # 💡 CRITICAL RULE: Trade SKIP if 3:1 target can't be reached before next Resistance
                    if rr_to_liq < 3.0:
                        continue
                    
                    # 3. SET TARGETS
                    tp1 = entry + (risk * 3.0)  # Strict 3:1 TP1
                    tp2 = next_liq_high if not pd.isna(next_liq_high) else entry + (risk * 5.0)
                    
                    # Risk must be healthy (0.3 ATR to 1.5 ATR)
                    if risk >= (0.3 * current_atr) and risk <= (1.5 * current_atr):
                        result.at[idx_5m, 'Signal'] = 'BUY'
                        result.at[idx_5m, 'Entry_Price'] = round(entry, 2)
                        result.at[idx_5m, 'Stop_Loss'] = round(sl, 2)
                        result.at[idx_5m, 'TP_1'] = round(tp1, 2)
                        result.at[idx_5m, 'TP_2'] = round(tp2, 2)
                        break

            # ----------------------------------------------------
            # SELL LOGIC
            # ----------------------------------------------------
            elif zone['entry_type'] == 'SELL' and is_bearish_regime:
                if low_5m <= ob_high and high_5m >= ob_low:
                    entry = current_close
                    
                    # 1. 🔥 STRUCTURAL SL: Previous Swing High (Resistance)
                    sl = row_5m.get('Liquidity_High')
                    if pd.isna(sl) or sl <= entry:
                        sl = ob_high + (0.4 * current_atr) # fallback
                    
                    risk = sl - entry
                    if risk <= 0: continue
                    
                    # 2. 🔥 CHECK TARGET 1 (3:1) vs SUPPORT
                    next_liq_low = row_5m.get('Liquidity_Low')
                    rr_to_liq = (entry - next_liq_low) / risk if not pd.isna(next_liq_low) and next_liq_low < entry else 99
                    
                    # 💡 CRITICAL RULE: Trade SKIP if 3:1 target can't be reached before next Support
                    if rr_to_liq < 3.0:
                        continue
                    
                    # 3. SET TARGETS
                    tp1 = entry - (risk * 3.0)  # Strict 3:1 TP1
                    tp2 = next_liq_low if not pd.isna(next_liq_low) else entry - (risk * 5.0)
                    
                    if risk >= (0.3 * current_atr) and risk <= (1.5 * current_atr):
                        result.at[idx_5m, 'Signal'] = 'SELL'
                        result.at[idx_5m, 'Entry_Price'] = round(entry, 2)
                        result.at[idx_5m, 'Stop_Loss'] = round(sl, 2)
                        result.at[idx_5m, 'TP_1'] = round(tp1, 2)
                        result.at[idx_5m, 'TP_2'] = round(tp2, 2)
                        break

    return result