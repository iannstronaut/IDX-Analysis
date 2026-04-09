"""
Chart Generation Module
Generates professional stock charts with indicators using mplfinance.
Styling inspired by Stockbit - modern, clean, and professional.
"""

import pandas as pd
import mplfinance as mpf
from pathlib import Path
import sys
sys.path.append('..')
from utils import load_stock_data


def prepare_data(df):
    """
    Prepare dataframe for mplfinance (requires specific column names).

    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with indicators

    Returns:
    --------
    pd.DataFrame : Properly formatted dataframe for mplfinance
    """
    df = df.copy()

    # Ensure Date is datetime and set as index
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

    # Rename columns to mplfinance standard (if not already)
    column_mapping = {
        'Open': 'Open',
        'High': 'High',
        'Low': 'Low',
        'Close': 'Close',
        'Volume': 'Volume'
    }

    # Ensure proper column names exist
    for std_name, req_name in column_mapping.items():
        if std_name not in df.columns and std_name.lower() in df.columns:
            df.rename(columns={std_name.lower(): std_name}, inplace=True)

    return df


def create_stockbit_style():
    """
    Create modern Stockbit-like style for charts.
    Returns mplfinance style configuration.
    """
    # Stockbit-inspired colors (dark theme with vibrant accents)
    mc = mpf.make_marketcolors(
        up='#00C853',      # Bright green for bullish
        down='#FF3D00',    # Bright red for bearish
        edge='inherit',
        wick='inherit',
        volume='in',
        inherit=True
    )

    # Create the style with dark background
    s = mpf.make_mpf_style(
        marketcolors=mc,
        figcolor='#1A1A2E',      # Deep dark blue background
        facecolor='#16213E',      # Slightly lighter panel background
        edgecolor='#0F3460',      # Border color
        gridcolor='#2D3748',      # Grid lines
        gridstyle='-',
        rc={
            'axes.labelcolor': '#E94560',
            'axes.edgecolor': '#0F3460',
            'axes.linewidth': 1.5,
            'xtick.color': '#EAEAEA',
            'ytick.color': '#EAEAEA',
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'font.size': 10,
            'font.family': 'sans-serif',
            'axes.grid': True,
            'grid.alpha': 0.3,
        }
    )

    return s, mc


