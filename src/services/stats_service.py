"""
FILE: src/services/stats_service.py
PURPOSE: Skaičiuoja bibliotekos statistiką.
RELATIONSHIPS:
  - Inicijuojamas src/library.py.
  - Naudoja book_repository ir user_repository duomenų analizei.
CONTEXT:
  - Perrašyta: Pridėtas universalus datų valdymas (String vs Date objektas).
  - Ištaisyta TypeError klaida lyginant datą su stringu.
"""

from datetime import datetime, date
from collections import Counter

class StatsService:
    def __init__(self, book_repository, user_repository):
        self.book_repo = book_repository
        self.user_repo = user_repository

    def get_advanced_statistics(self):
        """
        Sugeneruoja statistikos žodyną admin UI.
        """
        books = self.book_repo.get_all()
        users = self.user_repo.get_all()
        
        # 1. Populiariausias žanras (Inventory)
        genres = [b.genre for b in books if b.genre]
        top_genre = Counter(genres).most_common(1)
        inventory_top_genre = top_genre[0][0] if top_genre else "Nėra duomenų"

        # 2. Vidutiniai metai
        years = [b.year for b in books if b.year]
        avg_year = int(sum(years) / len(years)) if years else 0

        # 3. Knygų skolinimosi statistika
        active_loans = []
        for u in users:
            active_loans.extend(u.active_loans)
            
        borrowed_genres = []
        for loan in active_loans:
             # Saugiai gauname knygos informaciją
             book = getattr(loan, 'book', None)
             if not book and hasattr(loan, 'book_id'):
                 book = self.book_repo.get_by_id(loan.book_id)
                 
             if book and book.genre:
                 borrowed_genres.append(book.genre)
        
        top_borrowed = Counter(borrowed_genres).most_common(1)
        borrowed_top_genre = top_borrowed[0][0] if top_borrowed else "-"

        # 4. Vėlavimų statistika
        overdue_books = self.get_all_overdue_books()
        overdue_count = len(overdue_books)
        reader_count = len([u for u in users if u.role == 'reader'])
        avg_overdue = round(overdue_count / reader_count, 2) if reader_count > 0 else 0

        return {
            'inventory_top_genre': inventory_top_genre,
            'borrowed_top_genre': borrowed_top_genre,
            'avg_book_year': avg_year,
            'avg_overdue_per_reader': avg_overdue
        }

    def get_all_overdue_books(self):
        """
        Grąžina sąrašą vėluojančių knygų su vartotojo informacija.
        Kviečiamas iš library.get_all_overdue_books().
        """
        overdue_list = []
        users = self.user_repo.get_all()
        
        # Naudojame date objektą palyginimui (ne stringą)
        today = datetime.now().date()

        for user in users:
            for loan in user.active_loans:
                # Normalizuojame datą į datetime.date objektą
                # Tai apsaugo nuo klaidų, jei DB grąžina stringą ARBA date objektą
                loan_due = self._parse_date(loan.due_date)
                
                if loan_due and loan_due < today:
                    # Naudojame saugią prieigą prie atributų
                    title = getattr(loan, 'title', 'Nežinoma knyga')
                    
                    overdue_list.append({
                        "Knyga": title,
                        "Skaitytojas": user.username,
                        "Terminas": str(loan.due_date), # UI rodome originalų formatą
                        "Vėluoja (dienų)": (today - loan_due).days
                    })
        return overdue_list

    def _parse_date(self, date_value):
        """
        Universali funkcija konvertuoti stringą arba datetime į date objektą.
        Apsaugo nuo 'TypeError: < not supported between instances of datetime.date and str'.
        """
        if date_value is None:
            return None
            
        if isinstance(date_value, str):
            try:
                # Bandom parsilinti ISO formatą (YYYY-MM-DD)
                return datetime.strptime(date_value, "%Y-%m-%d").date()
            except ValueError:
                return None
        elif isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, date):
            return date_value
            
        return None

    def _days_overdue(self, due_date_val):
        """Pagalbinė funkcija (jei dar kur nors naudojama tiesiogiai)."""
        d_due = self._parse_date(due_date_val)
        if d_due:
            d_now = datetime.now().date()
            return (d_now - d_due).days
        return 0