# ============================================================================
# AgentOrchestra Backend Dockerfile
# Multi-stage build for Python FastAPI application
# ============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies (system-level)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (layer cached unless requirements change)
COPY backend/pyproject.toml backend/requirements*.txt* ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="AgentOrchestra Team"
LABEL description="AgentOrchestra Backend - Multi-Agent Collaboration System"
LABEL version="1.0.0"

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        tini \
        && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY --chown=appuser:appgroup backend/ .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    FASTAPI_ENV=production

# Expose the application port
EXPOSE 8000

# Health check - verify the API is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Use tini as PID 1 to handle signals properly
ENTRYPOINT ["tini", "--"]

# Start the FastAPI application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log"]
