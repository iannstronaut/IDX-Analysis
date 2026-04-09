"""
Chart Generation Module
Generates professional stock charts with indicators using mplfinance.
Styling inspired by Stockbit - modern, clean, and professional.
"""

import pandas as pd
import mplfinance as mpf
from pathlib import Path
import sys

sys.path.append("..")
from utils import load_stock_data


def resample_to_weekly(df):
    """
    Resample daily data to weekly and recalculate basic indicators.

    Parameters:
    -----------
    df : pd.DataFrame
        Daily stock data

    Returns:
    --------
    pd.DataFrame : Weekly resampled data with indicators
    """
    df = df.copy()
    if "Date" in df.columns:
        df.set_index("Date", inplace=True)

    # Resample OHLCV
    weekly = (
        df.resample("W")
        .agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )
        .dropna()
    )

    # Recalculate indicators for weekly data
    weekly["MA20"] = weekly["Close"].rolling(window=4).mean()  # 4 weeks ≈ 1 month
    weekly["MA50"] = weekly["Close"].rolling(window=12).mean()  # 12 weeks ≈ 3 months

    # EMA
    weekly["EMA12"] = weekly["Close"].ewm(span=4, adjust=False).mean()
    weekly["EMA26"] = weekly["Close"].ewm(span=8, adjust=False).mean()

    # MACD (using weekly periods)
    ema_fast = weekly["Close"].ewm(span=6, adjust=False).mean()
    ema_slow = weekly["Close"].ewm(span=13, adjust=False).mean()
    weekly["MACD_Line"] = ema_fast - ema_slow
    weekly["MACD_Signal"] = weekly["MACD_Line"].ewm(span=4, adjust=False).mean()
    weekly["MACD_Histogram"] = weekly["MACD_Line"] - weekly["MACD_Signal"]

    # RSI calculation for weekly data (14-week period)
    delta = weekly["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    weekly["RSI"] = 100 - (100 / (1 + rs))

    return weekly


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
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)

    # Rename columns to mplfinance standard (if not already)
    column_mapping = {
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Volume": "Volume",
    }

    # Ensure proper column names exist
    for std_name, req_name in column_mapping.items():
        if std_name not in df.columns and std_name.lower() in df.columns:
            df.rename(columns={std_name.lower(): std_name}, inplace=True)

    return df


def create_stockbit_style():
    """
    Create modern dark theme style for charts.
    Returns mplfinance style configuration.
    """
    # Market colors
    mc = mpf.make_marketcolors(
        up="#00C853",  # Bright green for bullish
        down="#FF3D00",  # Bright red for bearish
        edge="inherit",
        wick="inherit",
        volume="in",
        inherit=True,
    )

    # Create the style with new dark background colors
    # Background luar: #121212
    # Background chart: #1a1a1a
    s = mpf.make_mpf_style(
        marketcolors=mc,
        figcolor="#121212",  # Background luar (outer)
        facecolor="#1a1a1a",  # Background chart (panel)
        edgecolor="#404040",  # Border color
        gridcolor="#404040",  # Grid lines
        gridstyle="-",
        rc={
            "axes.labelcolor": "#FFFFFF",
            "axes.edgecolor": "#404040",
            "axes.linewidth": 1.5,
            "axes.titlecolor": "#FFFFFF",
            "text.color": "#FFFFFF",
            "xtick.color": "#FFFFFF",
            "ytick.color": "#FFFFFF",
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "font.size": 10,
            "font.family": "sans-serif",
            "axes.grid": True,
            "grid.alpha": 0.3,
        },
    )

    return s, mc


def save_chart_with_padding(
    fig, output_path, padding_color="#121212", top_padding=20, bottom_padding=20
):
    """Save chart with top and bottom padding."""
    import matplotlib.pyplot as plt
    from PIL import Image
    import io

    # Save to buffer
    buf = io.BytesIO()
    fig.savefig(
        buf,
        dpi=150,
        facecolor=padding_color,
        edgecolor="none",
        bbox_inches="tight",
        pad_inches=0.1,
    )
    buf.seek(0)

    # Open with PIL
    img = Image.open(buf)

    # Add padding
    from PIL import ImageOps

    img = ImageOps.expand(
        img, border=(0, top_padding, 0, bottom_padding), fill=padding_color
    )

    # Save final
    img.save(output_path)
    buf.close()
    plt.close(fig)

    return output_path


