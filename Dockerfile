# VIBECODER-SECURE MCP - Production Docker Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r vibecoder && useradd -r -g vibecoder vibecoder
RUN chown -R vibecoder:vibecoder /app
USER vibecoder

# Create necessary directories
RUN mkdir -p /app/.goldminer/backups \
    && mkdir -p /app/docs \
    && mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV VIBECODER_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command - run FastAPI server
CMD ["python", "main.py", "server", "--host", "0.0.0.0", "--port", "8000"]