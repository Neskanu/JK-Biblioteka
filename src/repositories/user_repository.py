"""
FILE: src/repositories/user_repository.py
PURPOSE: Valdo vartotojų duomenis su PyMySQL.
RELATIONSHIPS:
  - Naudoja src/database.py.
  - Tvarko Users ir Loans lenteles.
"""

from src.database import get_connection
from src.models import Librarian, Reader

class UserRepository:
    def __init__(self):
        self.users = []
        self.refresh_cache()

    def refresh_cache(self):
        self.users = []
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Visi vartotojai
                cursor.execute("SELECT * FROM users")
                users_data = cursor.fetchall()
                
                for u_row in users_data:
                    if u_row['role'] == 'librarian':
                        user = Librarian.from_dict(u_row)
                    else:
                        user = Reader.from_dict(u_row)
                        user.active_loans = []
                        
                        # 2. Paskolos (atskira užklausa)
                        # Galima optimizuoti naudojant vieną didelį JOIN, bet kol kas taip aiškiau
                        cursor.execute("SELECT book_id, title, due_date FROM loans WHERE user_id = %s", (user.id,))
                        loans = cursor.fetchall()
                        
                        for loan in loans:
                            if loan['due_date']:
                                loan['due_date'] = str(loan['due_date'])
                            user.active_loans.append(loan)
                    
                    self.users.append(user)
        finally:
            conn.close()

    def get_all(self):
        return self.users

    def get_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_by_username(self, username):
        for user in self.users:
            if user.username.lower() == username.lower():
                return user
        return None

    def add(self, user):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                pwd = getattr(user, 'password', None)
                sql = "INSERT INTO users (id, username, role, password) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (user.id, user.username, user.role, pwd))
            conn.commit()
            self.users.append(user)
        finally:
            conn.close()

    def save(self):
        """
        Išsaugo vartotojo duomenis ir perrašo paskolas.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                for user in self.users:
                    # 1. Atnaujiname patį vartotoją
                    pwd = getattr(user, 'password', None)
                    cursor.execute(
                        "UPDATE users SET username=%s, password=%s WHERE id=%s",
                        (user.username, pwd, user.id)
                    )
                    
                    # 2. Perrašome paskolas (Skaitytojams)
                    if user.role == 'reader':
                        cursor.execute("DELETE FROM loans WHERE user_id = %s", (user.id,))
                        if user.active_loans:
                            sql_loan = "INSERT INTO loans (user_id, book_id, title, due_date) VALUES (%s, %s, %s, %s)"
                            loan_data = [(user.id, l['book_id'], l['title'], l['due_date']) for l in user.active_loans]
                            cursor.executemany(sql_loan, loan_data)
            conn.commit()
        finally:
            conn.close()

    def remove(self, user):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user.id,))
            conn.commit()
            if user in self.users:
                self.users.remove(user)
            return True
        finally:
            conn.close()