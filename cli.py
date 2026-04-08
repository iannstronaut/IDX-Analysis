#!/usr/bin/env python3
"""
IDX Technical Analysis - Command Line Interface (CLI)
====================================================

Interactive CLI untuk analisis teknikal saham IDX.

Cara penggunaan:
    python cli.py [command] [options]

Commands:
    fetch       Fetch data dari Yahoo Finance
    analyze     Analisis lengkap dengan semua indikator
    score       Evaluasi scoring berdasarkan timeframe
    signal      Evaluasi sinyal candlestick
    config      Lihat/ubah konfigurasi scoring
    report      Generate laporan lengkap
    interactive Mode interaktif (wizard)

Examples:
    python cli.py fetch --emiten BBCA
    python cli.py analyze --emiten BBRI --timeframe weekly
    python cli.py score --emiten TLKM --timeframe daily
    python cli.py interactive
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append('.')


def print_header():
    """Print ASCII art header."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           IDX TECHNICAL ANALYSIS TOOL                        ║
║           Command Line Interface                             ║
╚══════════════════════════════════════════════════════════════╝
    """)


def print_success(msg):
    """Print success message."""
    print(f"✓ {msg}")


def print_error(msg):
    """Print error message."""
    print(f"✗ {msg}")


def print_info(msg):
    """Print info message."""
    print(f"ℹ {msg}")


def print_warning(msg):
    """Print warning message."""
    print(f"⚠ {msg}")


def cmd_fetch(args):
    """Command: Fetch data from Yahoo Finance."""
    print_header()
    print_info(f"Fetching data for {args.emiten}.JK...")
    
    from data.add_indicators import process_and_save
    
    try:
        df = process_and_save(emiten=args.emiten, interval=args.interval)
        print_success(f"Data saved to output/{args.emiten}_past_3_year.csv")
        print(f"\n  Total rows: {len(df)}")
        print(f"  Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        print(f"  Columns: {', '.join(df.columns)}")
    except Exception as e:
        print_error(f"Failed to fetch data: {e}")
        return 1
    
    return 0


def cmd_analyze(args):
    """Command: Run complete analysis."""
    print_header()
    print_info(f"Running analysis for {args.emiten}.JK ({args.timeframe})...")
    
    from data.add_indicators import process_and_save
    from evaluation.scoring import TechnicalScorer
    from evaluation.signal_eval import SignalEvaluator
    
    try:
        # Step 1: Fetch & add indicators
        print("\n[Step 1/3] Fetching data and calculating indicators...")
        df = process_and_save(emiten=args.emiten, interval="1d")
        
        # Step 2: Scoring
        print(f"\n[Step 2/3] Running scoring evaluation ({args.timeframe})...")
        scorer = TechnicalScorer(df)
        scorer.set_period(args.timeframe)
        
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
        
        # Step 3: Signal evaluation
        print("\n[Step 3/3] Running signal evaluation...")
        evaluator = SignalEvaluator(df)
        evaluator.evaluate_all()
        
        # Generate reports
        generate_reports(df, scorer, evaluator, args.emiten, args.timeframe)
        
        # Print summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\nOverall Score: {scorer.get_overall_score()}/100")
        print(f"Recommendation: {scorer.get_recommendation()}")
        print(f"Signal Sentiment: {evaluator.get_summary()['overall_sentiment']}")
        print(f"\nOutput files in output/ directory")
        
    except Exception as e:
        print_error(f"Analysis failed: {e}")
        return 1
    
    return 0


def cmd_score(args):
    """Command: Run scoring evaluation only."""
    print_header()
    print_info(f"Running scoring for {args.emiten}.JK ({args.timeframe})...")
    
    from evaluation.scoring import run_evaluation
    
    try:
        scorer = run_evaluation(emiten=args.emiten, timeframe=args.timeframe)
        print_success(f"Scoring complete! Overall: {scorer.get_overall_score()}/100")
    except Exception as e:
        print_error(f"Scoring failed: {e}")
        return 1
    
    return 0


def cmd_signal(args):
    """Command: Run signal evaluation only."""
    print_header()
    print_info(f"Running signal evaluation for {args.emiten}.JK...")
    
    from evaluation.signal_eval import run_signal_evaluation
    
    try:
        evaluator = run_signal_evaluation(emiten=args.emiten)
        summary = evaluator.get_summary()
        print_success(f"Signal evaluation complete! Sentiment: {summary['overall_sentiment']}")
    except Exception as e:
        print_error(f"Signal evaluation failed: {e}")
        return 1
    
    return 0


def cmd_config(args):
    """Command: View or modify configuration."""
    print_header()
    
    if args.action == 'view':
        print_info("Current configuration:")
        try:
            from config.scoring_config import print_config_summary
            print_config_summary()
        except Exception as e:
            print_error(f"Could not load config: {e}")
            return 1
    
    elif args.action == 'edit':
        print_info("Opening config file...")
        config_path = Path('config/scoring_config.py')
        if config_path.exists():
            print(f"Please edit: {config_path.absolute()}")
            print("\nKey sections to edit:")
            print("  - TIME_FRAMES: Change evaluation periods")
            print("  - RSI_THRESHOLDS: Change RSI levels")
            print("  - *_CONFIG: Change pattern detection parameters")
        else:
            print_error("Config file not found!")
            return 1
    
    return 0


def cmd_report(args):
    """Command: Generate reports from existing data."""
    print_header()
    print_info(f"Generating reports for {args.emiten}.JK...")
    
    from utils import load_stock_data
    from evaluation.scoring import TechnicalScorer
    from evaluation.signal_eval import SignalEvaluator
    
    try:
        filepath = f"output/{args.emiten.upper()}_past_3_year.csv"
        df = load_stock_data(filepath)
        
        # Run evaluations
        scorer = TechnicalScorer(df)
        scorer.set_period(args.timeframe)
        
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
        
        evaluator = SignalEvaluator(df)
        evaluator.evaluate_all()
        
        # Generate reports
        generate_reports(df, scorer, evaluator, args.emiten, args.timeframe)
        
        print_success("Reports generated successfully!")
        print(f"\nFiles created:")
        print(f"  - output/{args.emiten}_summary_report.txt")
        print(f"  - output/{args.emiten}_report_{args.timeframe}.csv")
        
    except Exception as e:
        print_error(f"Report generation failed: {e}")
        return 1
    
    return 0


def cmd_interactive(args):
    """Command: Interactive wizard mode."""
    print_header()
    print("Welcome to Interactive Mode!\n")
    
    # Step 1: Get emiten
    print("Step 1: Select Stock")
    print("-" * 40)
    emiten = input("Enter stock ticker (default: BBCA): ").strip().upper() or "BBCA"
    
    # Step 2: Get timeframe
    print("\nStep 2: Select Timeframe")
    print("-" * 40)
    print("1. Daily (20 days)")
    print("2. Weekly (12 weeks)")
    print("3. Monthly (12 months)")
    
    tf_choice = input("Select [1-3] (default: 1): ").strip() or "1"
    timeframe_map = {"1": "daily", "2": "weekly", "3": "monthly"}
    timeframe = timeframe_map.get(tf_choice, "daily")
    
    # Step 3: Confirm
    print(f"\nStep 3: Confirm")
    print("-" * 40)
    print(f"Stock: {emiten}.JK")
    print(f"Timeframe: {timeframe}")
    
    confirm = input("\nProceed? [Y/n]: ").strip().lower()
    if confirm in ('n', 'no'):
        print("Cancelled.")
        return 0
    
    # Run analysis
    print("\n" + "="*60)
    class Args:
        pass
    
    args = Args()
    args.emiten = emiten
    args.timeframe = timeframe
    args.interval = "1d"
    
    return cmd_analyze(args)


def generate_reports(df, scorer, evaluator, emiten, timeframe):
    """Generate summary and timeframe reports."""
    import pandas as pd
    
    summary = evaluator.get_summary()
    overall_score = scorer.get_overall_score()
    recommendation = scorer.get_recommendation()
    
    # Get config for period info
    try:
        from config.scoring_config import TIME_FRAMES
        eval_period = TIME_FRAMES.get(timeframe, 20)
    except:
        eval_period = 20
    
    latest = df.iloc[-1]
    
    # Text report
    text_report = f"""
