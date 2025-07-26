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

# --- Süresi Geçmiş Kitaplar ---
def get_overdue_books(db: Session):
    """Süresi geçmiş kitapları getirir."""
    today = date.today()
    return db.query(models.Book).filter(
        models.Book.due_date < today,
        models.Book.patron_id.isnot(None)
    ).all()

# --- Email Log CRUD İşlemleri ---
def create_email_log(db: Session, email_log: models.EmailLogCreate):
    """Email gönderim kaydı oluşturur."""
    db_email_log = models.EmailLog(**email_log.dict())
    db.add(db_email_log)
    db.commit()
    db.refresh(db_email_log)
    return db_email_log

def get_email_logs(db: Session, skip: int = 0, limit: int = 100):
    """Email gönderim kayıtlarını getirir."""
    return db.query(models.EmailLog).order_by(models.EmailLog.sent_at.desc()).offset(skip).limit(limit).all()

def get_email_logs_by_type(db: Session, email_type: str, skip: int = 0, limit: int = 100):
    """Belirli tipteki email kayıtlarını getirir."""
    return db.query(models.EmailLog).filter(
        models.EmailLog.email_type == email_type
    ).order_by(models.EmailLog.sent_at.desc()).offset(skip).limit(limit).all()

def update_email_log_status(db: Session, email_id: int, status: str):
    """Email log durumunu günceller."""
    db_email_log = db.query(models.EmailLog).filter(models.EmailLog.id == email_id).first()
    if db_email_log:
        db_email_log.status = status
        db.commit()
        db.refresh(db_email_log)
    return db_email_log

# --- Notification (Bildirim) CRUD ---
def create_notification(db: Session, notification: models.NotificationCreate):
    db_notification = models.Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_for_patron(db: Session, patron_id: int, only_unread: bool = False):
    q = db.query(models.Notification).filter(models.Notification.patron_id == patron_id)
    if only_unread:
        q = q.filter(models.Notification.is_read == False)
    return q.order_by(models.Notification.created_at.desc()).all()

def mark_notification_as_read(db: Session, notification_id: int):
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif