"""
Moving Average 50 (MA50) Indicator
Calculates 50-period Simple Moving Average for trend analysis.
"""

import pandas as pd
import sys
sys.path.append('..')
from utils import load_stock_data, save_results, validate_data


def calculate_ma50(df):
    """
    Calculate 50-period Simple Moving Average.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with 'Close' column
    
    Returns:
    --------
    pd.DataFrame : DataFrame with MA50 column
    """
    df = df.copy()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    df['MA50_Signal'] = df.apply(lambda row: 
        'Bullish' if row['Close'] > row['MA50'] else 
        'Bearish' if row['Close'] < row['MA50'] else 'Neutral', axis=1
    )
    
    return df


def analyze_ma50(filepath="output/bbca_past_3_year.csv"):
    """Run MA50 analysis on stock data."""
    print("=" * 50)
    print("MA50 Technical Analysis")
    print("=" * 50)
    
    df = load_stock_data(filepath)
    validate_data(df)
    
    df = calculate_ma50(df)
    
    latest = df.iloc[-1]
    print(f"\nLatest Data ({latest['Date'].date()}):")
    print(f"  Close : {latest['Close']:.2f}")
    print(f"  MA50  : {latest['MA50']:.2f}")
    print(f"  Signal: {latest['MA50_Signal']}")
    
    above_ma = df[df['Close'] > df['MA50']].shape[0]
    below_ma = df[df['Close'] < df['MA50']].shape[0]
    total_valid = df['MA50'].notna().sum()
    
    print(f"\nStatistics:")
    print(f"  Days above MA50: {above_ma} ({above_ma/total_valid*100:.1f}%)")
    print(f"  Days below MA50: {below_ma} ({below_ma/total_valid*100:.1f}%)")
    
    trend_days = 20
    recent = df.tail(trend_days)
    ma_slope = (recent['MA50'].iloc[-1] - recent['MA50'].iloc[0]) / trend_days
    
    print(f"\nTrend Analysis (last {trend_days} days):")
    print(f"  MA50 Slope: {ma_slope:.4f} per day")
    if ma_slope > 0.001:
        print(f"  Trend: Rising")
    elif ma_slope < -0.001:
        print(f"  Trend: Falling")
    else:
        print(f"  Trend: Flat")
    
    save_results(df, "output/ma50_analysis.csv", ['Close', 'MA50', 'MA50_Signal'])
    
    return df


if __name__ == "__main__":
    analyze_ma50()
