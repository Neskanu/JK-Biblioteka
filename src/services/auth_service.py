"""
FILE: src/services/auth_service.py
PURPOSE: Verslo logika vartotojų autentifikacijai.
RELATIONSHIPS:
  - Naudoja src/repositories/user_repository.py.
CONTEXT:
  - Pakeista: Skaitytojai (reader) autentifikuojami be slaptažodžio.
  - Bibliotekininkai (librarian) privalo įvesti slaptažodį.
"""

from src.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repository: UserRepository = None):
        self.user_repo = user_repository or UserRepository()

    def authenticate(self, username, password=None):
        """
        Patikrina vartotojo duomenis.
        - Jei rolė 'reader': slaptažodis ignoruojamas.
        - Jei rolė 'librarian': slaptažodis privalomas.
        """
        user = self.user_repo.get_by_username(username)
        
        if not user:
            return None
            
        # Logika pagal roles
        if user.role == 'reader':
            # Skaitytojams slaptažodžio nereikia
            return user
            
        elif user.role == 'librarian':
            # Bibliotekininkams slaptažodis būtinas
            if password and user.password == password:
                return user
            
        return None

    def register_user(self, username, password, role='reader'):
        """
        Registruoja naują vartotoją.
        """
        if self.user_repo.get_by_username(username):
            return False, "Vartotojas tokiu vardu jau egzistuoja."
            
        from src.models import User
        # Jei skaitytojas, password gali būti None (arba tuščias string),
        # bet DB reikalauja, kad modelis atitiktų struktūrą.
        new_user = User(username=username, password=password, role=role)
        
        try:
            self.user_repo.add(new_user)
            return True, "Vartotojas sėkmingai sukurtas."
        except Exception as e:
            return False, f"Klaida: {str(e)}"
            
    # Papildomi metodai specifinėms registracijoms (kad atitiktų admin_ui)
    def register_reader(self, username, card_id):
        # Admin UI naudoja kortelės ID, bet sistemoje tai dažnai tiesiog username
        # Arba galime card_id įrašyti į username, arba į password lauką kaip identifikatorių
        return self.register_user(username=username, password=None, role='reader')

    def register_librarian(self, username, password):
        return self.register_user(username=username, password=password, role='librarian')