"""
FILE: src/services/loan_service.py
PURPOSE: Valdo skolinimo transakcijas (SQL versija).
RELATIONSHIPS:
  - UserRepo: įrašo skolas į 'loans' lentelę.
  - BookRepo: atnaujina 'available_copies'.
"""

from datetime import datetime, timedelta
from src.config import LOAN_PERIOD_DAYS, MAX_BOOKS_PER_USER, DATE_FORMAT, FINE_PER_DAY

class LoanService:
    def __init__(self, book_manager, user_manager):
        # book_manager čia yra BookRepository
        # user_manager čia yra UserRepository
        self.book_repo = book_manager
        self.user_repo = user_manager

    def calculate_fine(self, user):
        """
        Suskaičiuoja baudas. Veikia taip pat, nes user objektas 
        jau turi užkrautą 'active_loans' sąrašą iš repo.
        """
        total_fine = 0.0
        overdue_books = []
        
        # Svarbu: user.active_loans sugeneruotas UserRepository._fetch_active_loans metodu
        for loan in user.active_loans:
            due_date_str = loan.get('due_date')
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    if datetime.now() > due_date:
                        days = (datetime.now() - due_date).days
                        fine = days * FINE_PER_DAY
                        total_fine += fine
                        overdue_books.append({
                            'book_id': loan['book_id'],
                            'days': days,
                            'fine': fine,
                            'due_date': due_date_str
                        })
                except ValueError:
                    continue
        return total_fine, overdue_books

    def borrow_book(self, user_id, book_id):
        """
        Vykdo skolinimą:
        1. Patikrinimai.
        2. UPDATE books (available_copies - 1).
        3. INSERT loans (user_id, book_id).
        """
        # Visada imame naujausius duomenis iš DB
        user = self.user_repo.get_by_id(user_id)
        book = self.book_repo.get_by_id(book_id)

        if not user: return False, "Vartotojas nerastas."
        if not book: return False, "Knyga nerasta."

        # 1. Patikrinimai
        current_fine, _ = self.calculate_fine(user)
        if current_fine > 0:
            return False, f"Turite {current_fine:.2f} € baudą. Skolinimas draudžiamas."

        if book.available_copies <= 0:
            return False, "Nėra laisvų kopijų."

        # Tikriname ar jau turi tokią knygą
        for loan in user.active_loans:
            if loan['book_id'] == book.id:
                return False, "Jau turite šios knygos kopiją."
        
        if len(user.active_loans) >= MAX_BOOKS_PER_USER:
            return False, "Pasiektas knygų limitas."

        # 2. VEIKSMAS - DB atnaujinimas
        try:
            # a) Sumažiname knygų kiekį
            book.available_copies -= 1
            self.book_repo.update(book) # SQL UPDATE
            
            # b) Sukuriame įrašą loans lentelėje
            return_date = (datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)).strftime(DATE_FORMAT)
            self.user_repo.add_loan(user.id, book.id, return_date) # SQL INSERT
            
            # c) Atnaujiname lokalu objektą (kad UI iškart matytų pokytį be perkrovimo)
            user.active_loans.append({
                "book_id": book.id,
                "title": book.title,
                "due_date": return_date
            })
            
            return True, f"Knyga '{book.title}' sėkmingai išduota."
            
        except Exception as e:
            return False, f"Sistemos klaida: {e}"

    def return_book(self, user_id, book_id):
        """
        Vykdo grąžinimą:
        1. DELETE FROM loans.
        2. UPDATE books (available_copies + 1).
        """
        user = self.user_repo.get_by_id(user_id)
        book = self.book_repo.get_by_id(book_id)

        if not user: return False, "Vartotojas nerastas."
        
        # Patikriname, ar vartotojas tikrai turi tą knygą
        # (Nors SQL DELETE ir taip nieko neištrintų, jei nėra, bet dėl žinutės vartotojui)
        has_book = any(l['book_id'] == book_id for l in user.active_loans)
        if not has_book:
            return False, "Ši knyga nėra pasiskolinta."

        try:
            # a) Ištriname skolą
            self.user_repo.remove_loan(user.id, book_id)
            
            # b) Padidiname knygų kiekį (jei knyga vis dar egzistuoja sistemoje)
            if book:
                if book.available_copies < book.total_copies:
                    book.available_copies += 1
                    self.book_repo.update(book)
            
            # c) Atnaujiname lokalų objektą UI daliai
            user.active_loans = [l for l in user.active_loans if l['book_id'] != book_id]
            
            return True, "Knyga sėkmingai grąžinta."
            
        except Exception as e:
            return False, f"Klaida: {e}"

    def return_all_books(self, user_id):
        # Čia reikėtų optimizuoti, bet kol kas kviečiame po vieną
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.active_loans:
            return False, "Nėra ką grąžinti."
            
        loans_copy = list(user.active_loans)
        count = 0
        for loan in loans_copy:
            success, _ = self.return_book(user_id, loan['book_id'])
            if success: count += 1
            
        return True, f"Grąžinta knygų: {count}"
    
    def get_user_overdue_loans(self, user):
        """Pagalbinis metodas UI."""
        _, overdue = self.calculate_fine(user)
        return overdue