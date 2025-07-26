from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from .database import Base

# --- SQLAlchemy DB Modelleri ---

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"), nullable=True)
    due_date = Column(Date, nullable=True)

    patron = relationship("Patron", back_populates="checked_out_books")

class Patron(Base):
    __tablename__ = "patrons"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    checked_out_books = relationship("Book", back_populates="patron")

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("patrons.id"), nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="sent")  # sent, failed, pending
    email_type = Column(String, nullable=False)  # overdue_reminder, weekly_report, etc.

    recipient = relationship("Patron")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    patron = relationship("Patron")

# --- Pydantic API Modelleri ---

class BookBase(BaseModel):
    title: str
    author: str

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    patron_id: Optional[int] = None
    due_date: Optional[date] = None
    class Config:
        from_attributes = True

class PatronBase(BaseModel):
    username: str

class PatronCreate(PatronBase):
    password: str

class PatronLogin(PatronBase):
    password: str

class PatronResponse(PatronBase):
    id: int
    class Config:
        from_attributes = True

class EmailLogBase(BaseModel):
    recipient_id: int
    subject: str
    message: str
    email_type: str

class EmailLogCreate(EmailLogBase):
    pass

class EmailLogResponse(EmailLogBase):
    id: int
    sent_at: datetime
    status: str
    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    patron_id: int
    message: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime
    is_read: bool
    class Config:
        from_attributes = True