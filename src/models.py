import uuid
from datetime import datetime

# --- Knygos Modelis ---

class Book:
    """
    Klasė, aprašanti vieną konkrečią knygą bibliotekoje.
    """
    def __init__(self, title, author, year, genre, is_borrowed=False, due_date=None, borrower_id=None, book_id=None):
        """
        Inicijuoja knygos objektą.
        
        Parametrai:
        - book_id: Jei nuskaitome iš failo, paduodame esamą ID. Jei kuriame naują, paliekame None.
        - title, author, year, genre: Knygos informacija.
        - is_borrowed: Ar knyga šiuo metu pas kažką yra (True/False).
        - due_date: Iki kada knygą reikia grąžinti (tekstas 'YYYY-MM-DD').
        - borrower_id: Vartotojo ID, kuris turi šią knygą.
        """
        # Generuojame unikalų ID. 
        # uuid.uuid4() sukuria atsitiktinį, unikalų kodą (pvz., '550e8400-e29b...').
        # Tai užtikrina, kad net ir knygos vienodais pavadinimais turės skirtingus ID.
        self.id = book_id if book_id else str(uuid.uuid4())
        
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        
        self.is_borrowed = is_borrowed
        self.due_date = due_date       
        self.borrower_id = borrower_id 

    def __str__(self):
        """
        Specialus Python metodas. Kai kviečiame print(knyga), suveikia šis kodas.
        Grąžina gražiai suformatuotą tekstą atvaizdavimui konsolėje.
        """
        status = f"Paimta (Iki {self.due_date})" if self.is_borrowed else "Laisva"
        return f"[{self.year}] '{self.title}' - {self.author} ({self.genre}) | {status}"

    def to_dict(self):
        """
        PAVERTIMAS Į ŽODYNĄ (Serialization).
        
        Kadangi negalime tiesiogiai įrašyti Python objekto į JSON failą,
        turime jį paversti į standartinį žodyną (dictionary).
        
        Grąžina:
        - dict: žodynas su visais knygos duomenimis.
        """
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

    @classmethod
    def from_dict(cls, data):
        """
        ATKŪRIMAS IŠ ŽODYNO (Deserialization).
        
        Šis metodas gauna duomenis iš JSON failo (kaip žodyną) ir sukuria
        naują Book objektą.
        
        @classmethod reiškia, kad metodas kviečiamas ne konkrečiam objektui, 
        o pačiai klasei (pvz., Book.from_dict(...)).
        
        Parametrai:
        - data: žodynas su knygos informacija.
        """
        return cls(
            book_id=data["id"],          # Atstatome tą patį ID
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
    """
    Bazinė vartotojo klasė.
    Tiek bibliotekininkas, tiek skaitytojas turės vardą ir ID.
    """
    def __init__(self, username, role, user_id=None):
        # Jei ID nepaduotas, generuojame naują
        self.id = user_id if user_id else str(uuid.uuid4())
        self.username = username
        self.role = role # 'admin' arba 'reader'

    def to_dict(self):
        """
        Paverčia bazinius vartotojo duomenis į žodyną.
        Vaikinės klasės (Librarian/Reader) naudos šį metodą savo duomenims papildyti.
        """
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

class Librarian(User):
    """
    Bibliotekininkas.
    Paveldi viską iš User, bet papildomai turi slaptažodį.
    """
    def __init__(self, username, password, user_id=None):
        # Kviečiame tėvinės klasės (User) __init__ metodą
        super().__init__(username, role="librarian", user_id=user_id)
        self.password = password

    def to_dict(self):
        # Pirmiausia gauname bazinį žodyną iš tėvinės klasės
        data = super().to_dict() 
        # Pridedame bibliotekininko specifinį lauką
        data["password"] = self.password 
        return data

    @classmethod
    def from_dict(cls, data):
        # Sukuriame Librarian objektą iš duomenų
        return cls(
            user_id=data["id"],
            username=data["username"],
            password=data["password"]
        )

class Reader(User):
    """
    Skaitytojas.
    Paveldi iš User, bet turi pasiimtų knygų sąrašą.
    """
    def __init__(self, username, user_id=None, borrowed_books_ids=None):
        super().__init__(username, role="reader", user_id=user_id)
        
        # Jei sąrašas nepaduotas, sukuriame tuščią.
        # Saugome tik ID, kad JSON failas būtų paprastesnis ir neužciklintume duomenų.
        if borrowed_books_ids is None:
            borrowed_books_ids = []
        self.borrowed_books_ids = borrowed_books_ids

    def to_dict(self):
        data = super().to_dict()
        # Pridedame specifinį lauką - knygų ID sąrašą
        data["borrowed_books_ids"] = self.borrowed_books_ids
        return data

    @classmethod
    def from_dict(cls, data):
        # .get() metodas saugus - jei rakto nėra, grąžins tuščią sąrašą []
        return cls(
            user_id=data["id"],
            username=data["username"],
            borrowed_books_ids=data.get("borrowed_books_ids", [])
        )