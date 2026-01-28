"""
FILE: src/services/auth_service.py
PURPOSE: Valdo vartotojų registraciją ir prisijungimą (Autentifikaciją).
RELATIONSHIPS:
  - Importuoja User modelį iš src/models.py.
  - Naudoja UserRepository duomenų tikrinimui ir saugojimui.
CONTEXT:
  - Refaktorizuota: Naudoja vieningą 'User' modelį vietoje 'Librarian'/'Reader'.
"""

from src.models import User
from src.utils import generate_card_id

class AuthService:
    def __init__(self, user_repository):
        self.repo = user_repository

    def _validate_card_format(self, card_id):
        """Patikrina, ar kodas atitinka formatą XX1111."""
        card_id = card_id.upper()
        if len(card_id) != 6:
            return False, "Kodas turi būti lygiai 6 simbolių ilgio."
        if not card_id[:2].isalpha():
            return False, "Pirmieji du simboliai turi būti raidės (pvz. AB)."
        if not card_id[2:].isdigit():
            return False, "Paskutiniai 4 simboliai turi būti skaičiai (pvz. 1234)."
        return True, ""
    
    def authenticate_librarian(self, username, password):
        """Tikrina vartotojo duomenis ir ar jis yra bibliotekininkas."""
        user = self.repo.get_by_username(username)
        
        if not user:
            return None
        
        # Tikriname rolę
        if user.role != 'librarian':
            return None
            
        # Tikriname slaptažodį (paprastas tekstas mokymosi tikslais)
        if user.password == password:
            return user
            
        return None

    def register_librarian(self, username, password):
        """Registruoja naują administratorių."""
        if self.repo.get_by_username(username):
            return False 
        
        # Kuriame User objektą su role 'librarian'
        new_admin = User(
            username=username, 
            role='librarian', 
            password=password
        )
        self.repo.add(new_admin)
        return True

    def register_reader(self, username, card_id):
        """Registruoja skaitytoją."""
        card_id = card_id.strip().upper()

        is_valid, error_msg = self._validate_card_format(card_id)
        if not is_valid:
            return False, error_msg

        if self.repo.get_by_id(card_id):
            return False, f"Kortelė {card_id} jau užregistruota sistemoje."

        # Kuriame User objektą su role 'reader'
        new_reader = User(
            id=card_id,
            username=username,
            role="reader"
        )
        self.repo.add(new_reader)
        
        return True, f"Skaitytojas '{username}' sukurtas. Kortelė: {card_id}"
    
    def regenerate_card_id(self, reader, new_card_id):
        """Pakeičia vartotojo kortelės ID (Primary Key keitimas)."""
        new_card_id = new_card_id.strip().upper()

        is_valid, error_msg = self._validate_card_format(new_card_id)
        if not is_valid:
            return False, error_msg

        existing_user = self.repo.get_by_id(new_card_id)
        if existing_user:
            return False, f"Klaida: Kortelė {new_card_id} jau užimta."
        
        # DB atveju PK keitimas yra sudėtingas. 
        # Paprasčiau: sukurti naują userį, perkelti paskolas, ištrinti seną.
        # ARBA tiesiog atnaujinti ID (SQLAlchemy tai leidžia, jei DB palaiko CASCADE).
        try:
            old_id = reader.id
            reader.id = new_card_id
            self.repo.update(reader)
            return True, f"Kortelė pakeista. {old_id} -> {new_card_id}"
        except Exception as e:
            return False, f"Klaida keičiant ID: {e}"