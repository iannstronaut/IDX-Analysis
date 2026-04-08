"""
EMA Cross Indicator
Calculates EMA12/EMA26 crossover signals (similar to MACD but pure EMA).
"""

import pandas as pd
import sys
sys.path.append('..')
from utils import load_stock_data, save_results, validate_data


def calculate_ema_cross(df, fast=12, slow=26):
    """
    Calculate EMA Crossover indicator.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with 'Close' column
    fast : int
        Fast EMA period
    slow : int
        Slow EMA period
    
    Returns:
    --------
    pd.DataFrame : DataFrame with EMA Cross columns
    """
    df = df.copy()
    
    df[f'EMA{fast}'] = df['Close'].ewm(span=fast, adjust=False).mean()
    df[f'EMA{slow}'] = df['Close'].ewm(span=slow, adjust=False).mean()
    
    df['EMA_Diff'] = df[f'EMA{fast}'] - df[f'EMA{slow}']
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


def analyze_ema_cross(filepath="output/bbca_past_3_year.csv"):
    """Run EMA Cross analysis on stock data."""
    print("=" * 50)
    print("EMA Cross Technical Analysis")
    print("=" * 50)
    
    df = load_stock_data(filepath)
    validate_data(df)
    
    df = calculate_ema_cross(df)
    
    latest = df.iloc[-1]
    print(f"\nLatest Data ({latest['Date'].date()}):")
    print(f"  Close      : {latest['Close']:.2f}")
    print(f"  EMA12      : {latest['EMA12']:.2f}")
    print(f"  EMA26      : {latest['EMA26']:.2f}")
    print(f"  Cross State: {latest['EMA_Cross']}")
    print(f"  Signal     : {latest['Cross_Signal']}")
    
    golden = df[df['EMA_Cross'] == 'Golden_Cross'].shape[0]
    death = df[df['EMA_Cross'] == 'Death_Cross'].shape[0]
    buys = df[df['Cross_Signal'] == 'Buy'].shape[0]
    sells = df[df['Cross_Signal'] == 'Sell'].shape[0]
    total_valid = df['EMA_Diff'].notna().sum()
    
    print(f"\nStatistics:")
    print(f"  Golden Cross days : {golden} ({golden/total_valid*100:.1f}%)")
    print(f"  Death Cross days  : {death} ({death/total_valid*100:.1f}%)")
    print(f"  Buy signals       : {buys}")
    print(f"  Sell signals      : {sells}")
    
    recent_buys = df[df['Cross_Signal'] == 'Buy'].tail(3)
    recent_sells = df[df['Cross_Signal'] == 'Sell'].tail(3)
    
    print(f"\nRecent Signals:")
    if not recent_buys.empty:
        for _, row in recent_buys.iterrows():
            print(f"  Buy  : {row['Date'].date()}")
    if not recent_sells.empty:
        for _, row in recent_sells.iterrows():
            print(f"  Sell : {row['Date'].date()}")
    
    save_results(df, "output/ema_cross_analysis.csv",
                 ['Close', 'EMA12', 'EMA26', 'EMA_Diff', 'EMA_Cross', 'Cross_Signal'])
    
    return df


if __name__ == "__main__":
    analyze_ema_cross()
