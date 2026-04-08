"""
Main Orchestrator for BBCA.JK Technical Analysis
Flow: Fetch 3Y → Add Indicators → Save → Evaluate by timeframe
"""

import sys
sys.path.append('data')
sys.path.append('indicators')
sys.path.append('evaluation')

import pandas as pd
from pathlib import Path


def run_pipeline(emiten='BBCA', timeframe='daily'):
    """
    Run complete analysis pipeline.
    
    Flow:
    1. Fetch 3 years data + calculate all indicators
    2. Save to data/{emiten}_past_3_year.csv
    3. Evaluate scoring based on timeframe (last N periods)
    4. Signal evaluation (candlestick patterns)
    5. Generate summary report (overall + timeframe filtered data)
    """
    print("=" * 60)
    print(f"{emiten}.JK TECHNICAL ANALYSIS PIPELINE")
    print("=" * 60)
    
    # 1. Fetch Data + Add Indicators
    print(f"\n[1/4] Fetching 3 Years Data + Calculating Indicators...")
    from data.add_indicators import process_and_save
    
    df = process_and_save(emiten=emiten, interval="1d")
    
    print(f"\nData saved with all indicators to: output/{emiten}_past_3_year.csv")
    print(f"Total rows: {len(df)} ({df['Date'].min().date()} to {df['Date'].max().date()})")
    
    # 2. Run Evaluation Scoring (on last N periods based on timeframe)
    print(f"\n[2/4] Running Evaluation Scoring ({timeframe})...")
    from evaluation.scoring import TechnicalScorer
    
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
    
    # 3. Run Signal Evaluation
    print("\n[3/4] Running Signal Evaluation...")
    from evaluation.signal_eval import SignalEvaluator
    
    evaluator = SignalEvaluator(df)
    evaluator.evaluate_all()
    evaluator.print_report()
    
    # 4. Generate Summary Report
    print("\n[4/4] Generating Summary Report...")
    generate_summary_report(df, scorer, evaluator, emiten, timeframe)
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nOutput Files:")
    print(f"  - output/{emiten}_past_3_year.csv (3Y data + all indicators)")
    print(f"  - output/{emiten}_summary_report.txt (overall analysis)")
    print(f"  - output/{emiten}_report_{timeframe}.csv (filtered data for {timeframe})")


def generate_summary_report(df, scorer, evaluator, emiten, timeframe):
    """Generate both text summary (overall) and CSV report (timeframe filtered)."""
    summary = evaluator.get_summary()
    overall_score = scorer.get_overall_score()
    recommendation = scorer.get_recommendation()
    
    # Get evaluation period info
    period_map = {'daily': 20, 'weekly': 12, 'monthly': 12}
    period_labels = {'daily': '20 days', 'weekly': '12 weeks', 'monthly': '12 months'}
    eval_period_count = period_map.get(timeframe, 20)
    eval_period_label = period_labels.get(timeframe, '20 days')
    
    latest = df.iloc[-1]
    
    # === 1. TEXT REPORT (Overall Analysis) ===
    text_report = f"""
=================================================================
           {emiten}.JK TECHNICAL ANALYSIS SUMMARY REPORT
=================================================================

Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Data Period: {df['Date'].min().date()} to {df['Date'].max().date()}
Total Records: {len(df)} (3 Years of Data with All Indicators)
Evaluation Timeframe: {timeframe.upper()} (Last {eval_period_label})

-----------------------------------------------------------------
                      CURRENT MARKET DATA
-----------------------------------------------------------------
Date: {latest['Date'].date()}
Close: Rp {latest['Close']:,.0f}
Open:  Rp {latest['Open']:,.0f}
High:  Rp {latest['High']:,.0f}
Low:   Rp {latest['Low']:,.0f}
Volume: {latest['Volume']:,.0f}

-----------------------------------------------------------------
                      TECHNICAL INDICATORS
-----------------------------------------------------------------
MA20:     {latest.get('MA20', 'N/A'):,.2f}
MA50:     {latest.get('MA50', 'N/A'):,.2f}
RSI(14):  {latest.get('RSI', 'N/A'):.2f}
MACD:     {latest.get('MACD_Line', 'N/A'):.4f}
Signal:   {latest.get('MACD_Signal', 'N/A'):.4f}
EMA12:    {latest.get('EMA12', 'N/A'):,.2f}
EMA26:    {latest.get('EMA26', 'N/A'):,.2f}

-----------------------------------------------------------------
                        SCORING SUMMARY
-----------------------------------------------------------------
Evaluation Period: {timeframe.upper()} (Last {eval_period_label})
Overall Score: {overall_score}/100
Recommendation: {recommendation}

Individual Scores:
"""
    
    for name, data in scorer.scores.items():
        text_report += f"  {name}: {data['score']:.2f} ({data['direction']})\n"
    
    text_report += f"""
-----------------------------------------------------------------
                       SIGNAL EVALUATION
-----------------------------------------------------------------
Overall Sentiment: {summary['overall_sentiment']}
Weighted Score: {summary['weighted_score']}

Signal Distribution (Last {eval_period_label}):
"""
    
    for signal, count in summary['signal_counts'].items():
        text_report += f"  {signal}: {count}\n"
    
    text_report += """
-----------------------------------------------------------------
                          DISCLAIMER
-----------------------------------------------------------------
This analysis is for educational purposes only. 
Not financial advice. Trade at your own risk.

=================================================================
"""
    
    # Save text report
    text_file = f"output/{emiten}_summary_report.txt"
    with open(text_file, "w") as f:
        f.write(text_report)
    print(f"Text summary saved to {text_file}")
    
    # === 2. CSV REPORT (Filtered Data for Timeframe) ===
    # Filter df to only include last N periods based on timeframe
    df_filtered = df.tail(eval_period_count).copy()
    
    # Save filtered data
    csv_file = f"output/{emiten}_report_{timeframe}.csv"
    df_filtered.to_csv(csv_file, index=False)
    print(f"Filtered data ({eval_period_label}) saved to {csv_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='BBCA.JK Technical Analysis')
    parser.add_argument('--emiten', default='BBCA', help='Stock ticker (default: BBCA)')
    parser.add_argument('--timeframe', choices=['daily', 'weekly', 'monthly'],
                       default='daily', help='Evaluation timeframe (daily=20 days, weekly=12 weeks, monthly=12 months)')
    
    args = parser.parse_args()
    
    run_pipeline(emiten=args.emiten, timeframe=args.timeframe)
