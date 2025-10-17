# Lumin Backend - Production Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r lumin && useradd -r -g lumin lumin

# Set work directory
WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy project files
COPY --chown=lumin:lumin . .

# Collect static files (will run in entrypoint)
RUN mkdir -p /app/staticfiles /app/media

# Change to app user
USER lumin

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/admin/')" || exit 1

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "config.wsgi:application"]
