"""
MACD Indicator
Calculates Moving Average Convergence Divergence with signal line.
"""

import pandas as pd
import sys
sys.path.append('..')
from utils import load_stock_data, save_results, validate_data


def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    Calculate MACD indicator.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with 'Close' column
    fast : int
        Fast EMA period
    slow : int
        Slow EMA period
    signal : int
        Signal line period
    
    Returns:
    --------
    pd.DataFrame : DataFrame with MACD columns
    """
    df = df.copy()
    
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


def analyze_macd(filepath="output/bbca_past_3_year.csv"):
    """Run MACD analysis on stock data."""
    print("=" * 50)
    print("MACD Technical Analysis")
    print("=" * 50)
    
    df = load_stock_data(filepath)
    validate_data(df)
    
    df = calculate_macd(df)
    
    latest = df.iloc[-1]
    print(f"\nLatest Data ({latest['Date'].date()}):")
    print(f"  Close          : {latest['Close']:.2f}")
    print(f"  MACD Line      : {latest['MACD_Line']:.4f}")
    print(f"  Signal Line    : {latest['MACD_Signal']:.4f}")
    print(f"  Histogram      : {latest['MACD_Histogram']:.4f}")
    print(f"  Signal         : {latest['MACD_Trend']}")
    
    bullish = df[df['MACD_Trend'] == 'Bullish'].shape[0]
    bearish = df[df['MACD_Trend'] == 'Bearish'].shape[0]
    total_valid = df['MACD_Line'].notna().sum()
    
    print(f"\nStatistics:")
    print(f"  Bullish signals  : {bullish} days ({bullish/total_valid*100:.1f}%)")
    print(f"  Bearish signals  : {bearish} days ({bearish/total_valid*100:.1f}%)")
    
    df['Histogram_Change'] = df['MACD_Histogram'].diff()
    divergence = df.tail(5)['Histogram_Change'].sum()
    
    print(f"\nRecent Momentum (5 days):")
    if divergence > 0:
        print(f"  Trend: Increasing bullish momentum")
    elif divergence < 0:
        print(f"  Trend: Increasing bearish momentum")
    else:
        print(f"  Trend: Stable")
    
    save_results(df, "output/macd_analysis.csv",
                 ['Close', 'MACD_Line', 'MACD_Signal', 'MACD_Histogram', 'MACD_Trend'])
    
    return df


if __name__ == "__main__":
    analyze_macd()
