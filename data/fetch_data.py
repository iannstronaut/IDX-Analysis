"""
Data Fetching Module for Indonesia Stock Exchange
Downloads historical data from Yahoo Finance for the last 3 years or specific date range.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


def parse_date(date_string):
    """
    Parse date string to datetime object.
    Supports formats: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY
    """
    if date_string is None:
        return None

    formats = [
        '%Y-%m-%d',      # 2025-01-01
        '%d-%m-%Y',      # 01-01-2025
        '%d/%m/%Y',      # 01/01/2025
        '%Y/%m/%d',      # 2025/01/01
        '%d-%m-%y',      # 01-01-25
        '%d/%m/%y',      # 01/01/25
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")


def download_stock_data(emiten="BBCA", period="3y", interval="1d", start=None, end=None):
    """
    Download stock data from Yahoo Finance.

    Parameters:
    -----------
    emiten : str
        Stock ticker without .JK suffix (default: BBCA)
    period : str
        Period to download (default: '3y' for 3 years)
    interval : str
        Data interval ('1d', '1wk', '1mo')
    start : str, optional
        Start date (format: YYYY-MM-DD or DD-MM-YYYY)
    end : str, optional
        End date (format: YYYY-MM-DD or DD-MM-YYYY)

    Returns:
    --------
    pd.DataFrame : Stock data with OHLCV columns
    """
    ticker_symbol = f"{emiten.upper()}.JK"

    # Parse dates if provided
    start_date = parse_date(start) if start else None
    end_date = parse_date(end) if end else None

    if start_date and end_date:
        print(f"Downloading {ticker_symbol} data from {start_date.date()} to {end_date.date()} (interval={interval})...")
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
    else:
        print(f"Downloading {ticker_symbol} data (period={period}, interval={interval})...")
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)

    if df.empty:
        raise ValueError(f"No data downloaded for {ticker_symbol}. Please check ticker symbol, date range, and internet connection.")

    df.reset_index(inplace=True)

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    elif 'Datetime' in df.columns:
        df['Date'] = pd.to_datetime(df['Datetime'])
        df.drop(columns=['Datetime'], inplace=True)

    df.columns = [c.replace(' ', '') for c in df.columns]

    print(f"Downloaded {len(df)} rows from {df['Date'].min().date()} to {df['Date'].max().date()}")

    return df


# Keep old function name for backward compatibility
def download_bbc_data(period="3y", interval="1d"):
    """Download BBCA.JK stock data (backward compatibility)."""
    return download_stock_data(emiten="BBCA", period=period, interval=interval)


def save_data(df, filepath="output/stock_data.csv"):
    """Save DataFrame to CSV file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")


def load_data(filepath="output/stock_data.csv"):
    """Load data from CSV file."""
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def get_resampled_data(df, timeframe='daily'):
    """
    Resample data to different timeframes.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Daily OHLCV data
    timeframe : str
        'daily', 'weekly', or 'monthly'
    
    Returns:
    --------
    pd.DataFrame : Resampled data
    """
    df = df.copy()
    df.set_index('Date', inplace=True)
    
    if timeframe == 'daily':
        return df.reset_index()
    elif timeframe == 'weekly':
        resampled = df.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna().reset_index()
        return resampled
    elif timeframe == 'monthly':
        resampled = df.resample('ME').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna().reset_index()
        return resampled
    else:
        raise ValueError(f"Unknown timeframe: {timeframe}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Fetch stock data from Yahoo Finance')
    parser.add_argument('--emiten', default='BBCA', help='Stock ticker without .JK (default: BBCA)')
    parser.add_argument('--period', default='3y', help='Download period (default: 3y)')
    parser.add_argument('--interval', default='1d', choices=['1d', '1wk', '1mo'],
                       help='Data interval (default: 1d)')
    parser.add_argument('--start', help='Start date (format: YYYY-MM-DD or DD-MM-YYYY)')
    parser.add_argument('--end', help='End date (format: YYYY-MM-DD or DD-MM-YYYY)')

    args = parser.parse_args()

    df = download_stock_data(
        emiten=args.emiten,
        period=args.period,
        interval=args.interval,
        start=args.start,
        end=args.end
    )

    output_file = f"output/{args.emiten.lower()}_raw.csv"
    save_data(df, output_file)

    print(f"\nData saved to {output_file}")
