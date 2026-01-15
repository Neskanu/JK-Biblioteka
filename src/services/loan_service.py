"""
FILE: src/services/loan_service.py
PURPOSE: Valdo verslo logiką, susijusią su knygų išdavimu ir grąžinimu.
RELATIONSHIPS:
  - Importuoja nustatymus iš src/config.py
  - Veikia kaip atskiras logikos modulis, naudojamas Library klasės.
CONTEXT:
  - Atskiriame "Transakcijų" logiką nuo bendro valdiklio. Tai palengvina testavimą
    ir klaidų paiešką.
"""

from datetime import datetime, timedelta
from src.config import LOAN_PERIOD_DAYS, MAX_BOOKS_PER_USER, DATE_FORMAT

class LoanService:
    def __init__(self, book_manager, user_manager):
        """
        Inicijuoja servisą su priklausomybėmis.
        
        Parametrai:
        - book_manager: Objektas, valdantis knygų duomenis.
        - user_manager: Objektas, valdantis vartotojų duomenis.
        """
        self.book_manager = book_manager
        self.user_manager = user_manager

    def borrow_book(self, user_id, book_id):
        """
        Vykdo knygos skolinimo transakciją.
        
        Patikrina:
        1. Ar vartotojas ir knyga egzistuoja.
        2. Ar yra laisvų kopijų.
        3. Ar vartotojas neturi skolų.
        4. Ar neviršytas limitas.
        
        Grąžina: (bool, str) -> (Sėkmė, Pranešimas)
        """
        user = self.user_manager.get_user_by_id(user_id)
        book = self.book_manager.get_book_by_id(book_id)

        if not user: return False, "Vartotojas nerastas."
        if not book: return False, "Knyga nerasta."

        # 1. Likučio tikrinimas
        if book.available_copies <= 0:
            return False, "Šiuo metu visos šios knygos kopijos yra išduotos."

        # 2. Vėlavimų tikrinimas (naudojame vidinį metodą)
        if self.get_user_overdue_loans(user):
            return False, "Turite vėluojančių knygų! Skolinimas draudžiamas."

        # 3. Limito tikrinimas
        if len(user.active_loans) >= MAX_BOOKS_PER_USER:
            return False, f"Pasiektas {MAX_BOOKS_PER_USER} knygų limitas."

        # 4. Dublikatų tikrinimas
        for loan in user.active_loans:
            if loan['book_id'] == book.id:
                return False, "Jau turite šios knygos kopiją."

        # --- VEIKSMAS ---
        book.available_copies -= 1
        
        return_date = datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)
        formatted_date = return_date.strftime(DATE_FORMAT)
        
        loan_record = {
            "book_id": book.id,
            "title": book.title,
            "due_date": formatted_date
        }
        
        user.active_loans.append(loan_record)

        # Išsaugome pakeitimus per managerius
        self.book_manager.save()
        self.user_manager.save()

        return True, f"Knyga '{book.title}' išduota. Liko kopijų: {book.available_copies}"

    def return_book(self, user_id, book_id):
        """
        Vykdo knygos grąžinimo procedūrą.
        """
        user = self.user_manager.get_user_by_id(user_id)
        # Knygos objektas gali būti None, jei knyga buvo ištrinta iš sistemos,
        # bet vartotojas vis dar turi įrašą apie ją.
        book = self.book_manager.get_book_by_id(book_id)

        if not user: return False, "Vartotojas nerastas."

        loan_to_remove = None
        for loan in user.active_loans:
            if loan['book_id'] == book_id:
                loan_to_remove = loan
                break
        
        if not loan_to_remove:
            return False, "Vartotojas neturi pasiėmęs šios knygos."

        # Pašaliname iš vartotojo
        user.active_loans.remove(loan_to_remove)
        
        # Grąžiname į lentyną (jei knyga vis dar egzistuoja duomenų bazėje)
        if book:
            book.available_copies += 1
            if book.available_copies > book.total_copies:
                book.available_copies = book.total_copies

        self.book_manager.save()
        self.user_manager.save()

        return True, "Knyga sėkmingai grąžinta."

    def return_all_books(self, user_id):
        """
        Grąžina visas konkretaus vartotojo knygas.
        """
        user = self.user_manager.get_user_by_id(user_id)
        if not user or not user.active_loans:
            return False, "Nėra ką grąžinti."
            
        loans_copy = list(user.active_loans)
        count = 0
        
        for loan in loans_copy:
            self.return_book(user_id, loan['book_id'])
            count += 1
            
        return True, f"Grąžinta knygų: {count}"

    def get_user_overdue_loans(self, user):
        """
        Grąžina sąrašą vėluojančių paskolų konkrečiam vartotojui.
        """
        if user.role != 'reader':
            return []

        overdue_loans = []
        today = datetime.now().date()

        for loan in user.active_loans:
            due_date_str = loan['due_date']
            try:
                due_date_obj = datetime.strptime(due_date_str, DATE_FORMAT).date()
                if due_date_obj < today:
                    overdue_loans.append(loan)
            except ValueError:
                pass
        
        return overdue_loans