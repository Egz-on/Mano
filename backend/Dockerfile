FROM python:3.14.2-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src \
    UV_SYSTEM_PYTHON=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock* ./

# Copy source code (needed for uv sync)
COPY src ./src

# Install dependencies and the project
# Use --frozen only if lock file exists, otherwise let uv generate it
RUN if [ -f uv.lock ]; then uv sync --frozen --no-dev; else uv sync --no-dev; fi

# Copy application code
COPY . .

# Create non-root user and set permissions
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "mano.main:app", "--host", "0.0.0.0", "--port", "8000"]
