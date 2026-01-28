"""
FILE: src/services/loan_service.py
PURPOSE: Valdo knygų skolinimo verslo logiką.
RELATIONSHIPS:
  - Naudoja BookRepository ir UserRepository.
  - Tikrina taisykles (MAX_BOOKS, available_copies).
CONTEXT:
  - PRIDĖTA: Detalus klaidų (debug) spausdinimas į konsolę.
  - PATAISYTA: Užtikrinamas suderinamumas su SQL UserRepository struktūra.
"""

from datetime import datetime, timedelta
from src.config import LOAN_PERIOD_DAYS, MAX_BOOKS_PER_USER

class LoanService:
    def __init__(self, book_repo, user_repo):
        self.book_repo = book_repo
        self.user_repo = user_repo

    def borrow_book(self, user, book_id):
        """
        Bando paskolinti knygą vartotojui.
        Grąžina: (bool, str) -> (sėkmė, žinutė)
        """
        try:
            print(f"DEBUG: Pradedamas knygos paėmimas. User: {user.username}, BookID: {book_id}")

            # 1. Patikriname knygą
            book = self.book_repo.get_by_id(book_id)
            if not book:
                print("DEBUG: Knyga nerasta.")
                return False, "Knyga nerasta sistemoje."

            print(f"DEBUG: Knyga rasta: {book.title}. Laisvų kopijų: {book.available_copies}")

            # 2. Patikriname, ar yra laisvų kopijų
            if book.available_copies <= 0:
                return False, "Šiuo metu visos knygos kopijos yra užimtos."

            # 3. Patikriname vartotojo limitus
            # user.active_loans gali būti None, jei tai naujas objektas iš DB
            if not hasattr(user, 'active_loans') or user.active_loans is None:
                user.active_loans = []

            print(f"DEBUG: Vartotojas turi {len(user.active_loans)} aktyvių paskolų.")

            if len(user.active_loans) >= MAX_BOOKS_PER_USER:
                return False, f"Pasiektas maksimalus ({MAX_BOOKS_PER_USER}) pasiskolintų knygų limitas."

            # 4. Patikriname, ar jau neturi šios knygos
            for loan in user.active_loans:
                # SQL repozitorija grąžina 'book_id', JSON galbūt seniau naudojo ką kitą
                loan_book_id = loan.get('book_id')
                # Konvertuojame į string palyginimui, nes ID formatai gali skirtis
                if str(loan_book_id) == str(book_id):
                    return False, "Jūs jau turite pasiskolinę šią knygą."

            # 5. Vykdome skolinimą
            due_date = datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)
            due_date_str = due_date.strftime("%Y-%m-%d")

            # Sukuriame įrašą. SVARBU: Raktai turi atitikti UserRepository.save() SQL logiką
            new_loan = {
                'book_id': str(book.id),
                'title': book.title,
                'due_date': due_date_str
            }

            # Atnaujiname objektus atmintyje
            user.active_loans.append(new_loan)
            book.available_copies -= 1

            print("DEBUG: Objektai atmintyje atnaujinti. Bandoma saugoti į DB...")

            # 6. Saugome į DB
            # Svarbu: Kviečiame save() abiems repozitorijoms
            self.book_repo.save()
            print("DEBUG: Knygų repozitorija išsaugota.")
            
            self.user_repo.save()
            print("DEBUG: Vartotojų repozitorija išsaugota.")

            return True, f"Knyga '{book.title}' sėkmingai išduota iki {due_date_str}."

        except Exception as e:
            # Čia pamatysime tikrąją SQL klaidą terminale
            import traceback
            traceback.print_exc()
            print(f"CRITICAL ERROR in borrow_book: {e}")
            return False, f"Sistemos klaida: {str(e)}"

    def return_book(self, user, book_id):
        """
        Grąžina knygą.
        """
        try:
            print(f"DEBUG: Bandoma grąžinti knygą {book_id} vartotojui {user.username}")
            
            # Randame paskolą
            loan_to_remove = None
            for loan in user.active_loans:
                if str(loan.get('book_id')) == str(book_id):
                    loan_to_remove = loan
                    break
            
            if not loan_to_remove:
                return False, "Ši knyga nėra pasiskolinta jūsų vardu."

            # Randame knygą, kad padidintume kiekį
            book = self.book_repo.get_by_id(book_id)
            if book:
                book.available_copies += 1
            else:
                # Knyga galėjo būti ištrinta iš sistemos, bet vis tiek leidžiame vartotojui "grąžinti"
                print("DEBUG: Grąžinama knyga, kurios nebėra books lentelėje.")

            # Pašaliname iš vartotojo sąrašo
            user.active_loans.remove(loan_to_remove)

            # Saugome pakeitimus
            self.book_repo.save()
            self.user_repo.save()

            return True, "Knyga sėkmingai grąžinta."

        except Exception as e:
            print(f"CRITICAL ERROR in return_book: {e}")
            return False, f"Grąžinimo klaida: {str(e)}"