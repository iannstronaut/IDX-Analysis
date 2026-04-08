# IDX Technical Analysis Project

> **Disclaimer:** Proyek ini hanya untuk kebutuhan edukasi dan pembelajaran. Bukan sebagai ajakan, rekomendasi, atau saran untuk membeli/menjual saham. Gunakan dengan bijak dan tanggung jawab sendiri.

Technical analysis tool untuk saham Indonesia Stock Exchange (IDX) menggunakan data dari Yahoo Finance.

## Daftar Isi

- [Fitur](#fitur)
- [Struktur Project](#struktur-project)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
  - [Opsi 1: CLI (Recommended)](#opsi-1-cli-recommended-untuk-pengguna)
  - [Opsi 2: Main.py (Simple)](#opsi-2-mainpy-simple)
  - [Opsi 3: Step-by-Step (Advanced)](#opsi-3-step-by-step-advanceddeveloper)
- [Output Files](#output-files)
- [Workflow](#workflow)
- [Konfigurasi Scoring (Editable)](#konfigurasi-scoring-editable)
- [Scoring Timeframe](#scoring-timeframe)
- [Candlestick Patterns](#candlestick-patterns)
- [Signal Strength](#signal-strength)
- [Disclaimer Penting](#disclaimer-penting)
- [Thanks To](#thanks-to)

## Fitur

- **Data Fetching:** Ambil data historis 3 tahun dari Yahoo Finance
- **Technical Indicators:** MA20, MA50, RSI, MACD, EMA Cross
- **Candlestick Patterns:** Deteksi Hammer, Engulfing, Doji, Marubozu, dll
- **Signal Evaluation:** Evaluasi sinyal bullish/bearish dengan trend analysis
- **Timeframe Scoring:** Scoring berdasarkan Daily (20 hari), Weekly (12 minggu), Monthly (12 bulan)

## Struktur Project

```
analyziz/
├── config/
│   ├── __init__.py            # Config module interface
│   └── scoring_config.py      # Konfigurasi scoring (editable)
├── data/
│   ├── fetch_data.py          # Download data dari Yahoo Finance
│   └── add_indicators.py      # Hitung semua indikator teknikal
├── indicators/
│   ├── ma20.py                # Moving Average 20
│   ├── ma50.py                # Moving Average 50
│   ├── rsi.py                 # Relative Strength Index
│   ├── macd.py                # MACD Indicator
│   └── ema_cross.py           # EMA 12/26 Crossover
├── evaluation/
│   ├── scoring.py             # Scoring berdasarkan timeframe
│   └── signal_eval.py         # Evaluasi candlestick patterns
├── utils/
│   └── __init__.py            # Utility functions
├── output/                    # Folder output (auto-generated)
├── main.py                    # Orchestrator utama (simple)
├── cli.py                     # Command Line Interface (advanced)
├── requirements.txt
└── .gitignore
```

## Instalasi

```bash
pip install -r requirements.txt
```

## Cara Penggunaan

### Opsi 1: CLI (Recommended untuk Pengguna)

Gunakan `cli.py` untuk interface yang lebih user-friendly dengan menu interaktif:

```bash
# Lihat semua commands
python cli.py --help

# Interactive wizard mode (paling mudah)
python cli.py interactive

# Fetch data saja
python cli.py fetch --emiten BBCA

# Analisis lengkap
python cli.py analyze --emiten BBRI --timeframe weekly

# Scoring only
python cli.py score --emiten TLKM --timeframe daily

# Signal evaluation only
python cli.py signal --emiten BBCA

# View configuration
python cli.py config view

# Generate reports dari data existing
python cli.py report --emiten BBCA --timeframe daily
```

### Opsi 2: Main.py (Simple)

Untuk penggunaan cepat tanpa interaksi:

```bash
# Analisis harian - evaluasi 20 hari terakhir dari 3 tahun data
python main.py

# Analisis mingguan - evaluasi 12 minggu terakhir
python main.py --timeframe weekly

# Analisis bulanan - evaluasi 12 bulan terakhir
python main.py --timeframe monthly

# Ganti emiten (default: BBCA)
python main.py --emiten BBRI
python main.py --emiten TLKM --timeframe weekly
```

### Opsi 3: Step-by-Step (Advanced/Developer)

Untuk kontrol penuh per module:

**Step 1: Fetch Data + Hitung Indikator**

```bash
python data/add_indicators.py --emiten BBCA
```

Output: `output/BBCA_past_3_year.csv`

**Step 2: Run Evaluation Scoring**

```bash
python evaluation/scoring.py --emiten BBCA --timeframe daily
```

**Step 3: Run Signal Evaluation**

```bash
python evaluation/signal_eval.py --emiten BBCA
```

## Output Files

| File | Deskripsi |
|------|-----------|
| `output/{EMITEN}_past_3_year.csv` | Data 3 tahun + semua indikator |
| `output/{EMITEN}_summary_report.txt` | Laporan analisis keseluruhan |
| `output/{EMITEN}_report_{TIMEFRAME}.csv` | Data 3 tahun dipotong sesuai timeframe |
| `output/*_analysis.csv` | Hasil individual per indikator |

## Workflow

```
[Yahoo Finance]
      ↓
[Fetch 3 Tahun Data]
      ↓
[Hitung Indikator: MA20, MA50, RSI, MACD, EMA Cross]
      ↓
[Save: output/{EMITEN}_past_3_year.csv]
      ↓
[Generate Reports]
      ├── Summary Report (TXT)
      ├── Timeframe Report (CSV)
      └── Individual Analysis (CSV)
```

## Konfigurasi Scoring (Editable)

Semua parameter scoring dapat diubah di `config/scoring_config.py` tanpa mengubah kode utama.

### Konfigurasi yang Tersedia

**1. Time Frames** (`TIME_FRAMES`)
```python
'daily': 20,      # 20 hari untuk evaluasi harian
'weekly': 12,     # 12 minggu untuk evaluasi mingguan
'monthly': 12,    # 12 bulan untuk evaluasi bulanan
```

**2. Threshold Scoring** (`*_THRESHOLDS`)
- `MA_THRESHOLDS` - Threshold untuk MA20/MA50
- `RSI_THRESHOLDS` - Threshold overbought/oversold RSI
- `MACD_THRESHOLDS` - Threshold bullish/bearish MACD
- `EMA_CROSS_THRESHOLDS` - Threshold golden/death cross

**3. Pattern Detection** (`*_CONFIG`)
- `HAMMER_CONFIG` - Parameter deteksi hammer pattern
- `SHOOTING_STAR_CONFIG` - Parameter deteksi shooting star
- `DOJI_CONFIG` - Parameter deteksi doji
- `MARUBOZU_CONFIG` - Parameter deteksi marubozu

**4. Recommendation Rules** (`RECOMMENDATION_THRESHOLDS`)
Atur aturan STRONG_BUY, BUY, SELL, STRONG_SELL, HOLD

**5. Signal Weights** (`SIGNAL_*_WEIGHTS`)
Atur bobot perhitungan sinyal candlestick

### Cara Mengubah Konfigurasi

1. Buka `config/scoring_config.py`
2. Edit nilai yang diinginkan (contoh: ubah RSI overbought dari 70 ke 75)
3. Save file
4. Jalankan ulang analysis - perubahan otomatis diterapkan

### Print Konfigurasi Saat Ini

```bash
python config/scoring_config.py
```

## Scoring Timeframe

| Timeframe | Periode Evaluasi | Kegunaan |
|-----------|-----------------|----------|
| Daily | 20 hari terakhir | Trading harian |
| Weekly | 12 minggu terakhir | Swing trading |
| Monthly | 12 bulan terakhir | Investasi jangka panjang |

## Candlestick Patterns

Patterns yang dideteksi:
- **Hammer** - Sinyal bullish reversal
- **Shooting Star** - Sinyal bearish reversal
- **Bullish/Bearish Engulfing** - Reversal pattern
- **Doji** - Indecision/konsolidasi
- **Marubozu** - Trend kuat

## Signal Strength

```
STRONG_BULLISH > BULLISH > NEUTRAL > BEARISH > STRONG_BEARISH
```

## Disclaimer Penting

**PROYEK INI HANYA UNTUK EDUKASI**

1. **Bukan Financial Advice** - Analisis dan sinyal yang dihasilkan bukan rekomendasi jual/beli
2. **Hasil Prediktif (Potensial)** - Semua analisis teknikal dan sinyal yang dihasilkan bersifat **prediktif/potensial** dan **tidak 100% pasti**. Pasar saham dipengaruhi oleh banyak faktor yang tidak dapat diprediksi dengan pasti
3. **Risiko Trading** - Trading saham memiliki risiko tinggi. Performa masa lalu tidak menjamin hasil masa depan
4. **Tanggung Jawab Sendiri** - Selalu lakukan riset sendiri dan konsultasi dengan advisor keuangan berlisensi
5. **Bukan Jaminan Profit** - Author tidak bertanggung jawab atas kerugian apapun
6. **Yahoo Finance Terms of Service** - Aplikasi ini menggunakan library yfinance. Pengguna diharapkan mematuhi Terms of Service Yahoo Finance. Pengembang tidak bertanggung jawab atas penggunaan data di luar tujuan edukasi

**Gunakan dengan bijak dan trade at your own risk!**

---

## Thanks To

Project ini menggunakan library open-source berikut:

| Library | Deskripsi | Link |
|---------|-----------|------|
| **yfinance** | Fetch data saham dari Yahoo Finance | [github.com/ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) |
| **pandas** | Data manipulation and analysis | [pandas.pydata.org](https://pandas.pydata.org/) |
| **numpy** | Numerical computing | [numpy.org](https://numpy.org/) |

Terima kasih kepada semua kontributor library di atas yang telah membuat project ini mungkin!

---

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
