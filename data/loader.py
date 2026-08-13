import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import time


def load_data(symbol, start_date, end_date, interval="1d"):
    """
    Download OHLCV data from Yahoo Finance with strict interval limits.
    """
    
    # Map interval to maximum available days
    interval_limits = {
        '1m': 55, '5m': 55, '10m': 55, '15m': 55, '30m': 55,
        '1h': 730, '4h': 730,
        '1d': None, '1wk': None, '1mo': None
    }

    today = datetime.today().date()
    requested_end = datetime.strptime(end_date, '%Y-%m-%d').date()
    if requested_end > today:
        print(f"Warning: End date {end_date} is in the future. Capping to today: {today}")
        end_date = today.strftime('%Y-%m-%d')

    max_days = interval_limits.get(interval)
    if max_days is not None:
        earliest_allowed = today - timedelta(days=max_days)
        requested_start = datetime.strptime(start_date, '%Y-%m-%d').date()
        if requested_start < earliest_allowed:
            print(f"Warning: {interval} data available for last {max_days} days. "
                  f"Adjusting start_date from {start_date} to {earliest_allowed.strftime('%Y-%m-%d')}")
            start_date = earliest_allowed.strftime('%Y-%m-%d')

    fallback_symbols = [symbol, '^GSPC', 'QQQ']

    for attempt, sym in enumerate(fallback_symbols):
        try:
            print(f"Attempting to download data for {sym} ({interval}) from {start_date} to {end_date}...")
            
            df = yf.download(
                tickers=sym,
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=False,
                progress=False
            )

            if df.empty:
                print(f"No data retrieved for {sym}. Trying next fallback...")
                time.sleep(1)
                continue

            if hasattr(df.columns, 'levels'):
                df.columns = df.columns.get_level_values(0)

            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df.columns.name = None
            df.dropna(inplace=True)

            return df

        except Exception as e:
            print(f"Download failed for {sym}: {e}. Trying fallback...")
            time.sleep(2)

    raise ValueError(f"Could not download data. Please wait 10 minutes or use a VPN.")