=================================================================
           {emiten}.JK TECHNICAL ANALYSIS SUMMARY REPORT
=================================================================

Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Data Period: {df['Date'].min().date()} to {df['Date'].max().date()}
Total Records: {len(df)} (3 Years with All Indicators)
Evaluation Timeframe: {timeframe.upper()} (Last {eval_period} periods)

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
Evaluation Period: {timeframe.upper()} (Last {eval_period} periods)
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

Signal Distribution:
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
    Path("output").mkdir(exist_ok=True)
    with open(f"output/{emiten}_summary_report.txt", "w") as f:
        f.write(text_report)
    
    # Save timeframe CSV
    df_filtered = df.tail(eval_period).copy()
    df_filtered.to_csv(f"output/{emiten}_report_{timeframe}.csv", index=False)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='cli.py',
        description='IDX Technical Analysis CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py fetch --emiten BBCA
  python cli.py analyze --emiten BBRI --timeframe weekly
  python cli.py score --emiten TLKM --timeframe daily
  python cli.py signal --emiten BBCA
  python cli.py config view
  python cli.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch stock data')
    fetch_parser.add_argument('--emiten', default='BBCA', help='Stock ticker')
    fetch_parser.add_argument('--interval', default='1d', choices=['1d', '1wk', '1mo'])
    fetch_parser.set_defaults(func=cmd_fetch)
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run complete analysis')
    analyze_parser.add_argument('--emiten', default='BBCA', help='Stock ticker')
    analyze_parser.add_argument('--timeframe', default='daily', 
                                choices=['daily', 'weekly', 'monthly'])
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Run scoring evaluation')
    score_parser.add_argument('--emiten', default='BBCA', help='Stock ticker')
    score_parser.add_argument('--timeframe', default='daily',
                             choices=['daily', 'weekly', 'monthly'])
    score_parser.set_defaults(func=cmd_score)
    
    # Signal command
    signal_parser = subparsers.add_parser('signal', help='Run signal evaluation')
    signal_parser.add_argument('--emiten', default='BBCA', help='Stock ticker')
    signal_parser.set_defaults(func=cmd_signal)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='View/edit configuration')
    config_parser.add_argument('action', choices=['view', 'edit'], 
                              help='View or edit config')
    config_parser.set_defaults(func=cmd_config)
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_parser.add_argument('--emiten', default='BBCA', help='Stock ticker')
    report_parser.add_argument('--timeframe', default='daily',
                              choices=['daily', 'weekly', 'monthly'])
    report_parser.set_defaults(func=cmd_report)
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', 
                                               help='Interactive wizard mode')
    interactive_parser.set_defaults(func=cmd_interactive)
    
    # Parse args
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Run command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
