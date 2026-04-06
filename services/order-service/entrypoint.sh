#!/bin/sh
set -e

echo "[entrypoint] running database migrations..."
python3 /app/migrate.py

echo "[entrypoint] starting order-service..."
exec python3 /app/main.py
