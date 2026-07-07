#!/bin/sh
set -e

echo "Waiting for database..."

until uv run python -c "
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect():
    pass
"; do
    sleep 2
done

echo "Running migrations..."
uv run alembic upgrade head

echo "Seeding languages..."
uv run python -m app.seeds.languages

echo "Starting API..."
exec "$@"