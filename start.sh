#!/bin/bash

# Railway startup script
echo "Starting Railway application..."

# Get port from environment variable or use default
PORT=${PORT:-8000}
echo "Using port: $PORT"

# Initialize database
echo "Initializing database..."
python -c "
from app.database import engine
from app.models import Base
from app.db_seeder import seed_db
from app.database import SessionLocal

try:
    Base.metadata.create_all(bind=engine)
    print('Database tables created successfully')
    
    db = SessionLocal()
    seed_db(db)
    print('Database seeded successfully')
    db.close()
except Exception as e:
    print(f'Database initialization error: {e}')
"

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 