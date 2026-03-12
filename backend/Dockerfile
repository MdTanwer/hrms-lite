# Production Dockerfile for HRMS Lite API (MongoDB Atlas)
# Pin base for reproducible builds
FROM python:3.11-slim-bookworm

LABEL maintainer="HRMS Lite"
LABEL description="HRMS Lite API - production"

# Security: non-root user (fixed UID/GID for file permissions)
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/sh --create-home appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT=production

WORKDIR /app

# System deps: only curl for healthcheck, minimal layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Application code last
COPY --chown=appuser:appgroup . .
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f -s http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
