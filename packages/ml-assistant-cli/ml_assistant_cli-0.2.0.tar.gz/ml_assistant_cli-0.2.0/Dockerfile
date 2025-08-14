# Multi-stage Docker build for ML Assistant CLI
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY pyproject.toml setup.py MANIFEST.in ./
COPY mlcli/ ./mlcli/
COPY README.md LICENSE ./

# Install the package
RUN pip install --upgrade pip setuptools wheel
RUN pip install .

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN useradd --create-home --shell /bin/bash mlcli
USER mlcli
WORKDIR /home/mlcli

# Create workspace directory
RUN mkdir -p /home/mlcli/workspace
WORKDIR /home/mlcli/workspace

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD mlcli --help || exit 1

# Default command
ENTRYPOINT ["mlcli"]
CMD ["--help"]