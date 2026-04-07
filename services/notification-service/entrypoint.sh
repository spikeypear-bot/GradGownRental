#!/bin/sh
set -e

echo "[entrypoint] running database migrations..."
python3 /app/migrate.py

echo "[entrypoint] starting notification-service..."
exec gunicorn --bind 0.0.0.0:5001 --workers 1 --timeout 120 "app:create_app()"
