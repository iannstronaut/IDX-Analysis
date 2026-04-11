"""
Signal Evaluation Module
Evaluates candlestick patterns and trend strength using configurable parameters.
Detects: Strong Bullish, Weak Bullish, Neutral, Weak Bearish, Strong Bearish
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('..')
from utils import load_stock_data

# Import configuration
try:
    from config.scoring_config import (
        SIGNAL_STRENGTH_WEIGHTS,
        SIGNAL_COMPONENT_WEIGHTS,
        HAMMER_CONFIG,
        SHOOTING_STAR_CONFIG,
        DOJI_CONFIG,
        MARUBOZU_CONFIG,
        ENGULFING_CONFIG,
        TREND_CONFIG,
        SENTIMENT_THRESHOLDS,
        SUMMARY_CONFIG,
        get_sentiment,
    )
except ImportError:
    # Fallback defaults if config not found
    SIGNAL_STRENGTH_WEIGHTS = {
        'STRONG_BULLISH': 2, 'BULLISH': 1, 'NEUTRAL': 0,
        'BEARISH': -1, 'STRONG_BEARISH': -2
    }
    SIGNAL_COMPONENT_WEIGHTS = {
        'body_positive': 1, 'body_negative': -1,
        'bullish_pattern': 2, 'bearish_pattern': -2,
        'uptrend': 1, 'downtrend': -1
    }
    HAMMER_CONFIG = {'max_body_ratio': 0.3, 'min_lower_shadow_ratio': 0.6}
    SHOOTING_STAR_CONFIG = {'max_body_ratio': 0.3, 'min_upper_shadow_ratio': 0.6}
    DOJI_CONFIG = {'max_body_ratio': 0.1}
    MARUBOZU_CONFIG = {'min_body_ratio': 0.9}
    TREND_CONFIG = {'lookback_periods': 5, 'uptrend_threshold': 3, 'downtrend_threshold': -3}
    SENTIMENT_THRESHOLDS = {
        'strong_bullish': 0.5, 'bullish': 0.2,
        'bearish': -0.2, 'strong_bearish': -0.5
    }
    SUMMARY_CONFIG = {'recent_signals_count': 5, 'signal_distribution_periods': 20}

    def get_sentiment(weighted_score):
        """Fallback sentiment function."""
        if weighted_score >= 0.5:
            return 'STRONG_BULLISH'
        elif weighted_score >= 0.2:
            return 'BULLISH'
        elif weighted_score <= -0.5:
            return 'STRONG_BEARISH'
        elif weighted_score <= -0.2:
            return 'BEARISH'
        return 'NEUTRAL'


class SignalEvaluator:
    """Evaluate trading signals from candlestick patterns and trends."""
    
    def __init__(self, df):
        self.df = df.copy()
        self.signals = []
        self.cfg_weights = SIGNAL_STRENGTH_WEIGHTS
        self.cfg_components = SIGNAL_COMPONENT_WEIGHTS
    
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
        """Detect hammer pattern (bullish reversal) using config thresholds."""
        cfg = HAMMER_CONFIG
        body = abs(self.calculate_body(row))
        upper, lower = self.calculate_shadows(row)
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return False
        
        body_ratio = body / total_range
        lower_ratio = lower / total_range
        
        # Check if bullish body required
        if cfg.get('require_bullish_body', True) and row['Close'] <= row['Open']:
            return False
        
        return (body_ratio < cfg['max_body_ratio'] and 
                lower_ratio > cfg['min_lower_shadow_ratio'])
    
    def is_shooting_star(self, row):
        """Detect shooting star pattern (bearish reversal) using config thresholds."""
        cfg = SHOOTING_STAR_CONFIG
        body = abs(self.calculate_body(row))
        upper, lower = self.calculate_shadows(row)
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return False
        
        body_ratio = body / total_range
        upper_ratio = upper / total_range
        
        # Check if bearish body required
        if cfg.get('require_bearish_body', True) and row['Close'] >= row['Open']:
            return False
        
        return (body_ratio < cfg['max_body_ratio'] and 
                upper_ratio > cfg['min_upper_shadow_ratio'])
    
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
        """Detect doji pattern (indecision) using config threshold."""
        cfg = DOJI_CONFIG
        body = abs(self.calculate_body(row))
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return True
        
        return body / total_range < cfg['max_body_ratio']
    
    def is_marubozu(self, row):
        """Detect marubozu pattern (strong trend) using config thresholds."""
        cfg = MARUBOZU_CONFIG
        body = abs(self.calculate_body(row))
        upper, lower = self.calculate_shadows(row)
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return None
        
        shadow_size = upper + lower
        shadow_ratio = shadow_size / total_range if total_range > 0 else 0
        body_ratio = body / total_range
        
        max_shadow = cfg.get('max_shadow_ratio', 0.1)
        
        if body_ratio > cfg['min_body_ratio'] and shadow_ratio < max_shadow:
            if row['Close'] > row['Open']:
                return 'BULLISH_MARUBOZU'
            else:
                return 'BEARISH_MARUBOZU'
        
        return None
    
    def analyze_trend(self):
        """Analyze short-term trend direction using config parameters."""
        cfg = TREND_CONFIG
        df = self.df
        df['Trend'] = 'NEUTRAL'
        
        periods = cfg['lookback_periods']
        up_thresh = cfg['uptrend_threshold']
        down_thresh = cfg['downtrend_threshold']
        
        for i in range(periods, len(df)):
            window = df.iloc[i-periods:i]
            start_price = window['Close'].iloc[0]
            end_price = window['Close'].iloc[-1]
            
            change_pct = (end_price - start_price) / start_price * 100
            
            if change_pct > up_thresh:
                df.iloc[i, df.columns.get_loc('Trend')] = 'UPTREND'
            elif change_pct < down_thresh:
                df.iloc[i, df.columns.get_loc('Trend')] = 'DOWNTREND'
        
        return df
    
    def evaluate_single_candle(self, idx):
        """Evaluate signal for a single candle using config weights."""
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
        """Determine final signal strength using configurable weights."""
        w = self.cfg_components
        score = 0
        
        # Body contribution
        if body > 0:
            score += w['body_positive']
        elif body < 0:
            score += w['body_negative']
        
        # Pattern contribution
        bullish_patterns = ['BULLISH_ENGULFING', 'BULLISH_MARUBOZU', 'HAMMER']
        bearish_patterns = ['BEARISH_ENGULFING', 'BEARISH_MARUBOZU', 'SHOOTING_STAR']
        
        if any(p in patterns for p in bullish_patterns):
            score += w['bullish_pattern']
        if any(p in patterns for p in bearish_patterns):
            score += w['bearish_pattern']
        if 'DOJI' in patterns:
            score = 0
        
        # Trend contribution
        if trend == 'UPTREND':
            score += w['uptrend']
        elif trend == 'DOWNTREND':
            score += w['downtrend']
        
        # Map score to signal (using thresholds that can be made configurable)
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
    
    def get_summary(self, last_n=None):
        """Get summary of recent signals using config."""
        if last_n is None:
            last_n = SUMMARY_CONFIG.get('signal_distribution_periods', 20)

        recent = self.signals[-last_n:]

        counts = {
            'STRONG_BULLISH': 0, 'BULLISH': 0, 'NEUTRAL': 0,
            'BEARISH': 0, 'STRONG_BEARISH': 0
        }

        for sig in recent:
            counts[sig['signal']] += 1

        # Calculate weighted score with proper weights
        total_weighted_score = sum(
            self.cfg_weights[sig['signal']]
            for sig in recent
        )

        # Calculate max possible score untuk normalisasi (-2 to +2 range)
        max_possible = 2 * len(recent)  # Jika semua STRONG_BULLISH (+2)
        min_possible = -2 * len(recent)  # Jika semua STRONG_BEARISH (-2)

        # Normalized score: -1.0 to +1.0 scale
        if recent:
            normalized_score = total_weighted_score / (2 * len(recent))  # Scale ke -1 sampai 1
        else:
            normalized_score = 0

        # Raw average untuk debug
        avg_score = total_weighted_score / len(recent) if recent else 0

        # Use config to determine sentiment
        sentiment = get_sentiment(normalized_score)

        recent_count = SUMMARY_CONFIG.get('recent_signals_count', 5)

        return {
            'periods_analyzed': last_n,
            'signal_counts': counts,
            'weighted_score': round(normalized_score, 2),
            'raw_score': round(avg_score, 2),
            'overall_sentiment': sentiment,
            'recent_signals': recent[-recent_count:]
        }
    
    def print_report(self):
        """Print signal evaluation report."""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("SIGNAL EVALUATION REPORT")
        print("=" * 60)

        print(f"\nPeriods Analyzed: {summary['periods_analyzed']}")
        print("\nSignal Distribution (with Weights):")

        total_bullish = summary['signal_counts']['STRONG_BULLISH'] + summary['signal_counts']['BULLISH']
        total_bearish = summary['signal_counts']['STRONG_BEARISH'] + summary['signal_counts']['BEARISH']
        neutral = summary['signal_counts']['NEUTRAL']

        for signal, count in summary['signal_counts'].items():
            weight = self.cfg_weights[signal]
            bar = "#" * count + "-" * (summary['periods_analyzed'] - count)
            print(f"  {signal:16} : {bar} ({count}) [weight: {weight:+d}]")

        print(f"\n{'-' * 60}")
        print(f"  Bullish Total : {total_bullish}")
        print(f"  Bearish Total : {total_bearish}")
        print(f"  Neutral       : {neutral}")
        print(f"{'-' * 60}")

        print(f"\nScore Calculation:")
        print(f"  Raw Score       : {summary['raw_score']:+.2f}")
        print(f"  Normalized Score: {summary['weighted_score']:+.2f} (range: -1.0 to +1.0)")
        print(f"  Formula         : sum(weights) / (2 x count)")
        print(f"  Threshold       : >=0.5 Strong, >=0.2 Bull, <=-0.2 Bear, <=-0.5 Strong")

        print(f"\nOverall Sentiment: {summary['overall_sentiment']}")

        print("\nRecent Signals (Last {}):".format(len(summary['recent_signals'])))
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
