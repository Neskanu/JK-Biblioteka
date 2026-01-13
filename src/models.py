import uuid
from datetime import datetime

# --- Knygos Modelis ---
class Book:
    def __init__(self, title, author, year, genre, is_borrowed=False, due_date=None, borrower_id=None, book_id=None):
        # 1. ID Generavimas:
        # Jei užkrauname iš failo, naudojame esamą ID (book_id).
        # Jei kuriame naują, generuojame unikalų UUID.
        self.id = book_id if book_id else str(uuid.uuid4())
        
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        
        # Svarbu: Atsisakiau 'no_of_copies'. Kodėl?
        # Jei turime 5 kopijas, ir viena pasiskolinta, sunku sekti, kuri būtent vėluoja.
        # Paprasčiau: kiekviena fizinė knyga sistemoje yra atskiras įrašas su savo unikaliu ID.
        
        self.is_borrowed = is_borrowed
        self.due_date = due_date       # Saugosime datą kaip string "YYYY-MM-DD" arba None
        self.borrower_id = borrower_id # Čia įrašysime Readerio ID, kuris paėmė knygą

    def __str__(self):
        status = f"Paimta (Iki {self.due_date})" if self.is_borrowed else "Laisva"
        return f"[{self.year}] '{self.title}' - {self.author} ({self.genre}) | {status}"

    # 2. Metodas, skirtas konvertuoti objektą į žodyną (JSON įrašymui)
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "is_borrowed": self.is_borrowed,
            "due_date": self.due_date,
            "borrower_id": self.borrower_id
        }

    # 3. Metodas, skirtas sukurti objektą iš žodyno (JSON nuskaitymui)
    # @classmethod reiškia, kad kviečiame ne ant objekto, o ant klasės: Book.from_dict(...)
    @classmethod
    def from_dict(cls, data):
        return cls(
            book_id=data["id"],
            title=data["title"],
            author=data["author"],
            year=data["year"],
            genre=data["genre"],
            is_borrowed=data["is_borrowed"],
            due_date=data["due_date"],
            borrower_id=data["borrower_id"]
        )

# --- Vartotojų Modeliai ---

class User:
    def __init__(self, username, role, user_id=None):
        self.id = user_id if user_id else str(uuid.uuid4())
        self.username = username
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

class Librarian(User):
    def __init__(self, username, password, user_id=None):
        # Bibliotekininkui reikia slaptažodžio (pagal Bonus reikalavimus)
        super().__init__(username, role="librarian", user_id=user_id)
        self.password = password

    def to_dict(self):
        data = super().to_dict() # Paimame bendrus duomenis
        data["password"] = self.password # Pridedame specifinius
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["id"],
            username=data["username"],
            password=data["password"]
        )

class Reader(User):
    def __init__(self, username, user_id=None, borrowed_books_ids=None):
        super().__init__(username, role="reader", user_id=user_id)
        # Čia saugosime tik ID sąrašą, ne pačius Book objektus.
        # Tai palengvina JSON saugojimą.
        if borrowed_books_ids is None:
            borrowed_books_ids = []
        self.borrowed_books_ids = borrowed_books_ids

    def to_dict(self):
        data = super().to_dict()
        data["borrowed_books_ids"] = self.borrowed_books_ids
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["id"],
            username=data["username"],
            borrowed_books_ids=data.get("borrowed_books_ids", [])
        )