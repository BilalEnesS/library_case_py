#!/bin/bash

# Railway build script
echo "Starting Railway build process..."

# Initialize database
echo "Initializing database..."
python -m app.db_init

# Start application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 