# Multi-stage build for minimal image size
# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    g++ \
    freetype-dev \
    libpng-dev \
    jpeg-dev \
    zlib-dev \
    make \
    cmake

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Install numpy first (heavy dependency)
RUN pip install --no-cache-dir numpy==2.4.4

# Install other heavy dependencies
RUN pip install --no-cache-dir \
    pandas==3.0.2 \
    matplotlib==3.10.8 \
    pillow==12.2.0 \
    contourpy==1.3.3 \
    fonttools==4.62.1

# Copy and install requirements
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Runtime image
FROM python:3.11-alpine AS runtime

# Install only runtime dependencies (minimal)
RUN apk add --no-cache \
    freetype \
    libpng \
    libstdc++ \
    libgcc \
    tzdata \
    curl

# Set timezone
ENV TZ=Asia/Jakarta

# Create non-root user for security
RUN adduser -D -s /bin/sh appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create output directory and set permissions
RUN mkdir -p /app/output && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MPLCONFIGDIR=/tmp/matplotlib

# Default to shell - user can run main.py manually
CMD ["/bin/sh"]
