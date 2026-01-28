"""
FILE: src/library.py
PURPOSE: Pagrindinis fasadas (Facade) bibliotekos sistemos valdymui.
RELATIONSHIPS:
  - Inicializuoja ir valdo servisus (Auth, Book, Loan, User, Stats).
  - Veikia kaip centrinis taškas UI kodui pasiekti verslo logiką.
CONTEXT:
  - Pridėti trūkstami 'safe_delete' ir statistikos metodai, kurių reikalauja admin_ui.
"""

from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository
from src.services.loan_service import LoanService
from src.services.inventory_service import InventoryService
from src.services.stats_service import StatsService
from src.services.auth_service import AuthService
from src.data_manager import DataManager

class Library:
    def __init__(self):
        """
        Inicializuoja visus bibliotekos komponentus ir servisus.
        """
        self.data_manager = DataManager()
        self.book_repository = BookRepository()
        self.user_repository = UserRepository()

        self.auth_service = AuthService(self.user_repository)
        self.loan_service = LoanService(self.book_repository, self.user_repository)
        self.inventory_service = InventoryService(self.book_repository)
        self.stats_service = StatsService(self.book_repository, self.user_repository)

        # Alias senam kodui
        self.book_manager = self.inventory_service 

    # --- Autentifikavimo Delegavimas ---
    def login(self, username, password):
        return self.auth_service.authenticate(username, password)

    def register_user(self, username, password, role='reader'):
        return self.auth_service.register_user(username, password, role)

    # --- Paskolų Valdymas ---
    def borrow_book(self, user_id, book_id):
        return self.loan_service.borrow_book(user_id, book_id)

    def return_book(self, user_id, book_id):
        return self.loan_service.return_book(user_id, book_id)

    def return_all_books(self, user_id):
        return self.loan_service.return_all_books(user_id)

    # --- Knygų Valdymas ---
    def find_books(self, query):
        return self.inventory_service.search_books(query)
        
    def add_book(self, title, author, year, total_copies, genre):
        return self.inventory_service.add_book(title, author, year, total_copies, genre)

    def remove_book(self, book_id):
        return self.inventory_service.remove_book(book_id)

    # --- SAUGUS TRYNIMAS (Reikalaujama admin_ui) ---
    def safe_delete_user(self, user):
        """
        Ištrina vartotoją tik jei jis neturi skolų.
        """
        if user.active_loans:
            return False, "Negalima ištrinti: vartotojas turi negrąžintų knygų."
        
        success = self.user_repository.remove(user)
        if success:
            return True, "Vartotojas sėkmingai ištrintas."
        return False, "Nepavyko ištrinti vartotojo."

    def safe_delete_book(self, book):
        """
        Ištrina knygą tik jei visos kopijos grąžintos.
        """
        if book.total_copies != book.available_copies:
            return False, f"Negalima ištrinti: {book.total_copies - book.available_copies} kopija(-os) vis dar pas skaitytojus."
        
        success, msg = self.inventory_service.remove_book(book.id)
        return success, msg

    # --- STATISTIKA (Delegavimas) ---
    def get_advanced_statistics(self):
        """Grąžina bendrą statistiką admin skydui."""
        return self.stats_service.get_advanced_statistics()

    def get_all_overdue_books(self):
        """Grąžina vėluojančių knygų sąrašą."""
        return self.stats_service.get_all_overdue_books()

    # --- Sistemos Valdymas ---
    def save_data(self):
        pass