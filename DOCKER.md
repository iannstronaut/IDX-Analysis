# Docker Usage Guide

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start container in interactive mode
docker-compose up -d

# Enter the container
docker-compose exec analyziz sh

# Inside container, run main.py
python main.py --emiten BBCA --chart
python main.py --emiten BBRI --timeframe weekly --chart
python main.py --emiten TLKM --start 2025-01-01 --end 2025-12-31 --chart

# Or run cli.py
python cli.py
python cli.py analyze --emiten BBCA --chart

# Exit container
exit
```

### Using Docker Run

```bash
# Build image
docker build -t analyziz .

# Run interactive shell
docker run -it -v $(pwd)/output:/app/output analyziz

# Inside container
python main.py --emiten BBCA --chart
python cli.py

# Or run one-time command directly
docker run -v $(pwd)/output:/app/output analyziz python main.py --emiten BBCA --chart
```

## Output Files

All output files are saved to the `./output` directory on your host machine:
- `*_past_3_year.csv` - Raw data with indicators
- `*_analysis_*.txt` - Analysis report
- `*_chart.png` - Generated chart image

## Image Size Optimization

The Dockerfile uses multi-stage build with Alpine Linux:
- **Base image**: ~50MB (python:3.11-alpine)
- **Final image**: ~562MB (vs ~1GB+ with standard Python image)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| TZ | Asia/Jakarta | Timezone setting |
| PYTHONUNBUFFERED | 1 | Disable Python output buffering |
| PYTHONPATH | /app | Python module path |

## Volume Mounts

| Container Path | Host Path | Purpose |
|----------------|-----------|---------|
| /app/output | ./output | Analysis output files |
| /tmp/matplotlib | analyziz-cache (named) | Matplotlib font cache |

## Available Scripts

Once inside the container, you can run:

```bash
# Main analysis pipeline
python main.py --emiten BBCA --chart

# Interactive CLI mode
python cli.py

# Chart generation only
python chart.py --emiten BBCA
```
