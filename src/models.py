"""
FILE: src/models.py
PURPOSE: Apibrėžia duomenų bazės lentelių struktūrą (ORM Modeliai) ir ryšius.
RELATIONSHIPS:
  - Paveldi iš src/database.py -> Base.
  - Apibrėžia tipizuotus ryšius tarp User, Book ir Loan.
CONTEXT:
  - Naudoja modernią SQLAlchemy 2.0 sintaksę.
  - Pridėtas .get() metodas Loan klasei atgaliniam suderinamumui.
"""

import uuid
import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

def generate_uuid():
    """Generuoja unikalų ID kaip string."""
    return str(uuid.uuid4())

class Book(Base):
    """
    Knygų modelis.
    """
    __tablename__ = "books"

    # SQLAlchemy 2.0 sintaksė
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)

    # NAUJAS LAUKAS: Automatiškai užpildomas įrašo sukūrimo metu
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Ryšys su Loan (naudojant string "Loan", kad išvengtume ciklinės priklausomybės)
    loans: Mapped[List["Loan"]] = relationship(back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book(title='{self.title}', available={self.available_copies})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }

class User(Base):
    """
    Vartotojų modelis.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50)) # 'reader' arba 'librarian'
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    loans: Mapped[List["Loan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    @property
    def active_loans(self) -> List["Loan"]:
        return self.loans

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
        }

class Loan(Base):
    """
    Paskolų modelis (jungiamoji lentelė).
    Svarbu: Ši klasė turi būti faile, kitaip kils ImportError.
    """
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"))
    
    # Denormalizuoti laukai
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[str] = mapped_column(String(20))

    user: Mapped["User"] = relationship(back_populates="loans")
    book: Mapped["Book"] = relationship(back_populates="loans")

    def __getitem__(self, key):
        """Leidžia pasiekti atributus kaip žodyną: loan['title']"""
        return getattr(self, key)
    
    def get(self, key, default=None):
        """
        Leidžia naudoti .get() metodą, lyg tai būtų žodynas.
        Reikalingas senesniam UI kodui, kuris tikisi dict.
        """
        return getattr(self, key, default)