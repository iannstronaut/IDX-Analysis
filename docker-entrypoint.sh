#!/bin/sh
# Docker entrypoint script for analyziz

set -e

# Ensure output directory exists and is writable
mkdir -p /app/output

# Show help if no arguments
if [ $# -eq 0 ]; then
    echo "Analyziz Technical Analysis Tool"
    echo ""
    echo "Usage:"
    echo "  docker run analyziz [main.py options]"
    echo "  docker run --entrypoint python analyziz cli.py [options]"
    echo "  docker run --entrypoint python analyziz chart.py [options]"
    echo ""
    echo "Examples:"
    echo "  docker run analyziz --emiten BBCA --chart"
    echo "  docker run analyziz --emiten BBRI --start 2025-01-01 --chart"
    echo "  docker run --entrypoint python analyziz cli.py analyze --emiten TLKM --chart"
    echo ""
    echo "Output files will be saved to ./output on the host."
    exit 0
fi

# Run the main analysis
exec python main.py "$@"
