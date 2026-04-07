# ── Stage 1: dependency install ──────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /install /usr/local

# Application source
COPY src/ ./src/

# Migration runner + SQL migration files
COPY migrate.py ./migrate.py
COPY db/migrations/ ./db/migrations/

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 5001

# gunicorn must run from src/ so it can find app.py
WORKDIR /app/src

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
