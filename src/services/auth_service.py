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

    def _validate_card_format(self, card_id):
        """
        Pagalbinis metodas: Patikrina, ar kodas atitinka formatą XX1111.
        Grąžina: (bool, error_message)
        """
        card_id = card_id.upper()
        
        # 1. Ilgio patikra
        if len(card_id) != 6:
            return False, "Kodas turi būti lygiai 6 simbolių ilgio."
            
        # 2. Pirmų dviejų simbolių patikra (turi būti raidės)
        if not card_id[:2].isalpha():
            return False, "Pirmieji du simboliai turi būti raidės (pvz. AB)."
            
        # 3. Paskutinių keturių simbolių patikra (turi būti skaičiai)
        if not card_id[2:].isdigit():
            return False, "Paskutiniai 4 simboliai turi būti skaičiai (pvz. 1234)."
            
        return True, ""
    
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
        
        new_admin = Librarian(username, role='librarian', password=password)
        self.repo.add(new_admin)
        return True

    def register_reader(self, username, card_id):
        """
        Registruoja skaitytoją su bibliotekininko įvestu ID.
        """
        # Normalizuojame į didžiąsias raides
        card_id = card_id.strip().upper()

        # 1. Formato validacija
        is_valid, error_msg = self._validate_card_format(card_id)
        if not is_valid:
            return False, error_msg

        # 2. Unikalumo tikrinimas
        if self.repo.get_by_id(card_id):
            return False, f"Kortelė {card_id} jau užregistruota sistemoje."

        # 3. Kūrimas
        new_reader = Reader(username, role="reader", id=card_id)
        self.repo.add(new_reader)
        
        return True, f"Skaitytojas '{username}' sukurtas. Kortelė: {card_id}"
    
    def regenerate_card_id(self, reader, new_card_id):
        """
        Priskiria naują kortelę esamam skaitytojui (RANKINIS ĮVEDIMAS).
        Sena kortelė (reader.id) bus pakeista nauja.
        """
        new_card_id = new_card_id.strip().upper()

        # 1. Formato validacija
        is_valid, error_msg = self._validate_card_format(new_card_id)
        if not is_valid:
            return False, error_msg

        # 2. Unikalumo tikrinimas
        # Svarbu: tikriname, ar kortelė neužimta (išskyrus atvejį, jei tai ta pati kortelė)
        existing_user = self.repo.get_by_id(new_card_id)
        if existing_user and existing_user.id != reader.id:
            return False, f"Klaida: Kortelė {new_card_id} jau priklauso kitam vartotojui."
        
        # 3. Atnaujinimas
        old_id = reader.id
        reader.id = new_card_id
        self.repo.save()
        
        return True, f"Kortelė pakeista. {old_id} -> {new_card_id}"