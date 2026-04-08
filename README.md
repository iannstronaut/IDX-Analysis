# IDX Technical Analysis Project

Project analisis teknikal saham dengan flow:

1. **Fetch data 3 tahun** dari Yahoo Finance
2. **Hitung semua indikator** (MA20, MA50, RSI, MACD, EMA Cross) untuk seluruh data
3. **Save ke CSV** dengan format: `output/{EMITEN}_past_3_year.csv`
4. **Evaluasi scoring** berdasarkan timeframe (hanya cek periode terakhir)

## Struktur Project

```
analyziz/
├── data/                      # Data scripts (fetch, add_indicators)
│   ├── fetch_data.py
│   └── add_indicators.py
├── indicators/                # Individual indicator scripts
│   ├── ma20.py
│   ├── ma50.py
│   ├── rsi.py
│   ├── macd.py
│   └── ema_cross.py
├── evaluation/                # Evaluation scripts
│   ├── scoring.py
│   └── signal_eval.py
├── utils/                     # Utility functions
│   └── __init__.py
├── output/                    # Output files (auto-created)
│   ├── {EMITEN}_past_3_year.csv
│   ├── {EMITEN}_summary_report.txt
│   ├── {EMITEN}_report_{TIMEFRAME}.csv
│   └── *.csv
├── main.py                    # Orchestrator utama
└── requirements.txt           # Dependencies
```

## Instalasi

```bash
pip install -r requirements.txt
```

## Penggunaan

### Complete Pipeline (Recommended)

```bash
# Analisis harian (evaluasi 20 hari terakhir dari 3 tahun data)
python main.py

# Analisis mingguan (evaluasi 12 minggu terakhir dari 3 tahun data)
python main.py --timeframe weekly

# Analisis bulanan (evaluasi 12 bulan terakhir dari 3 tahun data)
python main.py --timeframe monthly

# Ganti emiten (default: BBCA)
python main.py --emiten BBRI
python main.py --emiten TLKM --timeframe weekly
```

### Step-by-Step

**Step 1: Fetch Data + Add Indicators (3 Years)**

```bash
python data/add_indicators.py

# Atau dengan emiten lain
python data/add_indicators.py --emiten BBRI
```

Output: `output/BBCA_past_3_year.csv` (atau `output/BBRI_past_3_year.csv`)

**Step 2: Run Evaluation Scoring**

```bash
# Evaluasi 20 hari terakhir dari data 3 tahun
python evaluation/scoring.py --timeframe daily

# Evaluasi 12 minggu terakhir
python evaluation/scoring.py --timeframe weekly

# Evaluasi 12 bulan terakhir
python evaluation/scoring.py --timeframe monthly
```

**Step 3: Run Signal Evaluation**

```bash
python evaluation/signal_eval.py
```

## Output Files

| File                                     | Deskripsi                              |
| ---------------------------------------- | -------------------------------------- |
| `output/{EMITEN}_past_3_year.csv`        | Data 3 tahun + semua indikator         |
| `output/{EMITEN}_summary_report.txt`     | Laporan analisis overall (text)        |
| `output/{EMITEN}_report_{TIMEFRAME}.csv` | Data 3 tahun dipotong sesuai timeframe |
| `output/ma20_analysis.csv`               | Hasil MA20 individual                  |
| `output/ma50_analysis.csv`               | Hasil MA50 individual                  |
| `output/rsi_analysis.csv`                | Hasil RSI individual                   |
| `output/macd_analysis.csv`               | Hasil MACD individual                  |
| `output/ema_cross_analysis.csv`          | Hasil EMA Cross individual             |

## Flow Data

```
[Yahoo Finance]
      ↓
[Fetch 3 Years Data]
      ↓
[Calculate All Indicators] → MA20, MA50, RSI, MACD, EMA Cross
      ↓
[Save: output/{EMITEN}_past_3_year.csv]
      ↓
[Generate Summary Report: output/{EMITEN}_summary_report.txt]
      ↓
[Generate Timeframe Report: output/{EMITEN}_report_{TIMEFRAME}.csv]
      ↓
[Evaluation by Timeframe]
      ├── Daily: Cek 20 hari terakhir saja
      ├── Weekly: Cek 12 minggu terakhir saja
      └── Monthly: Cek 12 bulan terakhir saja
```

## Scoring Timeframe

| Timeframe | Periode Evaluasi   | Data Source   | Kegunaan                 |
| --------- | ------------------ | ------------- | ------------------------ |
| Daily     | 20 hari terakhir   | 3 tahun penuh | Trading harian           |
| Weekly    | 12 minggu terakhir | 3 tahun penuh | Swing trading            |
| Monthly   | 12 bulan terakhir  | 3 tahun penuh | Investasi jangka panjang |

**Catatan:** Semua indikator dihitung dari 3 tahun data penuh. Scoring hanya mengevaluasi performa di periode terakhir sesuai timeframe.

## Sinyal Evaluasi

Sinyal candlestick yang dideteksi:

- **Hammer** (bullish reversal)
- **Shooting Star** (bearish reversal)
- **Bullish/Bearish Engulfing**
- **Doji** (indecision)
- **Marubozu** (strong trend)

Output strength: `STRONG_BULLISH` > `BULLISH` > `NEUTRAL` > `BEARISH` > `STRONG_BEARISH`
