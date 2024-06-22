#!/bin/sh

set -e

# Wait for the database to be ready
./wait-for-it.sh db:5432 --timeout=30 --strict -- echo "PostgreSQL is up and running"

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Start the Django development server
exec python manage.py runserver 0.0.0.0:8000
