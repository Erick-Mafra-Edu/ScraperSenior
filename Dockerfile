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
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    python -m playwright install chromium

# Copy application code
COPY src/ /app/src/
COPY docs_indexacao.jsonl /app/
COPY docs_metadata.json /app/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port (opcional para API futura)
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7700/health || exit 1

# Default: Python shell (pode ser sobrescrito)
CMD ["python", "-i", "-c", "print('\\n📚 Senior Docs Scraper - Shell\\nUse: from src.scraper_unificado import SeniorDocScraper\\n')"]
