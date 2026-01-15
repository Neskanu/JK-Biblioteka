"""
FILE: src/services/inventory_service.py
PURPOSE: Valdo knygų fondą (Inventorių).
RELATIONSHIPS:
  - Bendrauja su BookRepository duomenų keitimui.
CONTEXT:
  - Čia yra taisyklė: "Jei knyga jau yra, nekurk naujos, o padidink kiekį".
    Tai vadinama Verslo Logika (Business Logic).
"""
from src.models import Book

class InventoryService:
    def __init__(self, book_repository):
        self.repo = book_repository

    def add_book(self, title, author, year, genre):
        """
        Prideda knygą į biblioteką.
        Algoritmas:
        1. Patikrinti, ar tokia knyga jau egzistuoja.
        2. Jei taip -> padidinti jos egzempliorių skaičių.
        3. Jei ne -> sukurti naują įrašą.
        """
        existing_book = self.repo.find_by_details(title, author)
        
        if existing_book:
            # Knyga rasta - atnaujiname skaitiklius
            existing_book.total_copies += 1
            existing_book.available_copies += 1
            self.repo.save() # Išsaugome pakeitimą
            return existing_book
        
        # Knyga nerasta - kuriame naują
        new_book = Book(title, author, year, genre, total_copies=1, available_copies=1)
        self.repo.add(new_book)
        return new_book

    def batch_delete(self, books):
        """
        Ištrina visą sąrašą knygų.
        Naudinga masiniam valymui (pvz., senų knygų nurašymui).
        """
        count = 0
        for book in books:
            # repo.remove grąžina True, jei pavyko ištrinti
            if self.repo.remove(book):
                count += 1
        return count