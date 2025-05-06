# Set base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psycopg2-binary

# Copy application files
COPY start_prod.py .
COPY README.md .
COPY secrets.json .
COPY src/ ./src/

# Create necessary directories and files
RUN mkdir -p /app/logs && \
    touch /app/logs/pds_data_api.log && \
    chmod 755 /app/logs/pds_data_api.log

# Create a non-root user
RUN useradd -m -u 1000 pdsapi && \
    chown -R pdsapi:pdsapi /app

# Switch to non-root user
USER pdsapi

# Expose port
EXPOSE 8000

# Set default environment variables
ENV DATABASE_URL=postgresql://pdsapi:pdsapi@db:5432/pds_data_api \
    PDS_HOST=0.0.0.0 \
    PDS_PORT=8000 \
    LOG_LEVEL=WARNING \
    LOG_FILE=/app/logs/pds_data_api.log \
    WORKERS=4

# Command to run the application
CMD ["python", "start_prod.py"] 