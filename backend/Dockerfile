# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Use a volume for pip cache to persist downloads across builds
# This line is a conceptual addition, actual Dockerfile won't directly manage host volumes.
# The effective solution is to rely on Docker's build cache or external dependency caching.

# Copy requirements and install Python dependencies
COPY requirements.txt .
# Use a separate layer for pip install to leverage Docker layer caching
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-dev --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim-buster

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only runtime dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

# Copy application code
COPY . .

# Ensure alembic can find its config
ENV PYTHONPATH=/app

# Run migrations and start the server
CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
