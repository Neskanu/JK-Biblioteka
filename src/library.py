from datetime import datetime, timedelta
from src.book_manager import BookManager
from src.user_manager import UserManager

# Nustatome skolinimo terminą (pvz., 14 dienų)
LOAN_PERIOD_DAYS = 14

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

        overdue_books = []
        today = datetime.now().date() # Gauname šiandienos datą (be laiko)

        # Einame per visas vartotojo turimas knygas (jų ID)
        for book_id in user.borrowed_books_ids:
            book = self.book_manager.get_book_by_id(book_id)
            
            # Jei knyga rasta, ji paskolinta ir turi grąžinimo datą
            if book and book.due_date:
                # Konvertuojame string datą 'YYYY-MM-DD' į tikrą datetime objektą palyginimui
                due_date_obj = datetime.strptime(book.due_date, "%Y-%m-%d").date()
                
                if due_date_obj < today:
                    overdue_books.append(book)
        
        return overdue_books

    def borrow_book(self, user_id, book_id):
        """
        Bando paskolinti knygą vartotojui.
        
        Grąžina tuple: (Success: bool, Message: str)
        Tai leidžia main.py lengvai parodyti vartotojui rezultatą.
        """
        # 1. Gauname objektus
        user = self.user_manager.get_user_by_id(user_id)
        book = self.book_manager.get_book_by_id(book_id)

        # 2. Baziniai patikrinimai
        if not user:
            return False, "Vartotojas nerastas."
        if not book:
            return False, "Knyga nerasta."
        if book.is_borrowed:
            return False, "Knyga jau paimta kito skaitytojo."

        # 3. Vėlavimo patikrinimas (Būtina sąlyga!)
        overdue_list = self.get_user_overdue_books(user_id)
        if len(overdue_list) > 0:
            return False, f"Negalima skolinti! Turite {len(overdue_list)} vėluojančią(-ias) knygą(-as)."

        # 4. Atliekame skolinimą
        # Apskaičiuojame grąžinimo datą
        return_date = datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)
        formatted_date = return_date.strftime("%Y-%m-%d")

        # Atnaujiname knygą
        book.is_borrowed = True
        book.borrower_id = user.id
        book.due_date = formatted_date
        
        # Atnaujiname vartotoją
        user.borrowed_books_ids.append(book.id)

        # 5. Išsaugome abu failus
        self.book_manager.save()
        self.user_manager.save()

        return True, f"Knyga '{book.title}' sėkmingai išduota iki {formatted_date}."

    def return_book(self, user_id, book_id):
        """Grąžina knygą į biblioteką."""
        user = self.user_manager.get_user_by_id(user_id)
        book = self.book_manager.get_book_by_id(book_id)

        if not user or not book:
            return False, "Neteisingi duomenys."

        if book_id not in user.borrowed_books_ids:
            return False, "Šis vartotojas neturi šios knygos."

        # Išvalome knygos duomenis
        book.is_borrowed = False
        book.borrower_id = None
        book.due_date = None

        # Pašaliname iš vartotojo sąrašo
        user.borrowed_books_ids.remove(book_id)

        # Saugome
        self.book_manager.save()
        self.user_manager.save()

        return True, "Knyga sėkmingai grąžinta."

    def get_all_overdue_books(self):
        """Grąžina sąrašą visų bibliotekoje vėluojančių knygų (Adminui)."""
        all_books = self.book_manager.get_all_books()
        overdue = []
        today = datetime.now().strftime("%Y-%m-%d") # Palyginimui kaip string

        for book in all_books:
            if book.is_borrowed and book.due_date and book.due_date < today:
                overdue.append(book)
        return overdue
    
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