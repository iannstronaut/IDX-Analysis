"""
Utility functions for technical analysis.
"""

import pandas as pd
import numpy as np


def load_stock_data(filepath="output/bbca_past_3_year.csv"):
    """Load stock data from CSV."""
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def save_results(df, filepath, columns):
    """Save analysis results to CSV."""
    output_cols = ['Date'] + columns
    df[output_cols].to_csv(filepath, index=False)
    print(f"Results saved to {filepath}")


def validate_data(df):
    """Validate that DataFrame has required columns."""
    required = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing = [col for col in required if col not in df.columns]
    if missing:
        available = ', '.join(df.columns)
        raise ValueError(f"Missing columns: {missing}. Available: {available}")
