"""
FILE: src/services/auth_service.py
PURPOSE: Verslo logika vartotojų autentifikacijai.
RELATIONSHIPS:
  - Naudoja src/repositories/user_repository.py.
CONTEXT:
  - Pakeista: Pridėtas 'authenticate_reader' metodas jungimuisi pagal ID.
"""

from src.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repository: UserRepository = None):
        self.user_repo = user_repository or UserRepository()

    def authenticate_admin(self, username, password):
        """
        Autentifikacija Bibliotekininkams (Vardas + Slaptažodis).
        """
        user = self.user_repo.get_by_username(username)
        
        if user and user.role == 'librarian':
            if user.password == password:
                return user
        return None

    def authenticate_reader(self, user_id):
        """
        Autentifikacija Skaitytojams (Tik ID).
        """
        # Ieškome tiesiogiai pagal ID (User.id)
        user = self.user_repo.get_by_id(user_id)
        
        if user and user.role == 'reader':
            return user
        return None

    # Paliekame seną metodą suderinamumui (jei dar kur nors naudojamas), 
    # bet viduje nukreipiame logiką.
    def authenticate(self, username, password=None):
        if password:
            return self.authenticate_admin(username, password)
        # Jei nėra slaptažodžio, manome, kad tai bandymas jungtis kaip skaitytojui,
        # bet čia 'username' kintamasis iš tikrųjų turės ID reikšmę.
        return self.authenticate_reader(username)

    def register_user(self, username, password, role='reader'):
        if self.user_repo.get_by_username(username):
            return False, "Vartotojas tokiu vardu jau egzistuoja."
            
        from src.models import User
        new_user = User(username=username, password=password, role=role)
        
        try:
            self.user_repo.add(new_user)
            # Grąžiname ID, kad vartotojas žinotų su kuo jungtis
            return True, f"Vartotojas sukurtas. Jūsų ID prisijungimui: {new_user.id}"
        except Exception as e:
            return False, f"Klaida: {str(e)}"

    def register_reader(self, username, card_id=None):
        # card_id argumentas čia ignoruojamas kuriant (nes ID generuojamas automatiškai UUID),
        # nebent norite leisti pasirinkti savo ID.
        # Paprastumo dėlei leidžiame sistemai sugeneruoti ID.
        return self.register_user(username=username, password=None, role='reader')

    def register_librarian(self, username, password):
        return self.register_user(username=username, password=password, role='librarian')