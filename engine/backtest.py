"""
Professional SMC Backtesting Engine
Features: 
- 1% Fixed Fractional Position Sizing
- Round Trip Commission (Entry + Exit)
- TP1 = 3:1 (75% book, SL to Breakeven)
- Trailing SL (Last Swing)
- TP2 = Liquidity (Remaining 25% book)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class BacktestEngine:
    """
    A robust backtesting engine with partial position management.
    """

    def __init__(self, initial_capital: float = 100000.0, commission: float = 0.0005, risk_percent: float = 0.01):
        self.initial_capital = initial_capital
        self.commission = commission
        self.risk_percent = risk_percent  # 1% default
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        self.trades = []
        self.equity_curve = []
        
        data = df.copy()
        capital = self.initial_capital
        current_position = None 

        for idx in range(len(data)):
            row = data.iloc[idx]
            
            # --- CLOSE POSITION / MANAGE PHASES ---
            if current_position:
                current_high = row['High']
                current_low = row['Low']
                size = current_position['size']
                
                # PHASE 1: Full size, Target = TP1 (3:1)
                if current_position['phase'] == 1:
                    tp1_hit = False
                    sl_hit = False
                    exit_price = 0.0

                    if current_position['type'] == 'BUY':
                        if current_low <= current_position['sl']:
                            sl_hit = True
                            exit_price = current_position['sl']
                        elif current_high >= current_position['tp1']:
                            tp1_hit = True
                            exit_price = current_position['tp1']
                    else: # SELL
                        if current_high >= current_position['sl']:
                            sl_hit = True
                            exit_price = current_position['sl']
                        elif current_low <= current_position['tp1']:
                            tp1_hit = True
                            exit_price = current_position['tp1']

                    # ACTION: SL HIT -> FULL LOSS
                    if sl_hit:
                        pnl = self._calculate_pnl(current_position['entry'], exit_price, current_position['type'], size)
                        capital += pnl
                        self.trades.append(self._create_trade_record(idx, current_position, exit_price, pnl, 'Loss'))
                        current_position = None

                    # ACTION: TP1 HIT -> 75% PROFIT, SL -> BREAKEVEN
                    elif tp1_hit:
                        pnl_75 = self._calculate_pnl(current_position['entry'], exit_price, current_position['type'], size * 0.75)
                        capital += pnl_75
                        self.trades.append(self._create_trade_record(idx, current_position, exit_price, pnl_75, 'Partial TP1 (75%)'))

                        # Upgrade to Phase 2 with 25% size
                        current_position['phase'] = 2
                        current_position['size'] = size * 0.25
                        current_position['sl'] = current_position['entry'] # Breakeven

                # PHASE 2: 25% size, Breakeven SL, Trailing SL, Target = TP2
                elif current_position['phase'] == 2:
                    tp2_hit = False
                    sl_hit = False
                    exit_price = 0.0

                    # TRAILING SL LOGIC
                    if current_position['type'] == 'BUY':
                        if row.get('Swing_Low', False) and row['Low'] > current_position['sl']:
                            current_position['sl'] = row['Low']
                        
                        if current_low <= current_position['sl']:
                            sl_hit = True
                            exit_price = current_position['sl']
                        elif current_high >= current_position['tp2']:
                            tp2_hit = True
                            exit_price = current_position['tp2']
                    
                    else: # SELL
                        if row.get('Swing_High', False) and row['High'] < current_position['sl']:
                            current_position['sl'] = row['High']
                        
                        if current_high >= current_position['sl']:
                            sl_hit = True
                            exit_price = current_position['sl']
                        elif current_low <= current_position['tp2']:
                            tp2_hit = True
                            exit_price = current_position['tp2']

                    # ACTION PHASE 2
                    if sl_hit:
                        pnl = self._calculate_pnl(current_position['entry'], exit_price, current_position['type'], current_position['size'])
                        capital += pnl
                        self.trades.append(self._create_trade_record(idx, current_position, exit_price, pnl, 'Breakeven/Loss'))
                        current_position = None
                        
                    elif tp2_hit:
                        pnl = self._calculate_pnl(current_position['entry'], exit_price, current_position['type'], current_position['size'])
                        capital += pnl
                        self.trades.append(self._create_trade_record(idx, current_position, exit_price, pnl, 'Win'))
                        current_position = None

            # --- CHECK FOR NEW SIGNAL ---
            signal = row.get('Signal')
            
            if signal in ['BUY', 'SELL'] and current_position is None:
                entry_price = row.get('Entry_Price')
                sl = row.get('Stop_Loss')
                tp1 = row.get('TP_1')
                tp2 = row.get('TP_2')

                if not pd.isna(entry_price) and not pd.isna(sl) and not pd.isna(tp1) and not pd.isna(tp2):
                    if (signal == 'BUY' and entry_price > sl) or (signal == 'SELL' and entry_price < sl):
                        
                        # 💥 POSITION SIZING FORMULA: (Capital * Risk%) / Risk_Points
                        risk_amount = capital * self.risk_percent
                        risk_points = abs(entry_price - sl)
                        if risk_points <= 0:
                            continue
                        
                        trade_size = risk_amount / risk_points
                        
                        # Deduct entry commission
                        capital -= trade_size * entry_price * self.commission
                        
                        current_position = {
                            'type': signal,
                            'entry': entry_price,
                            'sl': sl,
                            'tp1': tp1,
                            'tp2': tp2,
                            'size': trade_size,
                            'phase': 1,
                            'entry_idx': idx
                        }

            # --- TRACK EQUITY CURVE ---
            self.equity_curve.append(capital)

        # --- FINAL METRICS ---
        metrics = self._compute_metrics()

        return {
            'trades': pd.DataFrame(self.trades),
            'metrics': metrics,
            'equity_curve': self.equity_curve
        }

    def _calculate_pnl(self, entry: float, exit: float, direction: str, size: float) -> float:
        """Calculates accurate PnL including Round Trip Commission."""
        if direction == 'BUY':
            raw_pnl = (exit - entry) * size
        else:
            raw_pnl = (entry - exit) * size
        
        # Round trip commission = (Entry Price + Exit Price) * Size * Rate
        commission_cost = (entry + exit) * size * self.commission
        
        return raw_pnl - commission_cost

    def _create_trade_record(self, idx, pos, exit_p, pnl, result_str):
        return {
            'Entry_Index': pos['entry_idx'],
            'Exit_Index': idx,
            'Signal': pos['type'],
            'Entry_Price': round(pos['entry'], 2),
            'Exit_Price': round(exit_p, 2),
            'Size': round(pos['size'], 2),
            'P&L': round(pnl, 2),
            'Result': result_str
        }

    def _compute_metrics(self) -> Dict[str, Any]:
        if not self.trades:
            return {
                'Total Trades': 0, 'Win Rate': 0.0, 'Profit Factor': 0.0,
                'Total P&L': 0.0, 'Max Drawdown': 0.0, 'Sharpe Ratio': 0.0
            }

        trades_df = pd.DataFrame(self.trades)
        wins = trades_df[trades_df['P&L'] > 0]
        losses = trades_df[trades_df['P&L'] < 0]
        
        total_pnl = trades_df['P&L'].sum()
        win_rate = len(wins) / len(trades_df) if len(trades_df) > 0 else 0
        
        gross_profit = wins['P&L'].sum() if not wins.empty else 0
        gross_loss = abs(losses['P&L'].sum()) if not losses.empty else 1e-9
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0
        
        if self.equity_curve:
            running_max = np.maximum.accumulate(self.equity_curve)
            drawdown = (running_max - self.equity_curve) / running_max
            max_dd = drawdown.max()
        else:
            max_dd = 0.0

        returns = np.diff(self.equity_curve)
        if len(returns) > 0 and np.std(returns) != 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe = 0.0

        return {
            'Total Trades': len(trades_df),
            'Win Rate': round(win_rate * 100, 2),
            'Profit Factor': round(profit_factor, 2),
            'Total P&L': round(total_pnl, 2),
            'Max Drawdown': round(max_dd * 100, 2),
            'Sharpe Ratio': round(sharpe, 2)
        }