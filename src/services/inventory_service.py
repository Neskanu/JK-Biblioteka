"""
FILE: src/services/inventory_service.py
PURPOSE: Valdo knygų fondą su SQLAlchemy.
RELATIONSHIPS:
  - Naudoja BookRepository.
  - Importuoja Book modelį.
CONTEXT:
  - Atnaujinta dirbti su ORM objektais.
"""
from datetime import datetime
from src.models import Book
import os
import json
import uuid

class InventoryService:
    def __init__(self, book_repository):
        self.repo = book_repository

    def add_book(self, title, author, year, genre):
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError(f"Klaida: Metai turi būti skaičius, gauta: {year}")

        current_year = datetime.now().year
        if year_int > current_year + 1 or year_int < -1000:
            raise ValueError(f"Klaida: Netinkami metai {year_int}.")

        # Tikriname ar knyga egzistuoja
        existing_book = self.repo.find_by_details(title, author)
        
        if existing_book:
            existing_book.total_copies += 1
            existing_book.available_copies += 1
            self.repo.update(existing_book)
            return existing_book
        
        # Kuriame naują
        new_book = Book(
            title=title, 
            author=author, 
            year=year_int, 
            genre=genre,
            total_copies=1,
            available_copies=1
        )
        self.repo.add(new_book)
        return new_book

    def batch_delete(self, book_ids):
        deleted_count = 0
        for bid in book_ids:
            if self.repo.remove(bid):
                deleted_count += 1
        return deleted_count
    
    def import_books_from_json(self, filepath):
        if not os.path.exists(filepath):
            print(f"DEBUG: JSON failas nerastas: {filepath}")
            return 0

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("Klaida: Nepavyko nuskaityti JSON failo.")
            return 0

        imported_count = 0
        
        for item in data:
            # Jei knyga su tokiu ID jau yra, praleidžiame
            if self.repo.get_by_id(item.get('id')):
                continue

            book = Book(
                id=item.get('id', str(uuid.uuid4())),
                title=item['title'],
                author=item['author'],
                year=int(item['year']),
                genre=item['genre'],
                total_copies=item.get('total_copies', 1),
                available_copies=item.get('available_copies', 1)
            )
            self.repo.add(book)
            imported_count += 1
            
        return imported_count
    
    def get_new_arrivals(self, limit=5)
        """
        Grąžina vėliausiai į biblioteką įtrauktas knygas.
        """
        session = SessionLocal()
        try:
            return session.query(Book).order_by(Book.created_at.desc()).limit(limit).all()
        finally:
            session.close()