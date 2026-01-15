"""
FILE: src/repositories/book_repository.py
PURPOSE: Valdo operacijas su knygų duomenų failu (books.json).
RELATIONSHIPS:
  - Naudoja src/models.py (Book klasę).
CONTEXT:
  - Atskirtas failas leidžia lengviau valdyti duomenis. Jei ateityje failą pakeistume
    į SQL duomenų bazę, reikėtų keisti TIK šį failą, o ne visą programą.
"""

import os
from src.models import Book
from src.data_manager import load_data, save_data, get_data_file_path
from src.config import BOOKS_FILENAME, BACKUP_FILENAME

class BookRepository:
    def __init__(self):
        # Nustatome kelius iki pagrindinio failo ir backup failo
        self.filepath = get_data_file_path(BOOKS_FILENAME)
        self.backup_path = get_data_file_path(BACKUP_FILENAME)
        self._load()

    def _load(self):
        """Užkrauna knygas iš JSON į atmintį (Book objektų sąrašą)."""
        data = load_data(self.filepath)
        # Kiekvieną įrašą paverčiame Book objektu
        self.books = [Book.from_dict(item) for item in data]

    def save(self):
        """Įrašo dabartinę knygų būklę į failą."""
        data = [book.to_dict() for book in self.books]
        save_data(self.filepath, data)

    # --- Duomenų gavimo metodai ---

    def get_all(self):
        return self.books

    def get_by_id(self, book_id):
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def find_by_details(self, title, author):
        """
        Tikrina, ar knyga egzistuoja (tikslus atitikmuo).
        Naudojama prieš pridedant naują knygą, kad išvengtume dublikatų.
        """
        for book in self.books:
            if book.title.lower() == title.lower() and book.author.lower() == author.lower():
                return book
        return None

    def search(self, query):
        """
        Filtruoja knygas pagal paieškos frazę.
        """
        query = query.lower()
        # Grąžiname naują sąrašą tik su tomis knygomis, kurios atitinka paiešką pagal pavadinimą arba autorių
        return [b for b in self.books if query in b.title.lower() or query in b.author.lower()]

    # --- Modifikavimo metodai ---

    def add(self, book):
        self.books.append(book)
        self.save()

    def remove(self, book):
        if book in self.books:
            self.books.remove(book)
            self.save()
            return True
        return False

    def restore_backup(self):
        """
        Speciali funkcija: atstato duomenis iš atsarginės kopijos.
        """
        if not os.path.exists(self.backup_path):
            return False, "Backup failas nerastas."
        try:
            data = load_data(self.backup_path)
            self.books = [Book.from_dict(item) for item in data]
            self.save() # Iškart perrašome ir pagrindinį failą
            return True, f"Sėkmingai atkurta {len(self.books)} knygų."
        except Exception as e:
            return False, str(e)