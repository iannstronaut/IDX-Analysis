"""
Scoring Configuration Module
============================
Konfigurasi scoring untuk technical analysis.
Edit file ini untuk mengubah parameter scoring tanpa mengubah kode utama.

Panduan Penggunaan:
- TIME_FRAMES: Atur periode evaluasi untuk masing-masing timeframe
- INDICATOR_WEIGHTS: Atur bobot untuk masing-masing indikator (MA20, MA50, RSI, MACD, EMA_Cross)
- SCORE_THRESHOLDS: Atur batas nilai untuk kategori bullish/bearish
- SIGNAL_WEIGHTS: Atur bobot untuk masing-masing sinyal
- RECOMMENDATION_RULES: Atur aturan rekomendasi buy/sell/hold
- PATTERN_THRESHOLDS: Atur threshold deteksi candlestick patterns
- TREND_SETTINGS: Atur parameter analisis trend

Contoh Konfigurasi Bobot Indikator:
- MA20: 1.0       → Bobot normal
- MA50: 1.2       → 20% lebih penting dari MA20
- RSI: 1.0        → Bobot normal
- MACD: 1.5       → 50% lebih penting (prioritas momentum)
- EMA_Cross: 1.3  → 30% lebih penting (trend following)
Total bobot akan dinormalisasi otomatis (total = 100%)
"""

# =============================================================================
# 1. TIME FRAME CONFIGURATION
# =============================================================================
# Atur periode evaluasi untuk masing-masing timeframe
# Format: 'timeframe': jumlah_periode

TIME_FRAMES = {
    'daily': 20,      # 20 hari untuk evaluasi harian
    'weekly': 12,     # 12 minggu untuk evaluasi mingguan
    'monthly': 12,    # 12 bulan untuk evaluasi bulanan
}

# =============================================================================
# 2. SCORE THRESHOLDS
# =============================================================================
# Atur batas nilai untuk kategori scoring
# Format: (min_score, max_score, label)

MA_THRESHOLDS = {
    'bullish': 60,    # Score > 60 = Bullish
    'bearish': 40,    # Score < 40 = Bearish
    'neutral_min': 40,
    'neutral_max': 60,
}

RSI_THRESHOLDS = {
    'overbought': 70,
    'oversold': 30,
    'bullish_min': 55,
    'bearish_max': 45,
}

MACD_THRESHOLDS = {
    'bullish': 60,    # Persentase hari bullish
    'bearish': 40,
}

EMA_CROSS_THRESHOLDS = {
    'bullish': 60,    # Persentase hari golden cross
    'bearish': 40,
}

# =============================================================================
# 3. INDICATOR WEIGHTS (Scoring)
# =============================================================================
# Atur bobot untuk masing-masing indikator dalam perhitungan overall score
# Format: 'indicator_name': bobot (1.0 = normal, 0.5 = setengah bobot, 2.0 = 2x bobot)
# Total bobot akan dinormalisasi otomatis

INDICATOR_WEIGHTS = {
    'MA20': 1.0,       # Moving Average 20 - bobot default
    'MA50': 1.2,       # Moving Average 50 - sedikit lebih tinggi (trend jangka menengah)
    'RSI': 1.0,        # RSI - bobot default
    'MACD': 1.5,       # MACD - lebih tinggi (momentum indicator)
    'EMA_Cross': 1.3,  # EMA Cross - sedikit lebih tinggi (trend following)
}

# =============================================================================
# 4. SIGNAL WEIGHTS
# =============================================================================
# Atur bobot untuk perhitungan sinyal keseluruhan
# Format: 'signal_name': bobot

SIGNAL_STRENGTH_WEIGHTS = {
    'STRONG_BULLISH': 2,
    'BULLISH': 1,
    'NEUTRAL': 0,
    'BEARISH': -1,
    'STRONG_BEARISH': -2,
}

