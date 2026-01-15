"""
FILE: src/repositories/user_repository.py
PURPOSE: Atsakingas UŽ VARTOTOJŲ duomenų skaitymą ir įrašymą į JSON failą.
RELATIONSHIPS:
  - Naudoja src/data_manager.py fiziniam failo atidarymui.
  - Konvertuoja duomenis tarp JSON žodynų (dict) ir Python objektų (User/Librarian).
CONTEXT:
  - Tai yra "Duomenų prieigos sluoksnis" (Data Access Layer).
  - Jokia verslo logika (pvz., "ar slaptažodis teisingas?") čia neturi būti.
"""

from src.models import Librarian, Reader
from src.data_manager import load_data, save_data, get_data_file_path
from src.config import USERS_FILENAME

class UserRepository:
    def __init__(self):
        """
        Konstruktorius: Pasileidžia sukuriant objektą.
        Jo tikslas - paruošti kelią iki failo ir užkrauti duomenis į atmintį.
        """
        self.filepath = get_data_file_path(USERS_FILENAME)
        self._load() # Iškart užkrauname duomenis

    def _load(self):
        """
        Pagalbinis (privatus) metodas.
        Nuskaito 'raw' JSON duomenis ir paverčia juos į protingus Python objektus.
        """
        data = load_data(self.filepath) # Gauname paprastą sąrašą žodynų (list of dicts)
        self.users = []
        
        # Svarbus žingsnis: Deserializacija (JSON -> Object)
        # Turime atskirti, kokį objektą kurti pagal 'role' lauką.
        for item in data:
            if item.get('role') == 'librarian':
                self.users.append(Librarian.from_dict(item))
            elif item.get('role') == 'reader':
                self.users.append(Reader.from_dict(item))

    def save(self):
        """
        Išsaugo visus atmintyje esančius pakeitimus atgal į failą.
        Tai vadinama Serializacija (Object -> JSON).
        """
        # List comprehension - trumpas būdas sukurti naują sąrašą
        data = [user.to_dict() for user in self.users]
        save_data(self.filepath, data)

    # --- CRUD Operacijos (Create, Read, Update, Delete) ---

    def get_all(self):
        """Grąžina visų vartotojų sąrašą."""
        return self.users

    def get_by_id(self, user_id):
        """Suranda vartotoją pagal ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_by_username(self, username):
        """Suranda vartotoją pagal vardą (didžiosios/mažosios raidės nesvarbu)."""
        for user in self.users:
            if user.username.lower() == username.lower():
                return user
        return None

    def add(self, user):
        """Prideda naują vartotoją į sąrašą ir iškart išsaugo failą."""
        self.users.append(user)
        self.save()

    def remove(self, user):
        """Ištrina vartotoją, jei toks yra."""
        if user in self.users:
            self.users.remove(user)
            self.save()
            return True
        return False