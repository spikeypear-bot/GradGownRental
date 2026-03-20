# ── Stage 1: dependency install ──────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /install /usr/local

# The saga has no db/ folder — it is stateless (no database of its own).
# Only copy the source code.
COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

# Port 5003 — matches docker-compose.yml
EXPOSE 5003

WORKDIR /app/src
CMD ["gunicorn", "--bind", "0.0.0.0:5003", "--workers", "2", "--timeout", "120", "app:create_app()"]