# Bobot untuk komponen sinyal
SIGNAL_COMPONENT_WEIGHTS = {
    'body_positive': 1,          # Candle bullish
    'body_negative': -1,         # Candle bearish
    'bullish_pattern': 2,        # Hammer, Bullish Engulfing, dll
    'bearish_pattern': -2,       # Shooting Star, Bearish Engulfing, dll
    'uptrend': 1,                # Trend naik
    'downtrend': -1,             # Trend turun
}

# =============================================================================
# 5. RECOMMENDATION RULES
# =============================================================================
# Atur aturan untuk rekomendasi trading

RECOMMENDATION_THRESHOLDS = {
    'STRONG_BUY': {
        'min_overall_score': 70,
        'min_bullish_indicators': 0.6,  # 60% indikator bullish
    },
    'BUY': {
        'min_overall_score': 55,
    },
    'STRONG_SELL': {
        'max_overall_score': 30,
        'min_bearish_indicators': 0.6,  # 60% indikator bearish
    },
    'SELL': {
        'max_overall_score': 45,
    },
    'HOLD': {
        # Default jika tidak memenuhi kondisi di atas
    },
}

# =============================================================================
# 6. CANDLESTICK PATTERN THRESHOLDS
# =============================================================================
# Atur parameter deteksi candlestick patterns

HAMMER_CONFIG = {
    'max_body_ratio': 0.3,       # Body maksimal 30% dari range
    'min_lower_shadow_ratio': 0.6,  # Lower shadow minimal 60% dari range
    'max_upper_shadow_ratio': 0.1,  # Upper shadow maksimal 10% dari body
    'require_bullish_body': True,   # Harus candle bullish
}

SHOOTING_STAR_CONFIG = {
    'max_body_ratio': 0.3,
    'min_upper_shadow_ratio': 0.6,
    'max_lower_shadow_ratio': 0.1,
    'require_bearish_body': True,
}

DOJI_CONFIG = {
    'max_body_ratio': 0.1,       # Body sangat kecil (<10% range)
}

MARUBOZU_CONFIG = {
    'min_body_ratio': 0.9,       # Body besar (>90% range)
    'max_shadow_ratio': 0.1,     # Shadow sangat kecil
}

ENGULFING_CONFIG = {
    'min_body_multiplier': 1.0,  # Body current harus lebih besar dari previous
}

# =============================================================================
# 7. TREND ANALYSIS SETTINGS
# =============================================================================
# Atur parameter analisis trend

TREND_CONFIG = {
    'lookback_periods': 5,       # Periode untuk analisis trend
    'uptrend_threshold': 3,       # % kenaikan untuk dianggap uptrend
    'downtrend_threshold': -3,  # % penurunan untuk dianggap downtrend
}

# =============================================================================
# 8. EVALUATION SUMMARY SETTINGS
# =============================================================================
# Atur parameter untuk summary report

SUMMARY_CONFIG = {
    'recent_signals_count': 5,    # Jumlah sinyal terakhir yang ditampilkan
    'signal_distribution_periods': 20,  # Periode untuk distribusi sinyal
}

# =============================================================================
# 9. SENTIMENT THRESHOLDS
# =============================================================================
# Atur batas untuk penentuan sentiment keseluruhan

SENTIMENT_THRESHOLDS = {
    'strong_bullish': 0.5,   # Weighted score >= 0.5 = STRONG_BULLISH
    'bullish': 0.2,        # Weighted score >= 0.2 = BULLISH
    'bearish': -0.2,       # Weighted score <= -0.2 = BEARISH
    'strong_bearish': -0.5,# Weighted score <= -0.5 = STRONG_BEARISH
}

# =============================================================================
# Helper Functions
# =============================================================================

def get_timeframe_period(timeframe='daily'):
    """Get evaluation period for specified timeframe."""
    return TIME_FRAMES.get(timeframe, 20)


