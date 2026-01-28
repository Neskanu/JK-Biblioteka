"""
FILE: src/services/loan_service.py
PURPOSE: Valdo knygų skolinimo verslo logiką su SQLAlchemy.
RELATIONSHIPS:
  - Naudoja BookRepository ir UserRepository.
  - Kuria Loan objektus.
CONTEXT:
  - Atnaujinta: Dabar aiškiai išsaugo Loan objektus į 'loans' lentelę per ORM.
"""

from datetime import datetime, timedelta
from src.config import LOAN_PERIOD_DAYS, MAX_BOOKS_PER_USER
from src.models import Loan

class LoanService:
    def __init__(self, book_repo, user_repo):
        self.book_repo = book_repo
        self.user_repo = user_repo

    def borrow_book(self, user_id, book_id):
        # PASTABA: Priimame ID, ne objektus, kad gautume šviežius duomenis
        book = self.book_repo.get_by_id(book_id)
        user = self.user_repo.get_by_id(user_id)

        if not book:
            return False, "Knyga nerasta."
        if not user:
            return False, "Vartotojas nerastas."

        # 1. Patikrinimai
        if book.available_copies <= 0:
            return False, "Nėra laisvų kopijų."
        
        if len(user.loans) >= MAX_BOOKS_PER_USER:
            return False, "Pasiektas limitas."
            
        for loan in user.loans:
            if str(loan.book_id) == str(book.id):
                return False, "Jau turite šią knygą."

        # 2. Skolinimo veiksmas
        due_date = (datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)).strftime("%Y-%m-%d")
        
        # Kuriame naują Loan ORM objektą
        new_loan = Loan(
            user_id=user.id,
            book_id=book.id,
            title=book.title,
            due_date=due_date
        )
        
        # Modifikuojame knygą
        book.available_copies -= 1
        
        # 3. Išsaugojimas
        # Kadangi User.loans turi 'cascade=all', užtenka pridėti paskolą prie vartotojo
        # ir atnaujinti vartotoją (arba tiesiog pridėti loan į sesiją).
        # Tačiau saugiausia atnaujinti per repozitorijas.
        
        try:
            # Pridedame paskolą prie vartotojo sąrašo (SQLAlchemy tai suseks)
            user.loans.append(new_loan)
            
            # Atnaujiname vartotoją (tai išsaugos ir naują Loan dėl cascade)
            self.user_repo.update(user)
            
            # Atnaujiname knygos kiekį
            self.book_repo.update(book)
            
            return True, f"Knyga '{book.title}' išduota iki {due_date}."
            
        except Exception as e:
            return False, f"DB Klaida: {str(e)}"

    def return_book(self, user_id, book_id):
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            return False, "Vartotojas nerastas."

        loan_to_remove = None
        for loan in user.loans:
            if str(loan.book_id) == str(book_id):
                loan_to_remove = loan
                break
        
        if not loan_to_remove:
            return False, "Knyga nėra pasiskolinta."

        try:
            # Pašaliname paskolą iš sąrašo (SQLAlchemy pažymės trynimui)
            user.loans.remove(loan_to_remove)
            self.user_repo.update(user)

            # Atnaujiname knygą
            book = self.book_repo.get_by_id(book_id)
            if book:
                book.available_copies += 1
                self.book_repo.update(book)
            
            return True, "Knyga grąžinta."
        except Exception as e:
            return False, f"Grąžinimo klaida: {str(e)}"
            
    def return_all_books(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.loans:
            return False, "Nėra ką grąžinti."
            
        count = 0
        try:
            # Kuriame kopiją iteravimui, nes modifikuosime sąrašą
            for loan in list(user.loans):
                book = self.book_repo.get_by_id(loan.book_id)
                if book:
                    book.available_copies += 1
                    self.book_repo.update(book)
                
                user.loans.remove(loan)
                count += 1
            
            self.user_repo.update(user)
            return True, f"Grąžinta knygų: {count}"
        except Exception as e:
            return False, f"Klaida: {str(e)}"