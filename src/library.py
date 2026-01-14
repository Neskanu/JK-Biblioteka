from datetime import datetime, timedelta
from collections import Counter #patogiau kelioms statistikos fuinkcijoms
from src.book_manager import BookManager
from src.user_manager import UserManager

# Nustatome skolinimo terminą (pvz., 14 dienų)
LOAN_PERIOD_DAYS = 14
MAX_BOOKS_PER_USER = 5

class Library:
    """
    PAGRINDINIS VALDIKLIS (CONTROLLER)
    
    Ši klasė yra "smegenys", kurios sujungia knygų valdymą (BookManager) 
    ir vartotojų valdymą (UserManager).
    
    Jos atsakomybės:
    1. Koordinuoti veiksmus tarp vartotojų ir knygų (pvz., skolinimas).
    2. Užtikrinti verslo taisykles (pvz., negalima skolinti, jei yra skola).
    3. Atlikti sudėtingesnius skaičiavimus (vėlavimų tikrinimas).
    
    Main.py failas bendraus TIK su šia klase.
    """

    def __init__(self):
        # Sukuriame vadybininkus
        self.book_manager = BookManager()
        self.user_manager = UserManager()

    def get_user_overdue_books(self, user_id):
        """
        Patikrina, ar konkretus vartotojas turi vėluojančių knygų.
        Grąžina vėluojančių knygų sąrašą.
        """
        user = self.user_manager.get_user_by_id(user_id)
        if not user or user.role != 'reader':
            return []

        overdue_loans = []
        today = datetime.now().date()

        # Iteruojame per vartotojo paskolų sąrašą
        for loan in user.active_loans:
            due_date_str = loan['due_date']
            try:
                due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                if due_date_obj < today:
                    # Pridedame informaciją apie vėlavimą
                    overdue_loans.append(loan)
            except ValueError:
                pass
        
        return overdue_loans

    def borrow_book(self, user_id, book_id):
        """
        Bando paskolinti knygą vartotojui.
        
        Grąžina tuple: (Success: bool, Message: str)
        Tai leidžia main.py lengvai parodyti vartotojui rezultatą.
        """
        # 1. Gauname objektus
        user = self.user_manager.get_user_by_id(user_id)
        book = self.book_manager.get_book_by_id(book_id)

        if not user: return False, "Vartotojas nerastas."
        if not book: return False, "Knyga nerasta."

        # 1. Ar yra laisvų kopijų?
        if book.available_copies <= 0:
            return False, "Šiuo metu visos šios knygos kopijos yra išduotos."

        # 2. Vėlavimai
        overdue = self.get_user_overdue_books(user_id)
        if overdue:
            return False, "Turite vėluojančių knygų!"

        # 3. Limitas
        if len(user.active_loans) >= MAX_BOOKS_PER_USER:
            return False, "Pasiektas 5 knygų limitas."

        # 4. Ar jau turi šią knygą?
        for loan in user.active_loans:
            if loan['book_id'] == book.id:
                return False, "Jau turite šios knygos kopiją."

        # --- VEIKSMAS ---
        
        # A. Atnaujiname knygos likutį
        book.available_copies -= 1
        
        # B. Sukuriame paskolos įrašą vartotojui
        return_date = datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)
        formatted_date = return_date.strftime("%Y-%m-%d")
        
        loan_record = {
            "book_id": book.id,
            "title": book.title, # Išsaugome pavadinimą patogumui
            "due_date": formatted_date
        }
        
        user.active_loans.append(loan_record)

        self.book_manager.save()
        self.user_manager.save()

        return True, f"Knyga '{book.title}' išduota. Liko kopijų: {book.available_copies}"

    def return_book(self, user_id, book_id):
        """Grąžina knygą į biblioteką."""
        user = self.user_manager.get_user_by_id(user_id)
        book = self.book_manager.get_book_by_id(book_id)

        if not user: return False, "Vartotojas nerastas."

        # Ieškome paskolos įrašo
        loan_to_remove = None
        for loan in user.active_loans:
            if loan['book_id'] == book_id:
                loan_to_remove = loan
                break
        
        if not loan_to_remove:
            return False, "Vartotojas neturi pasiėmęs šios knygos."

        # --- VEIKSMAS ---
        
        # A. Pašaliname iš vartotojo
        user.active_loans.remove(loan_to_remove)
        
        # B. Padidiname knygos likutį (jei knyga dar egzistuoja sistemoje)
        if book:
            book.available_copies += 1
            # Saugiklis, kad neviršytume total
            if book.available_copies > book.total_copies:
                book.available_copies = book.total_copies

        self.book_manager.save()
        self.user_manager.save()

        return True, "Knyga sėkmingai grąžinta."
    
    # --- NAUJAS METODAS: GRĄŽINTI VISKĄ ---
    def return_all_books(self, user_id):
        """Vartotojas grąžina visas turimas knygas."""
        user = self.user_manager.get_user_by_id(user_id)
        if not user or not user.active_loans:
            return False, "Nėra ką grąžinti."
            
        # Kopijuojame sąrašą, kad galėtume iteruoti
        loans_copy = list(user.active_loans)
        count = 0
        
        for loan in loans_copy:
            self.return_book(user_id, loan['book_id'])
            count += 1
            
        return True, f"Grąžinta knygų: {count}"

    def get_all_overdue_books(self):
        """Administratoriui: grąžina visus vėluojančius įrašus."""
        # Ši logika sudėtingesnė, nes knyga pati "nežino", kad vėluoja.
        # Reikia eiti per VARTOTOJUS.
        overdue_report = []
        today = datetime.now().date()
        
        for user in self.user_manager.users:
            if user.role == 'reader':
                for loan in user.active_loans:
                    try:
                        due = datetime.strptime(loan['due_date'], "%Y-%m-%d").date()
                        if due < today:
                            # Konstruojame ataskaitos objektą (ne Book objektą, o info)
                            overdue_report.append({
                                "title": loan['title'],
                                "user": user.username,
                                "due_date": loan['due_date']
                            })
                    except ValueError:
                        pass
        return overdue_report
    
    def safe_delete_user(self, user):
        """
        Bando ištrinti vartotoją.
        Jei vartotojas turi skolų -> Grąžina (False, klaidų sąrašas).
        Jei viskas gerai -> Ištrina ir grąžina (True, sėkmės žinutė).
        """
        # 1. Patikriname, ar skaitytojas turi knygų
        if user.role == 'reader' and user.borrowed_books_ids:
            # Surenkame knygų pavadinimus, kad UI galėtų juos parodyti
            borrowed_titles = []
            for b_id in user.borrowed_books_ids:
                book = self.book_manager.get_book_by_id(b_id)
                if book:
                    borrowed_titles.append(book.title)
                else:
                    borrowed_titles.append(f"Nežinoma knyga ({b_id})")
            
            return False, borrowed_titles

        # 2. Jei skolų nėra, triname per user_manager
        self.user_manager.delete_user_from_db(user)
        return True, "Vartotojas sėkmingai pašalintas."
    
    def get_candidates_lost(self, years_overdue):
        """
        Suranda knygas, kurių grąžimo terminas vėluoja daugiau nei X metų ().
        """
        threshold_date = datetime.now() - timedelta(days=years_overdue * 365)
        lost_book_ids = set() # Naudojame aibę, kad nesikartotų
        
        # 1. Einame per vartotojus ir ieškome senų skolų
        for user in self.user_manager.users:
            if user.role == 'reader':
                for loan in user.active_loans:
                    try:
                        due_date_obj = datetime.strptime(loan['due_date'], "%Y-%m-%d")
                        # Jei terminas baigėsi seniau nei prieš X metų
                        if due_date_obj < threshold_date:
                            lost_book_ids.add(loan['book_id'])
                    except ValueError:
                        pass
        
        # 2. Pagal surastus ID surenkame tikrus knygų objektus
        candidates = []
        for book_id in lost_book_ids:
            book = self.book_manager.get_book_by_id(book_id)
            if book:
                candidates.append(book)
                
        return candidates
    
    def get_advanced_statistics(self):
        """
        Surenka išplėstinę statistiką apie žanrus ir vėlavimus.
        Grąžina žodyną (dict) su rodikliais.
        """
        stats = {}
        
        # 1. KOKIŲ KNYGŲ YRA DAUGIAUSIAI (Pagal Inventorių)
        all_genres = [b.genre for b in self.book_manager.books]
        if all_genres:
            # Counter automatiškai suskaičiuoja pasikartojimus
            genre_counts = Counter(all_genres)
            # Paimame patį populiariausią (grąžina sąrašą [(Elementas, Kiekis)])
            top_genre, count = genre_counts.most_common(1)[0]
            stats['inventory_top_genre'] = f"{top_genre} ({count} vnt.)"
        else:
            stats['inventory_top_genre'] = "Nėra duomenų"

        # 2. POPULIARIAUSIAS ŽANRAS TARP SKAITYTOJŲ (Pagal aktyvias paskolas)
        borrowed_genres = []
        total_overdue_books = 0
        reader_count = 0
        
        today = datetime.now().date()
        
        # Einame per visus skaitytojus
        for user in self.user_manager.users:
            if user.role == 'reader':
                reader_count += 1
                for loan in user.active_loans:
                    # Surandame knygą, kad sužinotume jos žanrą
                    book = self.book_manager.get_book_by_id(loan['book_id'])
                    if book:
                        borrowed_genres.append(book.genre)
                    
                    # Tikriname vėlavimą statistikai
                    try:
                        due_obj = datetime.strptime(loan['due_date'], "%Y-%m-%d").date()
                        if due_obj < today:
                            total_overdue_books += 1
                    except ValueError:
                        pass
        
        if borrowed_genres:
            loan_counts = Counter(borrowed_genres)
            top_borrowed, b_count = loan_counts.most_common(1)[0]
            stats['borrowed_top_genre'] = f"{top_borrowed} ({b_count} skolinimai)"
        else:
            stats['borrowed_top_genre'] = "Nėra aktyvių skolinimų"

        # 3. VIDUTINIS VĖLUOJANČIŲ KNYGŲ KIEKIS (Vienam skaitytojui)
        if reader_count > 0:
            avg_overdue = total_overdue_books / reader_count
            stats['avg_overdue_per_reader'] = f"{avg_overdue:.2f}"
        else:
            stats['avg_overdue_per_reader'] = "0.00"
            
        # 4. BIBLIOTEKOS "AMŽIUS" (Vidutiniai leidimo metai)
        years = [int(b.year) for b in self.book_manager.books if isinstance(b.year, int) or str(b.year).isdigit()]
        if years:
            avg_year = sum(years) / len(years)
            stats['avg_book_year'] = f"{int(avg_year)} metai"
        else:
            stats['avg_book_year'] = "-"

        return stats