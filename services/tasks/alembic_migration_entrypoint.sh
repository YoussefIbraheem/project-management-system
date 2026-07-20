#!/bin/sh

# * Exit immediately if a command exits with a non-zero status
set -e

# * Run the migrations
echo "Running database migrations..."
alembic upgrade head

# * Start the main application (passed from Docker CMD)
exec "$@"
