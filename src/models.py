"""
FILE: src/models.py
PURPOSE: Apibrėžia duomenų bazės lentelių struktūrą (ORM Modeliai).
RELATIONSHIPS:
  - Paveldi iš src/database.py -> Base.
  - Apibrėžia ryšius tarp User, Book ir Loan.
CONTEXT:
  - Pakeista iš paprastų dataclasses į SQLAlchemy modelius.
  - Pridėti Foreign Keys ir Relationships.
"""

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from src.database import Base

def generate_uuid():
    """Generuoja unikalų ID kaip string."""
    return str(uuid.uuid4())

class Book(Base):
    """
    Atstovauja 'books' lentelę.
    """
    __tablename__ = "books"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    year = Column(Integer, nullable=True)
    genre = Column(String(100), nullable=True)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)

    # Ryšys su Loan lentele (vienas-su-daugeliu)
    # cascade="all, delete" reiškia, kad ištrynus knygą, dings ir jos istorija (paskolos)
    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book(title='{self.title}', available={self.available_copies})>"
    
    def to_dict(self):
        """Serializacija UI atvaizdavimui (suderinamumas su senu kodu)."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies
        }


class User(Base):
    """
    Atstovauja 'users' lentelę. 
    Apjungia tiek Reader, tiek Librarian logiką vienoje lentelėje.
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # 'reader' arba 'librarian'
    password = Column(String(255), nullable=True) # Tik bibliotekininkams

    # Ryšys: Vartotojas gali turėti daug paskolų
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    
    # Šis property reikalingas senam kodui, kuris tikisi `active_loans` sąrašo
    @property
    def active_loans(self):
        # Grąžina paskolų sąrašą (objektus)
        return self.loans

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

    def to_dict(self):
        """Suderinamumas su UI."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            # active_loans čia neįtraukiame tiesiogiai, kad neapkrautume JSON, 
            # nebent reikia specifinėse vietose.
        }


class Loan(Base):
    """
    Atstovauja 'loans' lentelę (jungiamoji lentelė).
    Saugo informaciją apie pasiskolinimą.
    """
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    book_id = Column(String(36), ForeignKey("books.id"), nullable=False)
    
    # Denormalizacija: Saugome pavadinimą, kad nereikėtų visada join'inti, 
    # arba paliekame tuščią ir pasitikime 'book' relationship.
    # Senas kodas naudojo 'title', todėl paliekame suderinamumui.
    title = Column(String(255), nullable=True) 
    
    due_date = Column(String(20), nullable=False) # Paprastumo dėlei saugome kaip tekstą YYYY-MM-DD

    # ORM Ryšiai
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")

    def __getitem__(self, key):
        """Leidžia pasiekti atributus kaip žodyną (loan['title']), reikalinga senam UI kodui."""
        return getattr(self, key)