"""
Relative Strength Index (RSI) Indicator
Calculates RSI with standard 14-period lookback.
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('..')
from utils import load_stock_data, save_results, validate_data


def calculate_rsi(df, period=14):
    """
    Calculate RSI indicator.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with 'Close' column
    period : int
        RSI period (default: 14)
    
    Returns:
    --------
    pd.DataFrame : DataFrame with RSI column
    """
    df = df.copy()
    
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


def analyze_rsi(filepath="output/bbca_past_3_year.csv"):
    """Run RSI analysis on stock data."""
    print("=" * 50)
    print("RSI Technical Analysis")
    print("=" * 50)
    
    df = load_stock_data(filepath)
    validate_data(df)
    
    df = calculate_rsi(df)
    
    latest = df.iloc[-1]
    print(f"\nLatest Data ({latest['Date'].date()}):")
    print(f"  Close     : {latest['Close']:.2f}")
    print(f"  RSI(14)   : {latest['RSI']:.2f}")
    print(f"  Signal    : {latest['RSI_Signal']}")
    
    overbought = df[df['RSI'] > 70].shape[0]
    oversold = df[df['RSI'] < 30].shape[0]
    bullish = df[df['RSI_Signal'] == 'Bullish'].shape[0]
    bearish = df[df['RSI_Signal'] == 'Bearish'].shape[0]
    total_valid = df['RSI'].notna().sum()
    
    print(f"\nStatistics:")
    print(f"  Overbought (>70) : {overbought} days ({overbought/total_valid*100:.1f}%)")
    print(f"  Oversold (<30)   : {oversold} days ({oversold/total_valid*100:.1f}%)")
    print(f"  Bullish zone     : {bullish} days ({bullish/total_valid*100:.1f}%)")
    print(f"  Bearish zone     : {bearish} days ({bearish/total_valid*100:.1f}%)")
    
    save_results(df, "output/rsi_analysis.csv", ['Close', 'RSI', 'RSI_Signal'])
    
    return df


if __name__ == "__main__":
    analyze_rsi()
