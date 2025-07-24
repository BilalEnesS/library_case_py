from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# .env dosyasından bu bilgileri okuyacak şekilde de yapılandırılabilir.
# Şimdilik basit tutuyoruz.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@db/kutuphane_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı oturumu almak için bir dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()