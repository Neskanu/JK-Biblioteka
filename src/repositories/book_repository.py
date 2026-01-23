"""
FILE: src/repositories/book_repository.py
PURPOSE: Valdo knygų duomenų mainus tarp aplikacijos ir SQLite duomenų bazės.
RELATIONSHIPS:
  - Importuoja database.py ryšiui gauti.
  - Konvertuoja DB eilutes į src/models.py Book objektus.
CONTEXT:
  - Pakeičia senąją JSON implementaciją.
  - Naudoja tiesiogines SQL užklausas CRUD operacijoms.
"""

import sqlite3
from typing import List, Optional
from src.database import get_connection
from src.models import Book

class BookRepository:
    def __init__(self):
        """
        Konstruktorius. SQL versijoje mums nereikia užkrauti visų duomenų į atmintį
        starto metu, todėl init yra tuščias.
        """
        pass

    def _row_to_book(self, row: sqlite3.Row) -> Book:
        """
        Pagalbinis metodas: Konvertuoja SQL eilutę į Book objektą.
        Svarbu, kad stulpelių pavadinimai atitiktų Book klasės laukus arba būtų konvertuojami.
        """
        return Book(
            id=row['id'],
            title=row['title'],
            author=row['author'],
            year=row['year'],
            genre=row['genre'],
            total_copies=row['total_copies'],
            available_copies=row['available_copies']
        )

    def get_all(self) -> List[Book]:
        """
        Grąžina visas knygas iš duomenų bazės.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM books")
            rows = cursor.fetchall()
            # Konvertuojame kiekvieną eilutę į Book objektą
            return [self._row_to_book(row) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, book_id: str) -> Optional[Book]:
        """
        Suranda knygą pagal unikalų ID.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM books WHERE id = ?", (str(book_id),))
            row = cursor.fetchone()
            if row:
                return self._row_to_book(row)
            return None
        finally:
            conn.close()

    def find_by_details(self, title: str, author: str) -> Optional[Book]:
        """
        Suranda knygą pagal pavadinimą ir autorių (dublikatų prevencijai).
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # SQL paieška nepriklausomai nuo raidžių registro (COLLATE NOCASE būtų geriau, 
            # bet čia naudojame paprastą LOWER() funkciją).
            cursor.execute(
                "SELECT * FROM books WHERE LOWER(title) = ? AND LOWER(author) = ?", 
                (title.lower(), author.lower())
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_book(row)
            return None
        finally:
            conn.close()

    def search(self, query: str) -> List[Book]:
        """
        Paieška naudojant SQL LIKE operatorių.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            search_term = f"%{query}%"
            cursor.execute(
                "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", 
                (search_term, search_term)
            )
            rows = cursor.fetchall()
            return [self._row_to_book(row) for row in rows]
        finally:
            conn.close()

    def add(self, book: Book):
        """
        Įterpia naują knygą į duomenų bazę.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO books (id, title, author, year, genre, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (book.id, book.title, book.author, book.year, book.genre, book.total_copies, book.available_copies))
            conn.commit()
        finally:
            conn.close()

    def remove(self, book_id: str):
        """
        Ištrina knygą iš duomenų bazės.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM books WHERE id = ?", (str(book_id),))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            return False
        finally:
            conn.close()
            
    def remove_without_save(self, book_id: str):
        """
        Suderinamumui su senu kodu. SQL atveju remove() veikia iškart,
        todėl šis metodas tiesiog kviečia remove().
        """
        return self.remove(book_id)

    def save(self):
        """
        Suderinamumui su senu kodu (Backward Compatibility).
        JSON versijoje šis metodas įrašydavo visą sąrašą į failą.
        SQL versijoje pakeitimai vyksta iškart (autocommit), todėl šis metodas gali būti tuščias
        arba naudojamas specifiniam 'commit', jei naudotume transakcijas per kelis metodus.
        """
        # SQL atveju duomenys išsaugomi iškart po add/remove/update operacijų.
        # Tačiau, kadangi jūsų Services kodas (pvz., InventoryService) keičia objekto laukus
        # (pvz., book.total_copies += 1) ir tada kviečia repo.save(),
        # čia mes turėtume realizuoti UPDATE logiką visiems objektams, bet tai neefektyvu.
        
        # Geriausia praktika: ateityje Servisai turėtų kviesti `repo.update(book)`.
        # Kol kas paliekame tuščią, bet įspėjame.
        pass
        
    def update(self, book: Book):
        """
        NAUJAS METODAS: Atnaujina esamos knygos duomenis.
        Būtina naudoti vietoje senojo 'modify object -> save()'.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE books 
                SET title=?, author=?, year=?, genre=?, total_copies=?, available_copies=?
                WHERE id=?
            ''', (book.title, book.author, book.year, book.genre, book.total_copies, book.available_copies, book.id))
            conn.commit()
        finally:
            conn.close()

    # Kadangi senas kodas naudoja tiesioginį kreipimąsi į library.book_manager.books sąrašą,
    # mes sukuriame 'property', kuris imituoja šį sąrašą (nors tai nėra efektyvu dideliems kiekiams).
    @property
    def books(self):
        return self.get_all()