from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .db_seeder import seed_db
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Database tables and seed data"""
    
    # Database URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL:
        # Railway PostgreSQL URL use
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    else:
        # For local development
        DB_USER = os.getenv("POSTGRES_USER", "postgres")
        DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
        DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
        DB_PORT = os.getenv("POSTGRES_PORT", "5432")
        DB_NAME = os.getenv("POSTGRES_DB", "library")
        
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Add seed data
        print("Adding seed data...")
        seed_db(db)
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 