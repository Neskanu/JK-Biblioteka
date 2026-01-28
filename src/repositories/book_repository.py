"""
FILE: src/repositories/book_repository.py
PURPOSE: Valdo knygų duomenis naudojant PyMySQL.
RELATIONSHIPS:
  - Naudoja src/database.py.
  - Konvertuoja SQL eilutes į Book objektus.
CONTEXT:
  - PATAISYTA: get_by_id dabar naudoja cache, kad LoanService galėtų modifikuoti objektus atmintyje.
"""

from src.database import get_connection
from src.models import Book

class BookRepository:
    def __init__(self):
        self.books = []
        # Užkrauname duomenis į atmintį (cache) paleidimo metu
        self.refresh_cache()

    def refresh_cache(self):
        """Sinchronizuoja vietinį sąrašą su duomenų baze."""
        self.books = self.get_all_from_db()

    def get_all(self):
        return self.books

    def get_all_from_db(self):
        """Pagalbinis metodas duomenų traukimui."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books")
                rows = cursor.fetchall()
                # Sukuriame Book objektus iš DB eilučių
                return [Book.from_dict(row) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, book_id):
        """
        SVARBU: Ieškome atmintyje (self.books), o ne DB.
        Tai būtina, nes LoanService modifikuoja gautą objektą tiesiogiai,
        o save() metodas vėliau iteruoja per self.books.
        """
        # Konvertuojame į string, nes kartais gali ateiti int
        search_id = str(book_id).strip()
        for book in self.books:
            if str(book.id) == search_id:
                return book
        return None

    def find_by_details(self, title, author):
        """Ieško tikslaus atitikmens atmintyje."""
        for book in self.books:
            if book.title.lower() == title.lower() and book.author.lower() == author.lower():
                return book
        return None

    def search(self, query):
        """Paieška atmintyje (greičiau ir paprasčiau, kai turime cache)."""
        q = query.lower()
        return [b for b in self.books if q in b.title.lower() or q in b.author.lower()]

    def add(self, book):
        """Prideda knygą į DB ir į cache."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO books (id, title, author, year, genre, total_copies, available_copies)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                vals = (book.id, book.title, book.author, book.year, book.genre, book.total_copies, book.available_copies)
                cursor.execute(sql, vals)
            conn.commit()
            # Pridedame į vietinį sąrašą
            self.books.append(book)
        finally:
            conn.close()

    def save(self):
        """
        Išsaugo visus atmintyje esančius pakeitimus į DB.
        Tai leidžia veikti senai logikai: book.available -= 1 -> repo.save()
        """
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE books SET total_copies = %s, available_copies = %s WHERE id = %s"
                # Surenkame duomenis iš self.books (kurie jau turi pakeistus skaičius)
                data = [(b.total_copies, b.available_copies, b.id) for b in self.books]
                cursor.executemany(sql, data)
            conn.commit()
        finally:
            conn.close()

    def remove(self, book_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            conn.commit()
            # Pašaliname iš atminties
            self.books = [b for b in self.books if b.id != str(book_id)]
            return True
        finally:
            conn.close()
    
    def remove_without_save(self, book_id):
        return self.remove(book_id)