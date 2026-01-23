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
from src.config import LOAN_PERIOD_DAYS, MAX_BOOKS_PER_USER, DATE_FORMAT, FINE_PER_DAY

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

    def calculate_fine(self, user):
        """
        Suskaičiuoja bendrą vartotojo baudą už visas vėluojančias knygas.
        Taip pat grąžina detalią informaciją atvaizdavimui.
        """
        total_fine = 0.0
        overdue_books = []
        
        # Tikriname kiekvieną pasiskolintą knygą
        # user.borrowed_books turėtų būti sąrašas žodynų arba objektų
        loans = getattr(user, 'borrowed_books', [])

        for loan in loans:
            # 1. Ištraukiame grąžinimo terminą
            # Priklausomai nuo jūsų struktūros, tai gali būti loan['due_date'] arba loan.due_date
            due_date_str = loan.get('due_date') if isinstance(loan, dict) else getattr(loan, 'due_date', None)
            
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    today = datetime.now()
                    
                    # 2. Tikriname, ar vėluoja
                    if today > due_date:
                        delta = today - due_date
                        overdue_days = delta.days
                        
                        # 3. Skaičiuojame baudą šiai knygai
                        book_fine = overdue_days * FINE_PER_DAY
                        total_fine += book_fine
                        
                        # Išsaugome detales atvaizdavimui
                        # Mums reikia knygos pavadinimo (jei jis saugomas loane, puiku, jei ne - reiktų ieškoti pagal ID)
                        # Darykime prielaidą, kad loan turi 'title' arba gausime jį UI dalyje
                        book_id = loan.get('id') or loan.get('book_id')
                        
                        overdue_books.append({
                            'book_id': book_id,
                            'days': overdue_days,
                            'fine': book_fine,
                            'due_date': due_date_str
                        })
                except ValueError:
                    continue # Jei data blogo formato
        return total_fine, overdue_books

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
        user = self.user_manager.get_by_id(user_id)
        book = self.book_manager.get_by_id(book_id)

        if not user: return False, "Vartotojas nerastas."
        if not book: return False, "Knyga nerasta."

        # 1. Pirmiausia patikriname skolas
        current_fine, _ = self.calculate_fine(user)
        
        if current_fine > 0:
            return False, f"Turite nesumokėtą {current_fine:.2f} € baudą už vėluojančias knygas. Skolinimas draudžiamas."

        # 2. Likučio tikrinimas
        if book.available_copies <= 0:
            return False, "Šiuo metu visos šios knygos kopijos yra išduotos."

        # 3. Vėlavimų tikrinimas (naudojame vidinį metodą)
        if self.get_user_overdue_loans(user):
            return False, "Turite vėluojančių knygų! Skolinimas draudžiamas."

        # 4. Limito tikrinimas
        if len(user.active_loans) >= MAX_BOOKS_PER_USER:
            return False, f"Pasiektas {MAX_BOOKS_PER_USER} knygų limitas."

        # 5. Dublikatų tikrinimas
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
        user = self.user_manager.get_by_id(user_id)
        # Knygos objektas gali būti None, jei knyga buvo ištrinta iš sistemos,
        # bet vartotojas vis dar turi įrašą apie ją.
        book = self.book_manager.get_by_id(book_id)

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
        user = self.user_manager.get_by_id(user_id)
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