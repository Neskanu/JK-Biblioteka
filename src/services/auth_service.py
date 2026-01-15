"""
FILE: src/services/auth_service.py
PURPOSE: Valdo vartotojų registraciją ir prisijungimą (Autentifikaciją).
RELATIONSHIPS:
  - Naudoja UserRepository duomenų patikrinimui ir išsaugojimui.
  - Naudoja utils.py ID generavimui.
CONTEXT:
  - Šis modulis atskiria "kaip prisijungti" logiką nuo "kur saugomi duomenys".
"""

from src.models import Librarian, Reader
from src.utils import generate_card_id

class AuthService:
    def __init__(self, user_repository):
        """
        Dependency Injection (Priklausomybių įterpimas):
        Mes paduodame 'user_repository' iš išorės, užuot kūrę jį viduje.
        Tai leidžia lengviau testuoti kodą.
        """
        self.repo = user_repository

    def authenticate_librarian(self, username, password):
        """
        Tikrina, ar vartotojas egzistuoja ir ar tinka slaptažodis.
        """
        user = self.repo.get_by_username(username)
        
        # 1. Ar vartotojas rastas?
        # 2. Ar jo rolė tinkama (admin)?
        if not user or user.role != 'librarian':
            return None
        
        # 3. Slaptažodžio tikrinimas
        # DĖMESIO (Studentams): Realiame pasaulyje slaptažodžių "plain text" (atviru tekstu)
        # saugoti GRIEŽTAI NEGALIMA. Reikia naudoti "hashing" (pvz., bcrypt).
        # Čia darome paprastai tik mokymosi tikslais.
        if user.password == password:
            return user
            
        return None

    def register_librarian(self, username, password):
        """Registruoja naują administratorių."""
        # Patikriname, ar toks vardas jau užimtas
        if self.repo.get_by_username(username):
            return False 
        
        new_admin = Librarian(username, password)
        self.repo.add(new_admin)
        return True

    def register_reader(self, username):
        """
        Registruoja skaitytoją.
        Skaitytojai neturi slaptažodžio, bet turi unikalų Kortelės ID.
        """
        # Generuojame ID tol, kol randame unikalų
        while True:
            new_id = generate_card_id()
            if not self.repo.get_by_id(new_id): # Jei ID laisvas - nutraukiame ciklą
                break
        
        new_reader = Reader(username, user_id=new_id)
        self.repo.add(new_reader)
        return new_reader
        
    def regenerate_card_id(self, reader):
        """Suteikia skaitytojui naują ID (pamestos kortelės atvejis)."""
        while True:
            new_id = generate_card_id()
            if not self.repo.get_by_id(new_id):
                break
        
        # Atnaujiname objektą
        reader.id = new_id
        # Išsaugome pakeitimus į failą per repo
        self.repo.save()
        return new_id