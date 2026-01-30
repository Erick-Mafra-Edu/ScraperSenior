FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    python -m playwright install chromium

# Copy application code
COPY apps/ /app/apps/
COPY libs/ /app/libs/
COPY scripts/ /app/scripts/
COPY infra/docker/docker_entrypoint.py /app/

# Entrypoint: Orquestra tudo
CMD ["python", "docker_entrypoint.py"]
