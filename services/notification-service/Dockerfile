# ── Stage 1: dependency install ──────────────────────────────────────────────
# Use the official slim Python image matching your .python-version (3.13)
FROM python:3.13-slim AS builder

WORKDIR /app

# Copy only the dependency manifest first.
# Docker caches this layer — if requirements.txt hasn't changed,
# pip install is skipped entirely on rebuilds. Big time saver.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from the builder stage (keeps the final image small)
COPY --from=builder /install /usr/local

# Copy application source code
COPY src/ ./src/

# Tell Python not to buffer stdout/stderr —
# without this, your print() and logger output won't appear in docker compose logs
ENV PYTHONUNBUFFERED=1

# The port this service listens on (matches docker-compose.yml ports mapping)
EXPOSE 5001

# gunicorn is the production WSGI server.
# --workers 2     → 2 worker processes (fine for a mostly I/O-bound service)
# --timeout 120   → workers killed if they don't respond in 120s
# app:create_app() → calls the create_app() factory in src/app.py
WORKDIR /app/src
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "app:create_app()"]
