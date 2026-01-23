"""
FILE: src/repositories/user_repository.py
PURPOSE: Valdo vartotojų ir jų skolų duomenų mainus su SQLite.
RELATIONSHIPS:
  - Jungiasi su lentelėmis 'users' ir 'loans'.
  - Atkuria sudėtingą Reader objektą su active_loans sąrašu.
CONTEXT:
  - Svarbus pokytis: active_loans generuojamas dinamiškai per SQL JOIN.
"""

import sqlite3
from typing import List, Optional
from src.database import get_connection
from src.models import User, Reader, Librarian

class UserRepository:
    def __init__(self):
        pass

    def _fetch_active_loans(self, user_id: str) -> List[dict]:
        """
        Pagalbinis metodas: Suranda visas vartotojo aktyvias paskolas.
        Grąžina sąrašą žodynų, kokio tikisi Reader klasė (su title, due_date ir t.t.).
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # JOIN operacija: mums reikia knygos pavadinimo iš books lentelės
            cursor.execute('''
                SELECT l.book_id, l.due_date, b.title, b.author
                FROM loans l
                LEFT JOIN books b ON l.book_id = b.id
                WHERE l.user_id = ?
            ''', (user_id,))
            
            rows = cursor.fetchall()
            loans = []
            for row in rows:
                loans.append({
                    "book_id": row['book_id'],
                    "title": row['title'] if row['title'] else "Ištrinta knyga", # Apsauga jei knyga ištrinta
                    "due_date": row['due_date']
                })
            return loans
        finally:
            conn.close()

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """
        Konvertuoja DB eilutę į atitinkamą User objektą (Reader arba Librarian).
        """
        role = row['role']
        if role == 'librarian':
            return Librarian(
                id=row['id'],
                username=row['username'],
                role='librarian',
                password=row['password']
            )
        elif role == 'reader':
            # Skaitytojui reikia papildomai užkrauti skolas
            user = Reader(
                id=row['id'],
                username=row['username'],
                role='reader'
            )
            # Čia yra "brangi" operacija, nes kiekvienam vartotojui darome papildomą užklausą.
            # Didelėse sistemose tai optimizuojama, bet čia to pakaks.
            user.active_loans = self._fetch_active_loans(user.id)
            return user
        else:
            # Fallback
            return User(id=row['id'], username=row['username'], role=role)

    def get_all(self) -> List[User]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, user_id: str) -> Optional[User]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row)
            return None
        finally:
            conn.close()

    def get_by_username(self, username: str) -> Optional[User]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Case-insensitive paieška
            cursor.execute("SELECT * FROM users WHERE LOWER(username) = ?", (username.lower(),))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row)
            return None
        finally:
            conn.close()

    def add(self, user: User):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            password = getattr(user, 'password', None) # Tik admin turi slaptažodį
            cursor.execute('''
                INSERT INTO users (id, username, role, password)
                VALUES (?, ?, ?, ?)
            ''', (user.id, user.username, user.role, password))
            conn.commit()
        finally:
            conn.close()

    def remove(self, user):
        """
        Ištrina vartotoją. 
        Svarbu: DB turėtų turėti CASCADE delete, arba pirma reikia ištrinti loans.
        """
        user_id = user.id if hasattr(user, 'id') else user
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Pirmiausia ištriname skolas (jei SQL nėra ON DELETE CASCADE)
            cursor.execute("DELETE FROM loans WHERE user_id = ?", (str(user_id),))
            # Tada vartotoją
            cursor.execute("DELETE FROM users WHERE id = ?", (str(user_id),))
            conn.commit()
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False
        finally:
            conn.close()
            
    def save(self):
        """
        Dummy metodas suderinamumui.
        """
        pass
        
    def update_user_details(self, user: User):
        """
        Atnaujina vardą ar slaptažodį.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            password = getattr(user, 'password', None)
            cursor.execute('''
                UPDATE users SET username=?, password=? WHERE id=?
            ''', (user.username, password, user.id))
            conn.commit()
        finally:
            conn.close()

    # Imitacija senam kodui
    @property
    def users(self):
        return self.get_all()
    
    def add_loan(self, user_id: str, book_id: str, due_date: str):
        """
        NAUJAS: Įrašo naują skolinimo faktą į 'loans' lentelę.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO loans (user_id, book_id, due_date)
                VALUES (?, ?, ?)
            ''', (user_id, book_id, due_date))
            conn.commit()
            return True
        except Exception as e:
            print(f"Loan Error: {e}")
            return False
        finally:
            conn.close()

    def remove_loan(self, user_id: str, book_id: str):
        """
        NAUJAS: Ištrina įrašą iš 'loans' lentelės (knygos grąžinimas).
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Triname konkretų skolinimą.
            # DĖMESIO: Jei vartotojas turi kelias vienodas knygas (kas neturėtų būti leidžiama),
            # LIMIT 1 užtikrintų, kad ištrintume tik vieną. SQLite DELETE LIMIT palaikymas priklauso nuo kompiliavimo.
            # Paprastumo dėlei darome prielaidą, kad (user_id, book_id) pora unikali.
            cursor.execute('''
                DELETE FROM loans 
                WHERE user_id = ? AND book_id = ?
            ''', (user_id, book_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Return Error: {e}")
            return False
        finally:
            conn.close()