"""
Evaluation Scoring Module
Evaluates technical indicators based on timeframe using configurable parameters.
"""

import pandas as pd
import sys
sys.path.append('..')
from utils import load_stock_data

# Import configuration
try:
    from config.scoring_config import (
        TIME_FRAMES,
        MA_THRESHOLDS,
        RSI_THRESHOLDS,
        MACD_THRESHOLDS,
        EMA_CROSS_THRESHOLDS,
        get_timeframe_period,
        get_recommendation,
    )
except ImportError:
    # Fallback defaults if config not found
    TIME_FRAMES = {'daily': 20, 'weekly': 12, 'monthly': 12}
    MA_THRESHOLDS = {'bullish': 60, 'bearish': 40}
    RSI_THRESHOLDS = {'overbought': 70, 'oversold': 30, 'bullish_min': 55, 'bearish_max': 45}
    MACD_THRESHOLDS = {'bullish': 60, 'bearish': 40}
    EMA_CROSS_THRESHOLDS = {'bullish': 60, 'bearish': 40}
    
    def get_timeframe_period(tf):
        return TIME_FRAMES.get(tf, 20)
    
    def get_recommendation(score, bullish, total, dirs):
        if score >= 70 and bullish >= total * 0.6:
            return 'STRONG_BUY'
        elif score >= 55:
            return 'BUY'
        elif score <= 30 and (total - bullish) >= total * 0.6:
            return 'STRONG_SELL'
        elif score <= 45:
            return 'SELL'
        return 'HOLD'


class TechnicalScorer:
    """Score technical indicators based on historical performance."""
    
    def __init__(self, df):
        self.df = df.copy()
        self.scores = {}
    
    def set_period(self, timeframe='daily'):
        """Set evaluation period based on timeframe."""
        periods = get_timeframe_period(timeframe)
        self.eval_df = self.df.tail(periods).copy()
        print(f"\nEvaluation Period: {timeframe.upper()} (last {periods} periods)")
        return self
    
    def score_ma(self, ma_col='MA20', close_col='Close'):
        """Score Moving Average indicator."""
        df = self.eval_df
        
        above_ma = (df[close_col] > df[ma_col]).sum()
        below_ma = (df[close_col] < df[ma_col]).sum()
        total = len(df.dropna())
        
        if total == 0:
            score = 50
        else:
            score = (above_ma / total) * 100
        
        # Use config thresholds
        th = MA_THRESHOLDS
        if score > th['bullish']:
            direction = 'Bullish'
        elif score < th['bearish']:
            direction = 'Bearish'
        else:
            direction = 'Neutral'
        
        self.scores[ma_col] = {
            'score': round(score, 2),
            'direction': direction,
            'above_count': int(above_ma),
            'below_count': int(below_ma),
            'total': total
        }
        
        return self
    
    def score_rsi(self, rsi_col='RSI'):
        """Score RSI indicator."""
        df = self.eval_df
        rsi = df[rsi_col].dropna()
        
        if len(rsi) == 0:
            score = 50
            avg_rsi = 50
        else:
            avg_rsi = rsi.mean()
            score = avg_rsi
        
        # Use config thresholds
        th = RSI_THRESHOLDS
        if avg_rsi > th['overbought']:
            direction = 'Overbought'
        elif avg_rsi < th['oversold']:
            direction = 'Oversold'
        elif avg_rsi > th['bullish_min']:
            direction = 'Bullish'
        elif avg_rsi < th['bearish_max']:
            direction = 'Bearish'
        else:
            direction = 'Neutral'
        
        self.scores['RSI'] = {
            'score': round(score, 2),
            'direction': direction,
            'avg_rsi': round(avg_rsi, 2),
            'min_rsi': round(rsi.min(), 2) if len(rsi) > 0 else None,
            'max_rsi': round(rsi.max(), 2) if len(rsi) > 0 else None
        }
        
        return self
    
    def score_macd(self, macd_col='MACD_Line', signal_col='MACD_Signal'):
        """Score MACD indicator."""
        df = self.eval_df
        
        bullish = (df[macd_col] > df[signal_col]).sum()
        bearish = (df[macd_col] < df[signal_col]).sum()
        total = len(df.dropna())
        
        if total == 0:
            score = 50
        else:
            score = (bullish / total) * 100
        
        # Use config thresholds
        th = MACD_THRESHOLDS
        if score > th['bullish']:
            direction = 'Bullish'
        elif score < th['bearish']:
            direction = 'Bearish'
        else:
            direction = 'Neutral'
        
        self.scores['MACD'] = {
            'score': round(score, 2),
            'direction': direction,
            'bullish_periods': int(bullish),
            'bearish_periods': int(bearish)
        }
        
        return self
    
    def score_ema_cross(self, diff_col='EMA_Diff'):
        """Score EMA Cross indicator."""
        df = self.eval_df
        diff = df[diff_col].dropna()
        
        if len(diff) == 0:
            score = 50
        else:
            golden = (diff > 0).sum()
            score = (golden / len(diff)) * 100
        
        # Use config thresholds
        th = EMA_CROSS_THRESHOLDS
        if score > th['bullish']:
            direction = 'Bullish'
        elif score < th['bearish']:
            direction = 'Bearish'
        else:
            direction = 'Neutral'
        
        self.scores['EMA_Cross'] = {
            'score': round(score, 2),
            'direction': direction,
            'avg_diff': round(diff.mean(), 4) if len(diff) > 0 else 0
        }
        
        return self
    
    def get_overall_score(self):
        """Calculate overall composite score."""
        if not self.scores:
            return 50
        
        total_score = sum(s['score'] for s in self.scores.values())
        return round(total_score / len(self.scores), 2)
    
    def get_recommendation(self):
        """Get trading recommendation based on scores using config."""
        overall = self.get_overall_score()
        
        directions = [s['direction'] for s in self.scores.values()]
        bullish_count = directions.count('Bullish') + directions.count('Overbought')
        total = len(directions)
        
        return get_recommendation(overall, bullish_count, total, directions)
    
    def print_report(self):
        """Print evaluation report."""
        print("\n" + "=" * 50)
        print("TECHNICAL SCORING REPORT")
        print("=" * 50)
        
        for name, data in self.scores.items():
            print(f"\n{name}:")
            print(f"  Score: {data['score']:.2f}")
            print(f"  Direction: {data['direction']}")
        
        print(f"\nOverall Score: {self.get_overall_score()}")
        print(f"Recommendation: {self.get_recommendation()}")
        print("=" * 50)


