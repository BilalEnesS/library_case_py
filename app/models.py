from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import date
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