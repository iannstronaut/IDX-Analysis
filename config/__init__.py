"""
Configuration Module for Technical Analysis
===========================================

Module ini berisi konfigurasi scoring yang dapat diedit tanpa
mengubah kode utama.

Cara penggunaan:
1. Edit file scoring_config.py untuk mengubah parameter
2. Jalankan main.py atau script evaluation
3. Perubahan akan otomatis diterapkan

Struktur:
- scoring_config.py : Konfigurasi utama scoring
"""

from .scoring_config import (
    TIME_FRAMES,
    MA_THRESHOLDS,
    RSI_THRESHOLDS,
    MACD_THRESHOLDS,
    EMA_CROSS_THRESHOLDS,
    SIGNAL_STRENGTH_WEIGHTS,
    SIGNAL_COMPONENT_WEIGHTS,
    RECOMMENDATION_THRESHOLDS,
    HAMMER_CONFIG,
    SHOOTING_STAR_CONFIG,
    DOJI_CONFIG,
    MARUBOZU_CONFIG,
    TREND_CONFIG,
    SUMMARY_CONFIG,
    SENTIMENT_THRESHOLDS,
    get_timeframe_period,
    get_recommendation,
    get_sentiment,
    print_config_summary,
)

__all__ = [
    'TIME_FRAMES',
    'MA_THRESHOLDS',
    'RSI_THRESHOLDS',
    'MACD_THRESHOLDS',
    'EMA_CROSS_THRESHOLDS',
    'SIGNAL_STRENGTH_WEIGHTS',
    'SIGNAL_COMPONENT_WEIGHTS',
    'RECOMMENDATION_THRESHOLDS',
    'HAMMER_CONFIG',
    'SHOOTING_STAR_CONFIG',
    'DOJI_CONFIG',
    'MARUBOZU_CONFIG',
    'TREND_CONFIG',
    'SUMMARY_CONFIG',
    'SENTIMENT_THRESHOLDS',
    'get_timeframe_period',
    'get_recommendation',
    'get_sentiment',
    'print_config_summary',
]