def generate_individual_charts(
    df, emiten="STOCK", timeframe="daily", output_dir="output", start=None, end=None
):
    """
    Generate individual chart components separately.

    Returns:
    --------
    dict : Paths to individual chart images
    """
    from data.fetch_data import parse_date
    from config.scoring_config import TIME_FRAMES
    import matplotlib.pyplot as plt
    from PIL import Image
    import io

    # Prepare data
    df = prepare_data(df)

    # Handle timezone - convert to naive datetime for comparison
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Determine candle type and periods based on timeframe
    candle_type = "daily" if timeframe in ["daily", "weekly"] else "weekly"

    # Resample to weekly if monthly timeframe
    if candle_type == "weekly":
        print(f"Resampling data to weekly candles for monthly timeframe...")
        df = resample_to_weekly(df)

    # Determine number of periods to display
    if start or end:
        display_periods = None
    else:
        # Calculate periods based on timeframe
        if timeframe == "daily":
            display_periods = TIME_FRAMES.get(timeframe, 20)
        elif timeframe == "weekly":
            display_periods = TIME_FRAMES.get(timeframe, 12) * 5
        else:  # monthly
            display_periods = TIME_FRAMES.get(timeframe, 12) * 4
        display_periods = min(display_periods, 120)

    # Filter by date range if provided
    if start:
        start_date = parse_date(start)
        df = df[df.index >= start_date]
    if end:
        end_date = parse_date(end)
        df = df[df.index <= end_date]

    # If no date range but periods specified, take last N periods
    if not start and not end and display_periods:
        df = df.tail(display_periods)

    if len(df) == 0:
        raise ValueError("No data available for the specified date range")

    print(
        f"Chart data: {len(df)} periods ({df.index.min().date()} to {df.index.max().date()})"
    )

    style, mc = create_stockbit_style()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    chart_files = {}

    # 1. Main Chart (Price + Indicators)
    print("Generating main chart...")
    addplots_main = []

    if "MA20" in df.columns:
        addplots_main.append(
            mpf.make_addplot(df["MA20"], color="#00BCD4", width=1.2, label="MA20")
        )
    if "MA50" in df.columns:
        addplots_main.append(
            mpf.make_addplot(df["MA50"], color="#FF9800", width=1.2, label="MA50")
        )
    if "EMA12" in df.columns:
        addplots_main.append(
            mpf.make_addplot(
                df["EMA12"], color="#E040FB", width=1.0, linestyle="--", label="EMA12"
            )
        )
    if "EMA26" in df.columns:
        addplots_main.append(
            mpf.make_addplot(
                df["EMA26"], color="#FFEB3B", width=1.0, linestyle="--", label="EMA26"
            )
        )

    fig, axes = mpf.plot(
        df,
        type="candle",
        style=style,
        title=f"{emiten.upper()}.JK - {timeframe.upper()}",
        ylabel="Price (IDR)",
        addplot=addplots_main,
        figsize=(14, 8),
        returnfig=True,
        tight_layout=True,
    )

    # Add legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], color="#00BCD4", lw=1.2, label="MA20"),
        Line2D([0], [0], color="#FF9800", lw=1.2, label="MA50"),
        Line2D([0], [0], color="#E040FB", lw=1.0, linestyle="--", label="EMA12"),
        Line2D([0], [0], color="#FFEB3B", lw=1.0, linestyle="--", label="EMA26"),
    ]
    axes[0].legend(
        handles=legend_elements,
        loc="upper left",
        facecolor="#121212",
        edgecolor="#404040",
        labelcolor="#FFFFFF",
    )

    main_path = f"{output_dir}/{emiten}_chart_main.png"
    # Save with minimal horizontal padding
    fig.savefig(
        main_path, dpi=150, facecolor="#121212", bbox_inches="tight", pad_inches=0
    )
    plt.close(fig)

    # Add vertical padding only
    from PIL import Image, ImageOps

    img = Image.open(main_path)
    img = ImageOps.expand(img, border=(0, 10, 0, 15), fill="#121212")
    img.save(main_path)

    chart_files["main"] = main_path

    # 2. MACD Chart
    print("Generating MACD chart...")
    if "MACD_Line" in df.columns and "MACD_Signal" in df.columns:
        fig, ax = plt.subplots(figsize=(14, 3), facecolor="#121212")

        x = range(len(df))

        # Zero line
        ax.axhline(y=0, color="#7F8C8D", linewidth=0.8, alpha=0.5)

        # Histogram
        if "MACD_Histogram" in df.columns:
            colors = ["#00C853" if v >= 0 else "#FF3D00" for v in df["MACD_Histogram"]]
            ax.bar(x, df["MACD_Histogram"], color=colors, alpha=0.7, width=0.6)

        # MACD Line and Signal
        ax.plot(x, df["MACD_Line"], color="#00E5FF", linewidth=1.5, label="MACD")
        ax.plot(x, df["MACD_Signal"], color="#FF4081", linewidth=1.5, label="Signal")

        # Styling
        ax.set_facecolor("#1a1a1a")
        ax.set_ylabel("MACD", color="#FFFFFF", fontsize=10)
        ax.tick_params(colors="#FFFFFF")
        ax.grid(True, alpha=0.3, color="#404040")
        ax.spines["bottom"].set_color("#404040")
        ax.spines["top"].set_color("#404040")
        ax.spines["left"].set_color("#404040")
        ax.spines["right"].set_color("#404040")
        ax.legend(
            loc="upper left",
            facecolor="#121212",
            edgecolor="#404040",
            labelcolor="#FFFFFF",
        )

        # X ticks
        ax.set_xticks(range(0, len(df), len(df) // 5))
        ax.set_xticklabels(
            [df.index[i].strftime("%b %d") for i in range(0, len(df), len(df) // 5)],
            rotation=45,
            ha="right",
            color="#FFFFFF",
        )

        macd_path = f"{output_dir}/{emiten}_chart_macd.png"
        fig.savefig(
            macd_path, dpi=150, facecolor="#121212", bbox_inches="tight", pad_inches=0
        )
        plt.close(fig)

        # Add vertical padding only (top, bottom)
        from PIL import Image, ImageOps

        img = Image.open(macd_path)
        img = ImageOps.expand(img, border=(0, 10, 0, 10), fill="#121212")
        img.save(macd_path)

        chart_files["macd"] = macd_path

    # 3. RSI Chart
    print("Generating RSI chart...")
    if "RSI" in df.columns:
        fig, ax = plt.subplots(figsize=(14, 2.5), facecolor="#121212")

        x = range(len(df))

        # Reference lines
        ax.axhline(
            y=70,
            color="#FF3D00",
            linewidth=0.8,
            linestyle="--",
            alpha=0.7,
            label="Overbought (70)",
        )
        ax.axhline(
            y=30,
            color="#00C853",
            linewidth=0.8,
            linestyle="--",
            alpha=0.7,
            label="Oversold (30)",
        )

        # RSI line
        ax.plot(x, df["RSI"], color="#3498DB", linewidth=1.5)

        # Styling
        ax.set_facecolor("#1a1a1a")
        ax.set_ylabel("RSI (0-100)", color="#FFFFFF", fontsize=10)
        ax.set_ylim(0, 100)
        ax.tick_params(colors="#FFFFFF")
        ax.grid(True, alpha=0.3, color="#404040")
        ax.spines["bottom"].set_color("#404040")
        ax.spines["top"].set_color("#404040")
        ax.spines["left"].set_color("#404040")
        ax.spines["right"].set_color("#404040")
        ax.legend(
            loc="upper left",
            facecolor="#121212",
            edgecolor="#404040",
            labelcolor="#FFFFFF",
        )

        # X ticks
        ax.set_xticks(range(0, len(df), len(df) // 5))
        ax.set_xticklabels(
            [df.index[i].strftime("%b %d") for i in range(0, len(df), len(df) // 5)],
            rotation=45,
            ha="right",
            color="#FFFFFF",
        )

        rsi_path = f"{output_dir}/{emiten}_chart_rsi.png"
        fig.savefig(
            rsi_path, dpi=150, facecolor="#121212", bbox_inches="tight", pad_inches=0
        )
        plt.close(fig)

        # Add vertical padding only
        from PIL import Image, ImageOps

        img = Image.open(rsi_path)
        img = ImageOps.expand(img, border=(0, 10, 0, 10), fill="#121212")
        img.save(rsi_path)

        chart_files["rsi"] = rsi_path

    # 4. Volume Chart
    print("Generating Volume chart...")
    fig, ax = plt.subplots(figsize=(14, 2.5), facecolor="#121212")

    x = range(len(df))

    # Plot volume as bar chart
    colors = [
        "#00C853" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#FF3D00"
        for i in range(len(df))
    ]
    ax.bar(x, df["Volume"], color=colors, alpha=0.7, width=0.8)

    # Styling
    ax.set_facecolor("#1a1a1a")
    ax.set_ylabel("Volume", color="#FFFFFF", fontsize=10)
    ax.tick_params(colors="#FFFFFF")
    ax.grid(True, alpha=0.3, color="#404040")
    ax.spines["bottom"].set_color("#404040")
    ax.spines["top"].set_color("#404040")
    ax.spines["left"].set_color("#404040")
    ax.spines["right"].set_color("#404040")

    # X ticks
    ax.set_xticks(range(0, len(df), len(df) // 5))
    ax.set_xticklabels(
        [df.index[i].strftime("%b %d") for i in range(0, len(df), len(df) // 5)],
        rotation=45,
        ha="right",
        color="#FFFFFF",
    )

    volume_path = f"{output_dir}/{emiten}_chart_volume.png"
    fig.savefig(
        volume_path, dpi=150, facecolor="#121212", bbox_inches="tight", pad_inches=0
    )
    plt.close(fig)

    # Add vertical padding only
    from PIL import Image, ImageOps

    img = Image.open(volume_path)
    img = ImageOps.expand(img, border=(0, 10, 0, 10), fill="#121212")
    img.save(volume_path)

    chart_files["volume"] = volume_path

    return chart_files


def combine_charts(chart_files, output_path, gap=15, bg_color="#121212"):
    """
    Combine individual charts into one image with gaps.

    Parameters:
    -----------
    chart_files : dict
        Dictionary of chart paths
    output_path : str
        Output path for combined image
    gap : int
        Gap between charts in pixels
    bg_color : str
        Background color for gaps
    """
    from PIL import Image

    images = []
    for key in ["main", "macd", "rsi", "volume"]:
        if key in chart_files:
            images.append(Image.open(chart_files[key]))

    if not images:
        raise ValueError("No chart images to combine")

    # Get dimensions
    widths = [img.width for img in images]
    heights = [img.height for img in images]

    # Use maximum width and resize all images to same width
    max_width = max(widths)

    # Resize all images to same width if needed
    resized_images = []
    for img in images:
        if img.width != max_width:
            # Resize maintaining aspect ratio
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        resized_images.append(img)

    # Recalculate heights after resize
    heights = [img.height for img in resized_images]
    total_height = sum(heights) + gap * (len(resized_images) - 1)

    # Create new image
    combined = Image.new("RGB", (max_width, total_height), bg_color)

    # Paste images with gaps - align left (no horizontal centering)
    y_offset = 0
    for i, img in enumerate(resized_images):
        # Paste at left edge (x=0), no horizontal offset
        combined.paste(img, (0, y_offset))
        y_offset += img.height

        # Add gap (except after last image)
        if i < len(resized_images) - 1:
            y_offset += gap

    combined.save(output_path)
    print(f"Combined chart saved to: {output_path}")

    # Clean up individual files
    for path in chart_files.values():
        Path(path).unlink(missing_ok=True)

    return output_path


def generate_chart(
    df,
    emiten="STOCK",
    timeframe="daily",
    output_path=None,
    start=None,
    end=None,
    figsize=(14, 14),
    gap=15,
):
    """
    Generate complete chart by creating individual components and combining them.

    Parameters:
    -----------
    df : pd.DataFrame
        Stock data with all indicators
    emiten : str
        Stock ticker
    timeframe : str
        Timeframe label
    output_path : str, optional
        Output path. If None, saves to output/{emiten}_chart.png
    start, end : str, optional
        Date range
    figsize : tuple
        Figure size (width, height) - used for individual charts
    gap : int
        Gap between chart components in pixels

    Returns:
    --------
    str : Path to saved chart
    """
    if output_path is None:
        output_path = f"output/{emiten.upper()}_chart.png"

    # Generate individual charts
    chart_files = generate_individual_charts(
        df,
        emiten=emiten,
        timeframe=timeframe,
        output_dir="output",
        start=start,
        end=end,
    )

    # Combine with gaps
    combine_charts(chart_files, output_path, gap=gap)

    return output_path


def generate_chart_from_file(
    filepath=None, emiten="BBCA", timeframe="daily", start=None, end=None, **kwargs
):
    """
    Generate chart from CSV file.
    """
    if filepath is None:
        filepath = f"output/{emiten.upper()}_past_3_year.csv"

    print(f"Loading data from: {filepath}")
    df = load_stock_data(filepath)
    print(f"Data loaded: {len(df)} rows")

    return generate_chart(
        df, emiten=emiten, timeframe=timeframe, start=start, end=end, **kwargs
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate stock chart with indicators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chart.py --emiten BBCA
  python chart.py --emiten BBRI --start 2025-01-01 --end 2025-12-31
  python chart.py --file output/custom_data.csv --emiten TLKM
        """,
    )

    parser.add_argument("--emiten", default="BBCA", help="Stock ticker (default: BBCA)")
    parser.add_argument("--file", help="Input CSV file path")
    parser.add_argument("--output", help="Output chart file path")
    parser.add_argument("--start", help="Start date (format: YYYY-MM-DD or DD-MM-YYYY)")
    parser.add_argument("--end", help="End date (format: YYYY-MM-DD or DD-MM-YYYY)")
    parser.add_argument(
        "--timeframe",
        default="daily",
        choices=["daily", "weekly", "monthly"],
        help="Timeframe for chart (affects default period display)",
    )
    parser.add_argument(
        "--periods",
        type=int,
        help="Number of periods to display (overrides timeframe default)",
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=15,
        help="Gap between chart panels in pixels (default: 15)",
    )

    args = parser.parse_args()

    try:
        generate_chart_from_file(
            filepath=args.file,
            emiten=args.emiten,
            output_path=args.output,
            start=args.start,
            end=args.end,
            timeframe=args.timeframe,
            gap=args.gap,
        )
        print("Chart generated successfully!")
    except Exception as e:
        print(f"Error generating chart: {e}")
        import traceback

        traceback.print_exc()
