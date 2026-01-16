"""
FILE: src/library.py
PURPOSE: Pagrindinis sistemos valdiklis (Facade Pattern).
RELATIONSHIPS:
  - Inicijuoja Repositories (Duomenys).
  - Inicijuoja Services (Logika).
  - Prijungia Services prie Repositories.
CONTEXT:
  - Tai yra "Vieno langelio principas" (Single Entry Point).
  - UI (Vartotojo sąsaja) bendrauja TIK su šia klase. UI neturi žinoti,
    kad egzistuoja kažkokie 'auth_service' ar 'user_repository'.
"""

from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository
from src.services.loan_service import LoanService
from src.services.stats_service import StatsService
from src.services.auth_service import AuthService
from src.services.inventory_service import InventoryService

class Library:
    def __init__(self):
        """
        Konstruktorius: "Surenka" visą aplikaciją.
        """
        # 1. DUOMENŲ SLUOKSNIS (Data Layer)
        # Šie objektai moka tik skaityti/rašyti failus.
        self.book_repository = BookRepository()
        self.user_repository = UserRepository()

        # 2. LOGIKOS SLUOKSNIS (Service Layer)
        # Šie objektai atlieka skaičiavimus ir tikrinimus.
        # Mes jiems 'įduodame' repozitorijas, kad jie galėtų gauti duomenis.
        self.auth_service = AuthService(self.user_repository)
        self.inventory_service = InventoryService(self.book_repository)
        self.loan_service = LoanService(self.book_repository, self.user_repository)
        self.stats_service = StatsService(self.book_repository, self.user_repository)

        # 3. SUDERINAMUMAS (Backward Compatibility)
        # Kadangi jūsų UI kodas (main.py, reader_ui.py) vis dar kreipiasi į
        # 'library.book_manager' ir 'library.user_manager', mes sukuriame
        # nuorodas (alias) į naujas repozitorijas.
        self.book_manager = self.book_repository
        self.user_manager = self.user_repository
        
        # Čia yra "Monkey Patching" technika (dinaminis metodų priskyrimas).
        # Senas 'user_manager' turėjo metodus 'authenticate_librarian' ir t.t.
        # Naujas 'user_repository' jų neturi (nes jis tik saugo duomenis).
        # Todėl mes priskiriame šiuos metodus iš 'auth_service' prie 'user_manager' nuorodos.
        # TAIP UI KODAS NESULŪŠ, nors struktūra pasikeitė.
        # self.user_repository.authenticate_librarian = self.auth_service.authenticate_librarian
        # self.user_repository.register_librarian = self.auth_service.register_librarian
        # self.user_repository.register_reader = self.auth_service.register_reader
        # self.user_repository.regenerate_reader_id = self.auth_service.regenerate_card_id
        # self.user_repository.delete_user_from_db = self.user_repository.remove 

        # Tas pats su knygų valdymu - prijungiame metodus iš InventoryService
        self.book_repository.add_book = self.inventory_service.add_book
        self.book_repository.batch_delete_books = self.inventory_service.batch_delete
        
        # Trumpos Lambda funkcijos paieškai (filtravimui)
        # Jos leidžia senam kodui kviesti sudėtingas paieškas per repozitoriją
        self.book_repository.get_candidates_by_author = lambda a: [b for b in self.book_repository.books if a.lower() in b.author.lower() and b.available_copies == b.total_copies] # Ši funkcija ieško autorių, kurių vardas/pavardė atitinka 'b'
        self.book_repository.get_candidates_by_genre = lambda g: [b for b in self.book_repository.books if g.lower() == b.genre.lower() and b.available_copies == b.total_copies]
        self.book_repository.get_candidates_by_year = lambda y: [b for b in self.book_repository.books if int(b.year) < y and b.available_copies == b.total_copies]
        
        # Pervadiname metodus, kad atitiktų senąjį API
        self.book_repository.restore_from_backup = self.book_repository.restore_backup
        self.book_repository.search_books = self.book_repository.search
        self.book_repository.get_all_books = self.book_repository.get_all

    # --- FASADO METODAI (Delegavimas) ---
    # Kai UI kviečia library.borrow_book(), biblioteka nieko nedaro pati,
    # o tik perduoda (deleguoja) darbą 'loan_service'.

    def borrow_book(self, user_id, book_id):
        return self.loan_service.borrow_book(user_id, book_id)

    def return_book(self, user_id, book_id):
        return self.loan_service.return_book(user_id, book_id)

    def return_all_books(self, user_id):
        return self.loan_service.return_all_books(user_id)

    def get_user_overdue_books(self, user_id):
        """Grąžina konkretaus vartotojo vėluojančias knygas."""
        user = self.user_repository.get_by_id(user_id)
        if user:
            return self.loan_service.get_user_overdue_loans(user)
        return []

    def get_all_overdue_books(self):
        """Admin ataskaita: visos vėluojančios knygos."""
        return self.stats_service.get_all_overdue_report()
    
    def get_candidates_lost(self, years):
        """Randa knygas, kurios laikomos prarastomis (labai senos skolos)."""
        return self.stats_service.get_lost_books_candidates(years)
    
    def get_advanced_statistics(self):
        """Grąžina bendrą statistiką."""
        return self.stats_service.get_advanced_statistics()

    def safe_delete_user(self, user):
        """
        Saugus vartotojo trynimas.
        Logika: Library klasė koordinuoja patikrinimą.
        """
        # 1. Patikriname, ar skaitytojas turi skolų
        if user.role == 'reader' and user.active_loans:
            titles = [l['title'] for l in user.active_loans]
            return False, titles
        
        # 2. Jei skolų nėra, kviečiame repozitoriją trynimui
        if self.user_repository.remove(user):
            return True, "Vartotojas sėkmingai pašalintas."
        return False, "Vartotojas nerastas."
    
    def safe_delete_book(self, book):
        """Verslo logika: trina knygą tik jei ji saugi trinti.
        Bando saugiai ištrinti knygą.
        Grąžina (bool, message).
        """
        # Tikriname ar knyga yra paskolinta
        # Naudojame int(), kad užtikrintume, jog lyginame skaičius, o ne tekstą
        if int(book.available_copies) < int(book.total_copies):
            return False, "Negalima ištrinti: knyga šiuo metu yra paskolinta."
        
        self.book_repository.remove(book.id)
        if book in self.book_manager.books:
            self.book_manager.books.remove(book)
        self.book_repository.save()
        
        return True, f"Knyga '{book.title}' sėkmingai ištrinta."