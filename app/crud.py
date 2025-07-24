from sqlalchemy.orm import Session
from . import models
from datetime import date, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- Patron CRUD İşlemleri ---
def create_patron(db: Session, patron: models.PatronCreate):
    hashed_password = get_password_hash(patron.password)
    db_patron = models.Patron(username=patron.username, hashed_password=hashed_password)
    db.add(db_patron)
    db.commit()
    db.refresh(db_patron)
    return db_patron

def get_patron_by_username(db: Session, username: str):
    return db.query(models.Patron).filter(models.Patron.username == username).first()

def get_patron(db: Session, patron_id: int):
    return db.query(models.Patron).filter(models.Patron.id == patron_id).first()

def get_patrons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patron).offset(skip).limit(limit).all()

# --- Kitap CRUD İşlemleri ---
def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def create_book(db: Session, book: models.BookCreate):
    db_book = models.Book(title=book.title, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# --- Kütüphane Operasyonları ---
def checkout_book(db: Session, book_id: int, patron_id: int):
    db_book = get_book(db, book_id)
    if not db_book or db_book.patron_id is not None:
        return None  # Kitap yok veya zaten alınmış
    db_book.patron_id = patron_id
    db_book.due_date = date.today() + timedelta(days=14)
    db.commit()
    db.refresh(db_book)
    return db_book

def return_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if not db_book or db_book.patron_id is None:
        return None  # Kitap yok veya ödünç alınmamış
    db_book.patron_id = None
    db_book.due_date = None
    db.commit()
    db.refresh(db_book)
    return db_book