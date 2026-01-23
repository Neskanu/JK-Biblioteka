"""
FILE: src/services/inventory_service.py
PURPOSE: Valdo knygų fondą su SQL palaikymu.
RELATIONSHIPS:
  - Kviečia BookRepository metodus (add, update, remove).
CONTEXT:
  - Perrašytas, kad nenaudotų failų perrašymo logikos.
"""
from datetime import datetime
from src.models import Book

class InventoryService:
    def __init__(self, book_repository):
        self.repo = book_repository

    def add_book(self, title, author, year, genre):
        """
        Prideda knygą arba atnaujina esamą (SQL UPDATE/INSERT).
        """
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError(f"Klaida: Metai turi būti skaičius, gauta: {year}")

        # Validacija
        current_year = datetime.now().year
        if year_int > current_year + 1 or year_int < -1000:
            raise ValueError(f"Klaida: Netinkami metai {year_int}.")

        # 1. Tikriname DB
        existing_book = self.repo.find_by_details(title, author)
        
        if existing_book:
            # 2. Atnaujiname (UPDATE)
            existing_book.total_copies += 1
            existing_book.available_copies += 1
            # Čia esminis skirtumas: kviečiame update(), o ne save()
            self.repo.update(existing_book)
            print("DEBUG: Atnaujinta esama knyga (SQL).")
            return existing_book
        
        # 3. Kuriame naują (INSERT)
        new_book = Book(title=title, author=author, year=year_int, genre=genre)
        # BookRepository.add atlieka INSERT
        self.repo.add(new_book)
        print("DEBUG: Įterpta nauja knyga (SQL).")
        return new_book

    def batch_delete(self, book_ids):
        """
        Masinis knygų šalinimas.
        """
        deleted_count = 0
        for bid in book_ids:
            # Kviečiame repo.remove, kuris iškart vykdo DELETE FROM
            if self.repo.remove(bid):
                deleted_count += 1
        
        return deleted_count