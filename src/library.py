"""
FILE: src/library.py
PURPOSE: Pagrindinis sistemos valdiklis (Controller/Facade).
RELATIONSHIPS:
  - Inicijuoja BookManager ir UserManager.
  - Inicijuoja LoanService ir StatsService.
  - Aptarnauja užklausas iš UI (main.py, app.py).
CONTEXT:
  - Tai yra "single entry point" visai programos logikai. UI failai turėtų
    bendrauti TIK su šia klase, o ne tiesiogiai su manageriais ar servisais.
"""

from src.book_manager import BookManager
from src.user_manager import UserManager
from src.services.loan_service import LoanService
from src.services.stats_service import StatsService

class Library:
    def __init__(self):
        """Inicijuoja visus posistemius."""
        # Duomenų sluoksnis
        self.book_manager = BookManager()
        self.user_manager = UserManager()
        
        # Servisų sluoksnis (Business Logic)
        # Įduodame managerius kaip priklausomybes (Dependency Injection)
        self.loan_service = LoanService(self.book_manager, self.user_manager)
        self.stats_service = StatsService(self.book_manager, self.user_manager)

    # --- SKOLINIMO FUNKCIJOS (Deleguojamos LoanService) ---

    def borrow_book(self, user_id, book_id):
        """Bando paskolinti knygą."""
        return self.loan_service.borrow_book(user_id, book_id)

    def return_book(self, user_id, book_id):
        """Grąžina knygą."""
        return self.loan_service.return_book(user_id, book_id)

    def return_all_books(self, user_id):
        """Grąžina visas vartotojo knygas."""
        return self.loan_service.return_all_books(user_id)

    def get_user_overdue_books(self, user_id):
        """Grąžina konkretaus vartotojo vėluojančias knygas."""
        user = self.user_manager.get_user_by_id(user_id)
        if user:
            return self.loan_service.get_user_overdue_loans(user)
        return []

    # --- STATISTIKOS FUNKCIJOS (Deleguojamos StatsService) ---

    def get_all_overdue_books(self):
        """Grąžina visų vėluojančių knygų sąrašą adminui."""
        return self.stats_service.get_all_overdue_report()
    
    def get_candidates_lost(self, years_overdue):
        """Grąžina knygas, kurios laikomos prarastomis."""
        return self.stats_service.get_lost_books_candidates(years_overdue)
    
    def get_advanced_statistics(self):
        """Grąžina bendrą bibliotekos statistiką."""
        return self.stats_service.get_advanced_statistics()

    # --- VARTOTOJŲ VALDYMO PAGALBINĖS FUNKCIJOS ---
    
    def safe_delete_user(self, user):
        """
        Patikrina, ar saugu trinti vartotoją (ar neturi skolų),
        ir jei taip - ištrina per user_manager.
        """
        # 1. Patikriname, ar skaitytojas turi knygų
        if user.role == 'reader' and user.active_loans:
            borrowed_titles = [loan['title'] for loan in user.active_loans]
            return False, borrowed_titles

        # 2. Jei skolų nėra, triname
        if self.user_manager.delete_user_from_db(user):
            return True, "Vartotojas sėkmingai pašalintas."
        return False, "Vartotojas nerastas duomenų bazėje."