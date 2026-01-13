import os
import json # Reikės backup krovimui
from datetime import datetime, timedelta # Reikės trinant prarastas knygas
from src.models import Book
from src.data_manager import load_data, save_data
from src.data_manager import load_data, save_data, get_data_file_path

# ... (kelio nustatymas) ...
DATA_FILE = get_data_file_path('books.json')
BACKUP_FILE = get_data_file_path('books_backup.json')

class BookManager:
    def __init__(self):
        # Užkrauname "žalius" duomenis (list of dicts)
        data = load_data(DATA_FILE)
        # Paverčiame juos į Book objektus
        self.books = [Book.from_dict(item) for item in data]

    def save(self):
        """Išsaugo visus pakeitimus į failą."""
        # Paverčiame objektus atgal į dict
        data = [book.to_dict() for book in self.books]
        save_data(DATA_FILE, data)

    def add_book(self, title, author, year, genre):
        new_book = Book(title, author, year, genre)
        self.books.append(new_book)
        self.save() # Iškart saugome
        return new_book

    def get_candidates_by_year(self, year_threshold):
        """Grąžina sąrašą knygų, kurios senesnės nei X ir nėra paskolintos."""
        candidates = []
        for b in self.books:
            if int(b.year) < year_threshold and not b.is_borrowed:
                candidates.append(b)
        return candidates

    def get_candidates_by_author(self, author_name):
        """Grąžina autoriaus knygas, kurios nėra paskolintos."""
        candidates = []
        for b in self.books:
            if author_name.lower() in b.author.lower() and not b.is_borrowed:
                candidates.append(b)
        return candidates

    def get_candidates_by_genre(self, genre):
        candidates = []
        for b in self.books:
            if genre.lower() == b.genre.lower() and not b.is_borrowed:
                candidates.append(b)
        return candidates

    def get_candidates_lost(self, years_overdue):
        """Grąžina knygas, kurios vėluoja daugiau nei X metų."""
        threshold_date = datetime.now() - timedelta(days=years_overdue * 365)
        candidates = []
        for b in self.books:
            if b.is_borrowed and b.due_date:
                try:
                    due_date_obj = datetime.strptime(b.due_date, "%Y-%m-%d")
                    if due_date_obj < threshold_date:
                        candidates.append(b)
                except ValueError:
                    pass
        return candidates

    def batch_delete_books(self, books_to_delete):
        """
        Ištrina paduotą knygų sąrašą iš pagrindinės bibliotekos.
        """
        initial_count = len(self.books)
        
        # Sukuriame rinkinį ID greitesniam tikrinimui
        ids_to_remove = {b.id for b in books_to_delete}
        
        # Paliekame tas knygas, kurių ID NĖRA trinamų sąraše
        self.books = [b for b in self.books if b.id not in ids_to_remove]
        
        removed_count = initial_count - len(self.books)
        self.save()
        return removed_count

    # --- BACKUP RESTORE ---

    def restore_from_backup(self):
        """
        Bando užkrauti duomenis iš books_backup.json.
        Grąžina (True/False, žinutė).
        """
        if not os.path.exists(BACKUP_FILE):
            return False, "Atsarginis failas (books_backup.json) nerastas."

        try:
            # Naudojame tą pačią load_data funkciją arba tiesiogiai json
            data = load_data(BACKUP_FILE)
            if not data:
                return False, "Atsarginis failas tuščias arba sugadintas."

            # Atkuriame objektus
            self.books = [Book.from_dict(item) for item in data]
            self.save() # Iškart įrašome į pagrindinį failą
            return True, f"Sėkmingai atkurta {len(self.books)} knygų."
        except Exception as e:
            return False, f"Klaida atkuriant: {e}"

    def get_book_by_id(self, book_id):
        """Suranda knygos objektą pagal ID."""
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def search_books(self, query):
        """Ieško pagal pavadinimą arba autorių (neatsižvelgiant į didžiąsias raides)."""
        query = query.lower()
        results = []
        for book in self.books:
            if query in book.title.lower() or query in book.author.lower():
                results.append(book)
        return results
        
    def get_all_books(self):
        return self.books