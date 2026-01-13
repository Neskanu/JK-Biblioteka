from src.models import Book
from src.data_manager import load_data, save_data

DATA_FILE = 'data/books.json'

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

    def remove_old_books(self, year_threshold):
        """Ištrina knygas, senesnes nei nurodyti metai."""
        initial_count = len(self.books)
        # Paliekame tik tas, kurios naujesnės arba lygios metams (>=)
        # ARBA tas, kurios šiuo metu paskolintos (kad nedingtų skolos)
        self.books = [b for b in self.books if int(b.year) >= year_threshold or b.is_borrowed]
        
        removed_count = initial_count - len(self.books)
        if removed_count > 0:
            self.save()
        return removed_count

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