"""
Moving Average 20 (MA20) Indicator
Calculates 20-period Simple Moving Average.
"""

import pandas as pd
import sys
sys.path.append('..')
from utils import load_stock_data, save_results, validate_data


def calculate_ma20(df):
    """
    Calculate 20-period Simple Moving Average.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with 'Close' column
    
    Returns:
    --------
    pd.DataFrame : DataFrame with MA20 column
    """
    df = df.copy()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    df['MA20_Signal'] = df.apply(lambda row: 
        'Bullish' if row['Close'] > row['MA20'] else 
        'Bearish' if row['Close'] < row['MA20'] else 'Neutral', axis=1
    )
    
    return df


def analyze_ma20(filepath="output/bbca_past_3_year.csv"):
    """Run MA20 analysis on stock data."""
    print("=" * 50)
    print("MA20 Technical Analysis")
    print("=" * 50)
    
    df = load_stock_data(filepath)
    validate_data(df)
    
    df = calculate_ma20(df)
    
    latest = df.iloc[-1]
    print(f"\nLatest Data ({latest['Date'].date()}):")
    print(f"  Close : {latest['Close']:.2f}")
    print(f"  MA20  : {latest['MA20']:.2f}")
    print(f"  Signal: {latest['MA20_Signal']}")
    
    above_ma = df[df['Close'] > df['MA20']].shape[0]
    below_ma = df[df['Close'] < df['MA20']].shape[0]
    total_valid = df['MA20'].notna().sum()
    
    print(f"\nStatistics:")
    print(f"  Days above MA20: {above_ma} ({above_ma/total_valid*100:.1f}%)")
    print(f"  Days below MA20: {below_ma} ({below_ma/total_valid*100:.1f}%)")
    
    save_results(df, "output/ma20_analysis.csv", ['Close', 'MA20', 'MA20_Signal'])
    
    return df


if __name__ == "__main__":
    analyze_ma20()
