FROM mcr.microsoft.com/playwright:v1.57.0-jammy

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    SCRAPER_MODE=legacy

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY apps/ /app/apps/
COPY libs/ /app/libs/
COPY scripts/ /app/scripts/
COPY infra/docker/docker_entrypoint_workers.py /app/docker_entrypoint.py

# Copy configuration
COPY apps/scraper/config/ /app/apps/scraper/config/

WORKDIR /app
# Copy other necessary files
COPY *.py /app/

# Set PYTHONPATH para incluir /app
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8001/health || exit 1

# Entrypoint with multi-worker support
ENTRYPOINT ["python3", "docker_entrypoint.py"]

# Default command (can be overridden via docker-compose)
CMD [""]