def generate_chart(df, emiten='STOCK', timeframe='daily', output_path=None, 
                   start=None, end=None, figsize=(14, 12)):
    """
    Generate professional stock chart with all indicators.

    Layout:
    - Panel 0: Main chart (Price + MA20 + MA50 + EMA12 + EMA26)
    - Panel 1: MACD (MACD Line, Signal, Histogram)
    - Panel 2: Volume

    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with all indicators calculated
    emiten : str
        Stock ticker for title
    timeframe : str
        Timeframe label for title
    output_path : str, optional
        Path to save chart. If None, saves to output/{emiten}_chart.png
    start : str, optional
        Start date for filtering
    end : str, optional
        End date for filtering
    figsize : tuple
        Figure size (width, height)

    Returns:
    --------
    str : Path to saved chart file
    """
    from data.fetch_data import parse_date

    # Prepare data
    df = prepare_data(df)

    # Filter by date range if provided
    if start:
        start_date = parse_date(start)
        df = df[df.index >= start_date]
    if end:
        end_date = parse_date(end)
        df = df[df.index <= end_date]

    if len(df) == 0:
        raise ValueError("No data available for the specified date range")

    # Get style
    style, mc = create_stockbit_style()

    # Prepare additional plots (indicators)
    addplots = []

    # Panel 0: Moving Averages and EMAs (main chart)
    if 'MA20' in df.columns:
        addplots.append(mpf.make_addplot(
            df['MA20'], 
            color='#00BCD4',  # Cyan
            width=1.2,
            label='MA20',
            panel=0
        ))

    if 'MA50' in df.columns:
        addplots.append(mpf.make_addplot(
            df['MA50'], 
            color='#FF9800',  # Orange
            width=1.2,
            label='MA50',
            panel=0
        ))

    if 'EMA12' in df.columns:
        addplots.append(mpf.make_addplot(
            df['EMA12'], 
            color='#E040FB',  # Purple
            width=1.0,
            linestyle='--',
            label='EMA12',
            panel=0
        ))

    if 'EMA26' in df.columns:
        addplots.append(mpf.make_addplot(
            df['EMA26'], 
            color='#FFEB3B',  # Yellow
            width=1.0,
            linestyle='--',
            label='EMA26',
            panel=0
        ))

    # Panel 1: MACD
    if 'MACD_Line' in df.columns and 'MACD_Signal' in df.columns:
        # MACD Line
        addplots.append(mpf.make_addplot(
            df['MACD_Line'],
            color='#00E5FF',  # Light cyan
            width=1.2,
            label='MACD',
            panel=1
        ))

        # Signal Line
        addplots.append(mpf.make_addplot(
            df['MACD_Signal'],
            color='#FF4081',  # Pink
            width=1.2,
            label='Signal',
            panel=1
        ))

        # MACD Histogram (bar chart)
        if 'MACD_Histogram' in df.columns:
            # Color histogram based on positive/negative
            colors = ['#00C853' if v >= 0 else '#FF3D00' for v in df['MACD_Histogram']]
            addplots.append(mpf.make_addplot(
                df['MACD_Histogram'],
                type='bar',
                color=colors,
                width=0.7,
                alpha=0.7,
                panel=1,
                ylabel='MACD'
            ))

    # Panel 2: Volume (will be added via volume_panel parameter)

    # Create figure with subplots
    # Layout: [main, macd, volume]
    fig, axes = mpf.plot(
        df,
        type='candle',
        style=style,
        title=f'\n{emiten.upper()}.JK - {timeframe.upper()} Technical Analysis',
        ylabel='Price (IDR)',
        ylabel_lower='',
        volume=True,
        volume_panel=2,  # Volume in panel 2
        panel_ratios=(3, 1, 1),  # Main:MACD:Volume height ratio
        addplot=addplots,
        figsize=figsize,
        returnfig=True,
        tight_layout=True,
        show_nontrading=False
    )

    # Customize axes further
    axes[0].set_ylabel('Price (IDR)', color='#EAEAEA', fontsize=10, fontweight='bold')
    axes[1].set_ylabel('MACD', color='#EAEAEA', fontsize=9)
    axes[2].set_ylabel('Volume', color='#EAEAEA', fontsize=9)

    # Add legend for main chart indicators
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#00BCD4', lw=1.2, label='MA20'),
        Line2D([0], [0], color='#FF9800', lw=1.2, label='MA50'),
        Line2D([0], [0], color='#E040FB', lw=1.0, linestyle='--', label='EMA12'),
        Line2D([0], [0], color='#FFEB3B', lw=1.0, linestyle='--', label='EMA26'),
    ]
    axes[0].legend(
        handles=legend_elements,
        loc='upper left',
        framealpha=0.8,
        facecolor='#1A1A2E',
        edgecolor='#0F3460',
        labelcolor='#EAEAEA',
        fontsize=8
    )

    # MACD legend
    macd_legend = [
        Line2D([0], [0], color='#00E5FF', lw=1.2, label='MACD'),
        Line2D([0], [0], color='#FF4081', lw=1.2, label='Signal'),
    ]
    axes[1].legend(
        handles=macd_legend,
        loc='upper left',
        framealpha=0.8,
        facecolor='#1A1A2E',
        edgecolor='#0F3460',
        labelcolor='#EAEAEA',
        fontsize=8
    )

    # Save figure
    if output_path is None:
        output_path = f"output/{emiten.upper()}_chart.png"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='#1A1A2E', edgecolor='none')
    print(f"Chart saved to: {output_path}")

    # Close figure to free memory
    import matplotlib.pyplot as plt
    plt.close(fig)

    return output_path


def generate_chart_from_file(filepath=None, emiten='BBCA', **kwargs):
    """
    Generate chart from CSV file.

    Parameters:
    -----------
    filepath : str, optional
        Path to CSV. If None, uses output/{emiten}_past_3_year.csv
    emiten : str
        Stock ticker
    **kwargs : dict
        Additional arguments passed to generate_chart()

    Returns:
    --------
    str : Path to saved chart file
    """
    if filepath is None:
        filepath = f"output/{emiten.upper()}_past_3_year.csv"

    print(f"Loading data from: {filepath}")
    df = load_stock_data(filepath)
    print(f"Data loaded: {len(df)} rows")

    return generate_chart(df, emiten=emiten, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate stock chart with indicators',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chart.py --emiten BBCA
  python chart.py --emiten BBRI --start 2025-01-01 --end 2025-12-31
  python chart.py --file output/custom_data.csv --emiten TLKM
        """
    )

    parser.add_argument('--emiten', default='BBCA', help='Stock ticker (default: BBCA)')
    parser.add_argument('--file', help='Input CSV file path')
    parser.add_argument('--output', help='Output chart file path')
    parser.add_argument('--start', help='Start date (format: YYYY-MM-DD or DD-MM-YYYY)')
    parser.add_argument('--end', help='End date (format: YYYY-MM-DD or DD-MM-YYYY)')
    parser.add_argument('--timeframe', default='daily', help='Timeframe label for title')

    args = parser.parse_args()

    try:
        generate_chart_from_file(
            filepath=args.file,
            emiten=args.emiten,
            output_path=args.output,
            start=args.start,
            end=args.end,
            timeframe=args.timeframe
        )
        print("Chart generated successfully!")
    except Exception as e:
        print(f"Error generating chart: {e}")
        import traceback
        traceback.print_exc()
