"""
Signal Evaluation Module
Evaluates candlestick patterns and trend strength.
Detects: Strong Bullish, Weak Bullish, Neutral, Weak Bearish, Strong Bearish
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('..')
from utils import load_stock_data


class SignalEvaluator:
    """Evaluate trading signals from candlestick patterns and trends."""
    
    SIGNAL_STRENGTH = {
        'STRONG_BULLISH': 2,
        'BULLISH': 1,
        'NEUTRAL': 0,
        'BEARISH': -1,
        'STRONG_BEARISH': -2
    }
    
    def __init__(self, df):
        self.df = df.copy()
        self.signals = []
    
    def calculate_body(self, row):
        """Calculate candlestick body size and direction."""
        body = row['Close'] - row['Open']
        return body
    
    def calculate_shadows(self, row):
        """Calculate upper and lower shadows."""
        if row['Close'] >= row['Open']:
            upper = row['High'] - row['Close']
            lower = row['Open'] - row['Low']
        else:
            upper = row['High'] - row['Open']
            lower = row['Close'] - row['Low']
        return upper, lower
    
    def is_hammer(self, row):
        """Detect hammer pattern (bullish reversal)."""
        body = abs(self.calculate_body(row))
        upper, lower = self.calculate_shadows(row)
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return False
        
        body_ratio = body / total_range
        lower_ratio = lower / total_range
        
        return body_ratio < 0.3 and lower_ratio > 0.6 and upper < body
    
    def is_shooting_star(self, row):
        """Detect shooting star pattern (bearish reversal)."""
        body = abs(self.calculate_body(row))
        upper, lower = self.calculate_shadows(row)
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return False
        
        body_ratio = body / total_range
        upper_ratio = upper / total_range
        
        return body_ratio < 0.3 and upper_ratio > 0.6 and lower < body
    
    def is_engulfing(self, idx):
        """Detect bullish/bearish engulfing pattern."""
        if idx < 1:
            return None
        
        prev = self.df.iloc[idx - 1]
        curr = self.df.iloc[idx]
        
        prev_body = prev['Close'] - prev['Open']
        curr_body = curr['Close'] - curr['Open']
        
        # Bullish engulfing
        if prev_body < 0 and curr_body > 0:
            if curr['Open'] < prev['Close'] and curr['Close'] > prev['Open']:
                return 'BULLISH_ENGULFING'
        
        # Bearish engulfing
        if prev_body > 0 and curr_body < 0:
            if curr['Open'] > prev['Close'] and curr['Close'] < prev['Open']:
                return 'BEARISH_ENGULFING'
        
        return None
    
    def is_doji(self, row):
        """Detect doji pattern (indecision)."""
        body = abs(self.calculate_body(row))
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return True
        
        return body / total_range < 0.1
    
    def is_marubozu(self, row):
        """Detect marubozu pattern (strong trend)."""
        body = abs(self.calculate_body(row))
        upper, lower = self.calculate_shadows(row)
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return None
        
        if body / total_range > 0.9:
            if row['Close'] > row['Open']:
                return 'BULLISH_MARUBOZU'
            else:
                return 'BEARISH_MARUBOZU'
        
        return None
    
    def analyze_trend(self, periods=5):
        """Analyze short-term trend direction."""
        df = self.df
        df['Trend'] = 'NEUTRAL'
        
        for i in range(periods, len(df)):
            window = df.iloc[i-periods:i]
            start_price = window['Close'].iloc[0]
            end_price = window['Close'].iloc[-1]
            
            change_pct = (end_price - start_price) / start_price * 100
            
            if change_pct > 3:
                df.iloc[i, df.columns.get_loc('Trend')] = 'UPTREND'
            elif change_pct < -3:
                df.iloc[i, df.columns.get_loc('Trend')] = 'DOWNTREND'
        
        return df
    
    def evaluate_single_candle(self, idx):
        """Evaluate signal for a single candle."""
        row = self.df.iloc[idx]
        
        body = self.calculate_body(row)
        pattern_signals = []
        
        # Pattern detection
        if self.is_hammer(row) and body > 0:
            pattern_signals.append('HAMMER')
        elif self.is_shooting_star(row) and body < 0:
            pattern_signals.append('SHOOTING_STAR')
        
        engulfing = self.is_engulfing(idx)
        if engulfing:
            pattern_signals.append(engulfing)
        
        if self.is_doji(row):
            pattern_signals.append('DOJI')
        
        marubozu = self.is_marubozu(row)
        if marubozu:
            pattern_signals.append(marubozu)
        
        # Determine signal strength
        trend = row.get('Trend', 'NEUTRAL')
        signal = self._determine_signal(body, pattern_signals, trend)
        
        return {
            'date': row['Date'],
            'open': row['Open'],
            'high': row['High'],
            'low': row['Low'],
            'close': row['Close'],
            'patterns': pattern_signals,
            'trend': trend,
            'signal': signal
        }
    
    def _determine_signal(self, body, patterns, trend):
        """Determine final signal strength."""
        score = 0
        
        # Body contribution
        if body > 0:
            score += 1
        elif body < 0:
            score -= 1
        
        # Pattern contribution
        if 'BULLISH_ENGULFING' in patterns or 'BULLISH_MARUBOZU' in patterns or 'HAMMER' in patterns:
            score += 2
        if 'BEARISH_ENGULFING' in patterns or 'BEARISH_MARUBOZU' in patterns or 'SHOOTING_STAR' in patterns:
            score -= 2
        if 'DOJI' in patterns:
            score = 0
        
        # Trend contribution
        if trend == 'UPTREND':
            score += 1
        elif trend == 'DOWNTREND':
            score -= 1
        
        # Map score to signal
        if score >= 3:
            return 'STRONG_BULLISH'
        elif score >= 1:
            return 'BULLISH'
        elif score <= -3:
            return 'STRONG_BEARISH'
        elif score <= -1:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def evaluate_all(self):
        """Evaluate all candles in the dataset."""
        self.analyze_trend()
        
        for i in range(len(self.df)):
            signal = self.evaluate_single_candle(i)
            self.signals.append(signal)
        
        return self
    
    def get_summary(self, last_n=20):
        """Get summary of recent signals."""
        recent = self.signals[-last_n:]
        
        counts = {
            'STRONG_BULLISH': 0,
            'BULLISH': 0,
            'NEUTRAL': 0,
            'BEARISH': 0,
            'STRONG_BEARISH': 0
        }
        
        for sig in recent:
            counts[sig['signal']] += 1
        
        # Calculate weighted score
        total_score = sum(
            self.SIGNAL_STRENGTH[sig['signal']] 
            for sig in recent
        )
        
        avg_score = total_score / len(recent) if recent else 0
        
        # Determine overall sentiment
        if avg_score > 1:
            sentiment = 'BULLISH'
        elif avg_score < -1:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        return {
            'periods_analyzed': last_n,
            'signal_counts': counts,
            'weighted_score': round(avg_score, 2),
            'overall_sentiment': sentiment,
            'recent_signals': recent[-5:]
        }
    
    def print_report(self):
        """Print signal evaluation report."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("SIGNAL EVALUATION REPORT")
        print("=" * 60)
        
        print(f"\nPeriods Analyzed: {summary['periods_analyzed']}")
        print("\nSignal Distribution:")
        for signal, count in summary['signal_counts'].items():
            bar = "█" * count + "░" * (summary['periods_analyzed'] - count)
            print(f"  {signal:16} : {bar} ({count})")
        
        print(f"\nWeighted Score: {summary['weighted_score']}")
        print(f"Overall Sentiment: {summary['overall_sentiment']}")
        
        print("\nRecent Signals (Last 5):")
        for sig in summary['recent_signals']:
            patterns = ", ".join(sig['patterns']) if sig['patterns'] else "None"
            print(f"  {sig['date'].date()} | {sig['signal']:16} | Patterns: {patterns}")
        
        print("=" * 60)


def run_signal_evaluation(filepath=None, emiten='BBCA'):
    """
    Run complete signal evaluation.
    
    Parameters:
    -----------
    filepath : str, optional
        Path to CSV file. If None, uses output/{emiten}_past_3_year.csv
    emiten : str
        Stock ticker (default: BBCA)
    """
    if filepath is None:
        filepath = f"output/{emiten.upper()}_past_3_year.csv"
    
    print(f"Loading data from: {filepath}")
    df = load_stock_data(filepath)
    print(f"Data loaded: {len(df)} rows from {df['Date'].min().date()} to {df['Date'].max().date()}")
    
    evaluator = SignalEvaluator(df)
    evaluator.evaluate_all()
    evaluator.print_report()
    
    return evaluator


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Signal Evaluation')
    parser.add_argument('--emiten', default='BBCA', help='Stock ticker (default: BBCA)')
    args = parser.parse_args()
    
    run_signal_evaluation(emiten=args.emiten)
