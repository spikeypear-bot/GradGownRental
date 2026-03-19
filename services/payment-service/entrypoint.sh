sleep 5

if [ ! -d migrations ] || [ ! -f migrations/alembic.ini ]; then
    echo "Setting up migrations directory..."
    uv run flask db init
fi

exec uv run gunicorn --bind 0.0.0.0:3000 "run:app"