def get_recommendation(score, bullish_count, total_indicators, directions):
    """
    Determine recommendation based on score and indicator directions.
    
    Parameters:
    -----------
    score : float
        Overall score (0-100)
    bullish_count : int
        Number of bullish indicators
    total_indicators : int
        Total number of indicators
    directions : list
        List of indicator directions
    
    Returns:
    --------
    str : Recommendation (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL)
    """
    bullish_ratio = bullish_count / total_indicators if total_indicators > 0 else 0
    bearish_count = directions.count('Bearish') + directions.count('Oversold')
    bearish_ratio = bearish_count / total_indicators if total_indicators > 0 else 0
    
    rules = RECOMMENDATION_THRESHOLDS
    
    # Check STRONG_BUY
    if (score >= rules['STRONG_BUY']['min_overall_score'] and 
        bullish_ratio >= rules['STRONG_BUY']['min_bullish_indicators']):
        return 'STRONG_BUY'
    
    # Check BUY
    if score >= rules['BUY']['min_overall_score']:
        return 'BUY'
    
    # Check STRONG_SELL
    if (score <= rules['STRONG_SELL']['max_overall_score'] and 
        bearish_ratio >= rules['STRONG_SELL']['min_bearish_indicators']):
        return 'STRONG_SELL'
    
    # Check SELL
    if score <= rules['SELL']['max_overall_score']:
        return 'SELL'
    
    # Default HOLD
    return 'HOLD'


def get_sentiment(weighted_score):
    """
    Get sentiment based on weighted score.

    Threshold:
    - weighted_score >= 0.5  → STRONG_BULLISH
    - weighted_score >= 0.2  → BULLISH
    - weighted_score <= -0.5 → STRONG_BEARISH
    - weighted_score <= -0.2 → BEARISH
    - else                   → NEUTRAL
    """
    th = SENTIMENT_THRESHOLDS

    if weighted_score >= th['strong_bullish']:
        return 'STRONG_BULLISH'
    elif weighted_score >= th['bullish']:
        return 'BULLISH'
    elif weighted_score <= th['strong_bearish']:
        return 'STRONG_BEARISH'
    elif weighted_score <= th['bearish']:
        return 'BEARISH'

    return 'NEUTRAL'


def get_indicator_weights():
    """
    Get normalized indicator weights (sum to 1.0).
    Returns a dict with normalized weights for each indicator.
    """
    total_weight = sum(INDICATOR_WEIGHTS.values())
    if total_weight == 0:
        return {k: 1.0 / len(INDICATOR_WEIGHTS) for k in INDICATOR_WEIGHTS}
    return {k: v / total_weight for k, v in INDICATOR_WEIGHTS.items()}


def get_indicator_weight(indicator_name):
    """
    Get normalized weight for a specific indicator.

    Parameters:
    -----------
    indicator_name : str
        Name of the indicator (e.g., 'MA20', 'RSI', 'MACD')

    Returns:
    --------
    float : Normalized weight (0.0 to 1.0)
    """
    weights = get_indicator_weights()
    return weights.get(indicator_name, 1.0 / len(INDICATOR_WEIGHTS))


def print_config_summary():
    """Print current configuration summary."""
    print("=" * 60)
    print("SCORING CONFIGURATION SUMMARY")
    print("=" * 60)

    print("\n1. Time Frames:")
    for tf, period in TIME_FRAMES.items():
        print(f"   {tf}: {period} periods")

    print("\n2. Indicator Weights:")
    normalized = get_indicator_weights()
    for ind, raw in INDICATOR_WEIGHTS.items():
        norm = normalized.get(ind, 0)
        print(f"   {ind}: {raw:.1f} (normalized: {norm:.2%})")

    print("\n3. Recommendation Thresholds:")
    for rec, rules in RECOMMENDATION_THRESHOLDS.items():
        if rules:
            print(f"   {rec}: {rules}")

    print("\n4. Pattern Detection Thresholds:")
    print(f"   Hammer max body ratio: {HAMMER_CONFIG['max_body_ratio']}")
    print(f"   Doji max body ratio: {DOJI_CONFIG['max_body_ratio']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Print current configuration when run directly
    print_config_summary()
