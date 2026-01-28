"""
FILE: src/services/stats_service.py
PURPOSE: Generuoja statistines ataskaitas.
RELATIONSHIPS:
  - Naudoja Repozitorijas duomenų gavimui.
CONTEXT:
  - Pritaikyta SQLAlchemy objektų struktūrai.
"""

from datetime import datetime, timedelta
from collections import Counter
from src.config import DATE_FORMAT

class StatsService:
    def __init__(self, book_repo, user_repo):
        self.book_repo = book_repo # Pervadinta iš book_manager
        self.user_repo = user_repo # Pervadinta iš user_manager

    def get_all_overdue_report(self):
        overdue_report = []
        today = datetime.now().date()
        
        # Gauname visus vartotojus su jų paskolomis
        users = self.user_repo.get_all()
        
        for user in users:
            if user.role == 'reader':
                for loan in user.loans: # user.loans dabar yra objektų sąrašas
                    try:
                        # loan.due_date yra string (YYYY-MM-DD)
                        due = datetime.strptime(loan.due_date, DATE_FORMAT).date()
                        if due < today:
                            overdue_report.append({
                                "title": loan.title, # Naudojame tašką, ne ['key']
                                "user": user.username,
                                "due_date": loan.due_date
                            })
                    except (ValueError, TypeError):
                        pass
        return overdue_report

    def get_lost_books_candidates(self, years_overdue):
        threshold_date = datetime.now() - timedelta(days=years_overdue * 365)
        lost_book_ids = set()
        
        users = self.user_repo.get_all()
        
        for user in users:
            for loan in user.loans:
                try:
                    due_date_obj = datetime.strptime(loan.due_date, DATE_FORMAT)
                    if due_date_obj < threshold_date:
                        lost_book_ids.add(loan.book_id)
                except (ValueError, TypeError):
                    pass
        
        candidates = []
        for book_id in lost_book_ids:
            book = self.book_repo.get_by_id(book_id)
            if book:
                candidates.append(book)
        return candidates

    def get_advanced_statistics(self):
        stats = {}
        
        all_books = self.book_repo.get_all()
        all_genres = [b.genre for b in all_books if b.genre]
        
        if all_genres:
            top_genre, count = Counter(all_genres).most_common(1)[0]
            stats['inventory_top_genre'] = f"{top_genre} ({count} vnt.)"
        else:
            stats['inventory_top_genre'] = "Nėra duomenų"

        # Skolinimosi statistika
        borrowed_genres = []
        total_overdue_books = 0
        reader_count = 0
        today = datetime.now().date()
        
        users = self.user_repo.get_all()
        
        for user in users:
            if user.role == 'reader':
                reader_count += 1
                for loan in user.loans:
                    # Kadangi loan objektas turi book_id, galime rasti knygą
                    book = self.book_repo.get_by_id(loan.book_id)
                    if book and book.genre:
                        borrowed_genres.append(book.genre)
                    
                    try:
                        due_obj = datetime.strptime(loan.due_date, DATE_FORMAT).date()
                        if due_obj < today:
                            total_overdue_books += 1
                    except (ValueError, TypeError):
                        pass
        
        if borrowed_genres:
            top_borrowed, b_count = Counter(borrowed_genres).most_common(1)[0]
            stats['borrowed_top_genre'] = f"{top_borrowed} ({b_count} skolinimai)"
        else:
            stats['borrowed_top_genre'] = "-"

        if reader_count > 0:
            avg = total_overdue_books / reader_count
            stats['avg_overdue_per_reader'] = f"{avg:.2f}"
        else:
            stats['avg_overdue_per_reader'] = "0.00"
            
        years = [int(b.year) for b in all_books if b.year]
        if years:
            avg_year = sum(years) / len(years)
            stats['avg_book_year'] = f"{int(avg_year)} metai"
        else:
            stats['avg_book_year'] = "-"

        return stats