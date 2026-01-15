"""
FILE: src/services/stats_service.py
PURPOSE: Generuoja statistines ataskaitas ir analizę.
RELATIONSHIPS:
  - Naudoja duomenis iš BookManager ir UserManager.
  - Importuoja config nustatymus.
CONTEXT:
  - Analitikos modulis, atskirtas nuo transakcinės logikos.
"""

from datetime import datetime, timedelta
from collections import Counter
from src.config import DATE_FORMAT

class StatsService:
    def __init__(self, book_manager, user_manager):
        self.book_manager = book_manager
        self.user_manager = user_manager

    def get_all_overdue_report(self):
        """
        Generuoja bendrą visų vėluojančių knygų ataskaitą administratoriui.
        """
        overdue_report = []
        today = datetime.now().date()
        
        for user in self.user_manager.users:
            if user.role == 'reader':
                for loan in user.active_loans:
                    try:
                        due = datetime.strptime(loan['due_date'], DATE_FORMAT).date()
                        if due < today:
                            overdue_report.append({
                                "title": loan['title'],
                                "user": user.username,
                                "due_date": loan['due_date']
                            })
                    except ValueError:
                        pass
        return overdue_report

    def get_lost_books_candidates(self, years_overdue):
        """
        Randa knygas, kurios vėluoja daugiau nei X metų (laikomos prarastomis).
        """
        threshold_date = datetime.now() - timedelta(days=years_overdue * 365)
        lost_book_ids = set()
        
        for user in self.user_manager.users:
            if user.role == 'reader':
                for loan in user.active_loans:
                    try:
                        due_date_obj = datetime.strptime(loan['due_date'], DATE_FORMAT)
                        if due_date_obj < threshold_date:
                            lost_book_ids.add(loan['book_id'])
                    except ValueError:
                        pass
        
        # Konvertuojame ID į objektus
        candidates = []
        for book_id in lost_book_ids:
            book = self.book_manager.get_by_id(book_id)
            if book:
                candidates.append(book)
        return candidates

    def get_advanced_statistics(self):
        """
        Surenka ir grąžina "big picture" statistiką.
        """
        stats = {}
        
        # 1. Populiariausias žanras (Inventorius)
        all_genres = [b.genre for b in self.book_manager.books]
        if all_genres:
            top_genre, count = Counter(all_genres).most_common(1)[0]
            stats['inventory_top_genre'] = f"{top_genre} ({count} vnt.)"
        else:
            stats['inventory_top_genre'] = "Nėra duomenų"

        # 2. Skolinimosi statistika
        borrowed_genres = []
        total_overdue_books = 0
        reader_count = 0
        today = datetime.now().date()
        
        for user in self.user_manager.users:
            if user.role == 'reader':
                reader_count += 1
                for loan in user.active_loans:
                    book = self.book_manager.get_by_id(loan['book_id'])
                    if book:
                        borrowed_genres.append(book.genre)
                    
                    try:
                        due_obj = datetime.strptime(loan['due_date'], DATE_FORMAT).date()
                        if due_obj < today:
                            total_overdue_books += 1
                    except ValueError:
                        pass
        
        if borrowed_genres:
            top_borrowed, b_count = Counter(borrowed_genres).most_common(1)[0]
            stats['borrowed_top_genre'] = f"{top_borrowed} ({b_count} skolinimai)"
        else:
            stats['borrowed_top_genre'] = "Nėra aktyvių skolinimų"

        # 3. Vidutiniai rodikliai
        if reader_count > 0:
            avg = total_overdue_books / reader_count
            stats['avg_overdue_per_reader'] = f"{avg:.2f}"
        else:
            stats['avg_overdue_per_reader'] = "0.00"
            
        years = [int(b.year) for b in self.book_manager.books if isinstance(b.year, int)]
        if years:
            avg_year = sum(years) / len(years)
            stats['avg_book_year'] = f"{int(avg_year)} metai"
        else:
            stats['avg_book_year'] = "-"

        return stats