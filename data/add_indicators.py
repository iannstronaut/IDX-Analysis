"""
Add Technical Indicators to Stock Data
Fetches 3-year data, calculates all indicators, saves to data/{emiten}_past_3_year.csv
"""

import sys
sys.path.append('..')

import pandas as pd
from pathlib import Path


def add_ma20(df):
    """Add MA20 indicator."""
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA20_Signal'] = df.apply(lambda row: 
        'Bullish' if row['Close'] > row['MA20'] else 
        'Bearish' if row['Close'] < row['MA20'] else 'Neutral', axis=1
    )
    return df


def add_ma50(df):
    """Add MA50 indicator."""
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA50_Signal'] = df.apply(lambda row: 
        'Bullish' if row['Close'] > row['MA50'] else 
        'Bearish' if row['Close'] < row['MA50'] else 'Neutral', axis=1
    )
    return df


def add_rsi(df, period=14):
    """Add RSI indicator."""
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    def get_signal(rsi):
        if pd.isna(rsi):
            return 'Neutral'
        if rsi > 70:
            return 'Overbought'
        elif rsi < 30:
            return 'Oversold'
        elif rsi > 55:
            return 'Bullish'
        elif rsi < 45:
            return 'Bearish'
        else:
            return 'Neutral'
    
    df['RSI_Signal'] = df['RSI'].apply(get_signal)
    return df


def add_macd(df, fast=12, slow=26, signal=9):
    """Add MACD indicator."""
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    df['MACD_Line'] = ema_fast - ema_slow
    df['MACD_Signal'] = df['MACD_Line'].ewm(span=signal, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD_Line'] - df['MACD_Signal']
    
    def get_macd_signal(row):
        if pd.isna(row['MACD_Line']) or pd.isna(row['MACD_Signal']):
            return 'Neutral'
        if row['MACD_Line'] > row['MACD_Signal'] and row['MACD_Histogram'] > 0:
            return 'Bullish'
        elif row['MACD_Line'] < row['MACD_Signal'] and row['MACD_Histogram'] < 0:
            return 'Bearish'
        elif row['MACD_Line'] > 0 and row['MACD_Signal'] > 0:
            return 'Weak_Bullish'
        elif row['MACD_Line'] < 0 and row['MACD_Signal'] < 0:
            return 'Weak_Bearish'
        else:
            return 'Neutral'
    
    df['MACD_Trend'] = df.apply(get_macd_signal, axis=1)
    return df


def add_ema_cross(df, fast=12, slow=26):
    """Add EMA Cross indicator."""
    df['EMA12'] = df['Close'].ewm(span=fast, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=slow, adjust=False).mean()
    df['EMA_Diff'] = df['EMA12'] - df['EMA26']
    df['EMA_Cross'] = df['EMA_Diff'].apply(lambda x: 
        'Golden_Cross' if x > 0 else 'Death_Cross' if x < 0 else 'Neutral'
    )
    
    df['Cross_Signal'] = 'Hold'
    for i in range(1, len(df)):
        prev = df['EMA_Diff'].iloc[i-1]
        curr = df['EMA_Diff'].iloc[i]
        if prev < 0 and curr > 0:
            df.iloc[i, df.columns.get_loc('Cross_Signal')] = 'Buy'
        elif prev > 0 and curr < 0:
            df.iloc[i, df.columns.get_loc('Cross_Signal')] = 'Sell'
    
    return df


def add_all_indicators(df):
    """Add all technical indicators to dataframe."""
    print("Calculating MA20...")
    df = add_ma20(df)
    
    print("Calculating MA50...")
    df = add_ma50(df)
    
    print("Calculating RSI...")
    df = add_rsi(df)
    
    print("Calculating MACD...")
    df = add_macd(df)
    
    print("Calculating EMA Cross...")
    df = add_ema_cross(df)
    
    return df


def process_and_save(emiten="BBCA", interval="1d", start=None, end=None, period="3y"):
    """
    Fetch data, add indicators, save to data/{emiten}_past_3_year.csv

    Parameters:
    -----------
    emiten : str
        Stock ticker (default: BBCA)
    interval : str
        Data interval ('1d', '1wk', '1mo')
    start : str, optional
        Start date (format: YYYY-MM-DD or DD-MM-YYYY)
    end : str, optional
        End date (format: YYYY-MM-DD or DD-MM-YYYY)
    period : str, optional
        Period to download if start/end not provided (default: '3y')
    """
    from data.fetch_data import download_stock_data, save_data

    # Determine date range description
    if start and end:
        range_desc = f"{start} to {end}"
    elif start:
        range_desc = f"from {start}"
    elif end:
        range_desc = f"until {end}"
    else:
        range_desc = f"3 Years"

    print(f"\n{'='*60}")
    print(f"Processing {emiten}.JK - {range_desc} with Indicators")
    print(f"{'='*60}\n")

    # Fetch data (by date range or period)
    df = download_stock_data(emiten=emiten, period=period, interval=interval, start=start, end=end)

    # Add all indicators
    df = add_all_indicators(df)

    # Save to file with emiten name
    filename = f"output/{emiten.upper()}_past_3_year.csv"
    save_data(df, filename)

    print(f"\n{'='*60}")
    print(f"Complete! File saved: {filename}")
    print(f"{'='*60}")
    print(f"\nData shape: {df.shape}")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"\nColumns: {list(df.columns)}")

    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Add indicators to stock data')
    parser.add_argument('--emiten', default='BBCA', help='Stock ticker (default: BBCA)')
    parser.add_argument('--interval', default='1d', choices=['1d', '1wk', '1mo'],
                       help='Data interval')
    parser.add_argument('--start', help='Start date (format: YYYY-MM-DD or DD-MM-YYYY)')
    parser.add_argument('--end', help='End date (format: YYYY-MM-DD or DD-MM-YYYY)')
    parser.add_argument('--period', default='3y', help='Download period (default: 3y)')

    args = parser.parse_args()

    process_and_save(
        emiten=args.emiten,
        interval=args.interval,
        start=args.start,
        end=args.end,
        period=args.period
    )
