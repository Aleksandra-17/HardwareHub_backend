#!/bin/sh
set -e

# Ensure alembic.ini exists (volume mount may overwrite /app)
if [ ! -f alembic.ini ]; then
    cp alembic.ini.example alembic.ini
fi

echo "Running database migrations..."
for i in 1 2 3 4 5; do
    if alembic upgrade head; then
        break
    fi
    if [ "$i" -eq 5 ]; then
        echo "Migration failed after 5 attempts"
        exit 1
    fi
    echo "Waiting for database (attempt $i/5), retrying in 3s..."
    sleep 3
done

echo "Starting application..."
exec "$@"
