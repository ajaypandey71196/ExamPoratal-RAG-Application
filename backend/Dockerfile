# syntax=docker/dockerfile:1

# ============================================================
# Stage 1: Builder
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps needed only to BUILD python packages (psycopg2, etc.)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Install PyTorch CPU-only build FIRST, and separately ---
# This is the single biggest win: the default `pip install torch`
# pulls the CUDA build (2-4 GB). This app only ever runs
# embeddings on CPU (see embeddings.py), so we force the small
# CPU-only wheel (~200 MB) from PyTorch's own CPU index.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
    torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install the rest of the Python dependencies.
# Kept as a separate layer + cache mount so Docker only re-downloads
# when requirements.txt actually changes.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: Final runtime image
# ============================================================
# IMPORTANT: same Debian base ("bookworm", via python:3.11-slim) as the
# builder stage. The previous image mixed slim (bookworm) in the builder
# with slim-buster (EOL, different glibc) in the final stage, which is an
# unsafe combination for copying compiled C-extension wheels across.
FROM python:3.11-slim AS final

WORKDIR /app

# Runtime-only system deps
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the installed packages + alembic binary from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

# Copy application code
COPY . .

ENV PYTHONPATH=/app

# Run migrations and start the server
CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
