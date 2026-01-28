"""
FILE: src/repositories/book_repository.py
PURPOSE: Atlieka CRUD operacijas su Knygomis naudojant SQLAlchemy.
RELATIONSHIPS:
  - Naudoja src/database.py sesijos gavimui.
  - Manipuliuoja src/models.py Book objektais.
CONTEXT:
  - Refaktorizuota: Panaikintas 'cache' (sąrašas atmintyje).
  - Duomenys visada švieži iš DB.
"""

from src.database import SessionLocal
from src.models import Book

class BookRepository:
    def __init__(self):
        # Sesija sukuriama kiekvienai užklausai
        pass

    @property
    def books(self):
        """
        Suderinamumo sluoksnis (Shim).
        Senas kodas tikisi, kad repo.books grąžins sąrašą.
        """
        return self.get_all()

    def refresh_cache(self):
        """
        DEPRECATED (Pasenęs metodas).
        Paliktas tik dėl suderinamumo su senu UI kodu.
        SQLAlchemy atveju duomenys visada imami iš DB, todėl cache atnaujinti nereikia.
        """
        pass

    def get_all(self):
        """Grąžina visas knygas iš DB."""
        session = SessionLocal()
        try:
            return session.query(Book).all()
        finally:
            session.close()

    def get_by_id(self, book_id):
        """Suranda knygą pagal ID."""
        session = SessionLocal()
        try:
            return session.query(Book).filter(Book.id == str(book_id)).first()
        finally:
            session.close()

    def find_by_details(self, title, author):
        """Suranda knygą pagal pavadinimą ir autorių."""
        session = SessionLocal()
        try:
            return session.query(Book).filter(
                Book.title == title, 
                Book.author == author
            ).first()
        finally:
            session.close()

    def search(self, query):
        """Paieška DB naudojant LIKE operatorių."""
        session = SessionLocal()
        try:
            search_str = f"%{query}%"
            return session.query(Book).filter(
                (Book.title.like(search_str)) | 
                (Book.author.like(search_str))
            ).all()
        finally:
            session.close()
    
    # Alias senam kodui
    search_books = search 
    get_all_books = get_all

    def add(self, book):
        """Prideda naują knygą į DB."""
        session = SessionLocal()
        try:
            session.add(book)
            session.commit()
            session.refresh(book) # Atnaujina ID ir kitus laukus
            return book
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update(self, book):
        """Atnaujina esamą knygą."""
        session = SessionLocal()
        try:
            session.merge(book)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save(self):
        """
        Suderinamumo metodas.
        SQLAlchemy atveju pakeitimai įrašomi per commit() metodus.
        """
        pass

    def remove(self, book_id):
        """Ištrina knygą pagal ID."""
        session = SessionLocal()
        try:
            book = session.query(Book).filter(Book.id == str(book_id)).first()
            if book:
                session.delete(book)
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()