"""
FILE: src/models.py
PURPOSE: Apibrėžia programos duomenų struktūras (Modelius).
CONTEXT:
  - Naudojame modernią Python biblioteką 'dataclasses'.
  - Tai leidžia išvengti daug pasikartojančio kodo (boilerplate), kurį
    tekdavo rašyti senesnėse Python versijose (pvz., __init__ metodus).
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any

# @dataclass yra "dekoratorius". Jis automatiškai sugeneruoja klasei metodus:
# __init__() - konstruktorių
# __repr__() - gražų atvaizdavimą spausdinant (print)
# __eq__() - objektų palyginimą
@dataclass
class Book:
    """
    Modelis, atstovaujantis vieną knygą.
    """
    # Type Hinting (Tipų sufleriai): 'title: str' sako, kad laukas turi būti tekstas.
    # Tai netikrina tipų vykdymo metu, bet padeda programuotojams ir IDE.
    title: str
    author: str
    year: int
    genre: str
    
    # Numatomosios reikšmės (Default values):
    # Jei kuriant objektą nenurodysime šių reikšmių, jos bus lygios 1.
    total_copies: int = 1
    available_copies: int = 1
    
    # field(default_factory=...) naudojame, kai norime dinaminės numatytosios reikšmės.
    # Jei rašytume tiesiog 'id: str = str(uuid.uuid4())', visiems objektams ID būtų tas pats!
    # Lambda funkcija užtikrina, kad kaskart kuriant naują knygą, sugeneruojamas NAUJAS kodas.
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Vartotojui draugiškas atvaizdavimas (naudojamas spausdinant meniu)."""
        return f"{self.title} - {self.author} | Laisva: {self.available_copies}/{self.total_copies}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializacija: Objektas -> Žodynas (dict).
        Reikalinga, norint išsaugoti duomenis į JSON failą.
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """
        Deserializacija: Žodynas -> Objektas.
        Reikalinga, skaitant duomenis iš JSON failo.
        """
        return cls(
            title=data["title"],
            author=data["author"],
            year=int(data["year"]), # Užtikriname, kad metai būtų skaičius
            genre=data["genre"],
            total_copies=data.get("total_copies", 1),
            available_copies=data.get("available_copies", 1),
            id=data.get("id", str(uuid.uuid4())) # Jei JSON faile nėra ID, sukuriame naują
        )

# --- Vartotojų Modeliai ---

@dataclass
class User:
    """
    Bazinė vartotojo klasė.
    Kitos klasės (Librarian, Reader) paveldės šiuos laukus.
    """
    username: str
    role: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

@dataclass
class Librarian(User):
    """
    Bibliotekininkas (Admin).
    Paveldi 'username', 'role' ir 'id' iš User klasės.
    """
    password: str = ""

    def __post_init__(self):
        """
        Šis specialus metodas dataclasses veikia KAIP konstruktoriaus pabaiga.
        Čia mes 'kietai' nustatome rolę, kad ji visada būtų 'librarian'.
        """
        self.role = "librarian"

    def to_dict(self) -> Dict[str, Any]:
        # Paimame bazinį žodyną iš tėvinės klasės (User)
        data = super().to_dict()
        # Pridedame specifinį lauką
        data["password"] = self.password
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Librarian':
        return cls(
            id=data["id"],
            username=data["username"],
            role="librarian",
            password=data["password"]
        )

@dataclass
class Reader(User):
    """
    Skaitytojas.
    Turi papildomą sąrašą 'active_loans' pasiskolintoms knygoms.
    """
    # DĖMESIO: Sąrašams (list) negalima naudoti 'active_loans = []', nes tada
    # visi skaitytojai dalinsis TUO PAČIU sąrašu (Python nuorodų specifika).
    # field(default_factory=list) sukuria naują tuščią sąrašą kiekvienam objektui.
    active_loans: List[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        self.role = "reader"

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["active_loans"] = self.active_loans
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reader':
        return cls(
            id=data["id"],
            username=data["username"],
            role="reader",
            active_loans=data.get("active_loans", [])
        )