def run_evaluation(filepath=None, emiten='BBCA', timeframe='daily'):
    """
    Run complete evaluation scoring.
    
    Parameters:
    -----------
    filepath : str, optional
        Path to CSV file. If None, uses output/{emiten}_past_3_year.csv
    emiten : str
        Stock ticker (default: BBCA)
    timeframe : str
        Evaluation timeframe (daily/weekly/monthly)
    """
    if filepath is None:
        filepath = f"output/{emiten.upper()}_past_3_year.csv"
    
    print(f"Loading data from: {filepath}")
    df = load_stock_data(filepath)
    print(f"Data loaded: {len(df)} rows from {df['Date'].min().date()} to {df['Date'].max().date()}")
    
    scorer = TechnicalScorer(df)
    scorer.set_period(timeframe)
    
    if 'MA20' in df.columns:
        scorer.score_ma('MA20', 'Close')
    if 'MA50' in df.columns:
        scorer.score_ma('MA50', 'Close')
    if 'RSI' in df.columns:
        scorer.score_rsi('RSI')
    if 'MACD_Line' in df.columns:
        scorer.score_macd('MACD_Line', 'MACD_Signal')
    if 'EMA_Diff' in df.columns:
        scorer.score_ema_cross('EMA_Diff')
    
    scorer.print_report()
    
    return scorer


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Technical Analysis Scoring')
    parser.add_argument('--emiten', default='BBCA', help='Stock ticker (default: BBCA)')
    parser.add_argument('--timeframe', choices=['daily', 'weekly', 'monthly'],
                       default='daily', help='Evaluation timeframe')
    args = parser.parse_args()
    
    run_evaluation(emiten=args.emiten, timeframe=args.timeframe)
