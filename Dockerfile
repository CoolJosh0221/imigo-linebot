# FastAPI Backend Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first (for better caching)
COPY pyproject.toml .

# Install Python dependencies directly from pyproject.toml
RUN pip install --no-cache-dir --upgrade pip uv && \
    uv pip install --system -r pyproject.toml

# Copy application code
COPY . .

# Create directory for database
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
