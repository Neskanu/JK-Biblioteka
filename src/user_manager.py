import os
from src.models import Librarian, Reader
from src.data_manager import load_data, save_data
from src.utils import generate_card_id
from src.data_manager import load_data, save_data, get_data_file_path

# ... (kelio nustatymas) ...
DATA_FILE = get_data_file_path('users.json')

class UserManager:
    def __init__(self):
        data = load_data(DATA_FILE)
        self.users = []
        
        # Svarbi dalis: turime atskirti, kokį objektą kurti (Bibliotekininką ar Skaitytoją)
        for item in data:
            if item['role'] == 'librarian':
                self.users.append(Librarian.from_dict(item))
            elif item['role'] == 'reader':
                self.users.append(Reader.from_dict(item))

    def save(self):
        data = [user.to_dict() for user in self.users]
        save_data(DATA_FILE, data)

    def register_reader(self, username):
        """Registruoja naują skaitytoją su trumpu ID."""
        
        # Generuojame unikalų ID
        # Ciklas while užtikrina, kad jei netyčia sugeneruotume egzistuojantį (labai maža tikimybė),
        # bandytume dar kartą.
        while True:
            new_card_id = generate_card_id()
            if not self.get_user_by_id(new_card_id): # Jei tokio ID dar nėra
                break
        
        # Kuriame objektą su MŪSŲ sugeneruotu ID
        new_reader = Reader(username, user_id=new_card_id)
        
        self.users.append(new_reader)
        self.save()
        return new_reader

    def register_librarian(self, username, password):
        if self.get_user_by_username(username):
            return None
            
        new_admin = Librarian(username, password)
        self.users.append(new_admin)
        self.save()
        return new_admin

    def authenticate_librarian(self, username, password):
        """Tikrina prisijungimo duomenis."""
        user = self.get_user_by_username(username)
        # Tikriname ar vartotojas yra, ar jis bibliotekininkas ir ar tinka slaptažodis
        if user and user.role == 'librarian' and user.password == password:
            return user
        return None

    def get_user_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None
        
    def get_user_by_username(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def delete_user(self, user):
        """Pašalina vartotoją iš sistemos."""
        if user in self.users:
            self.users.remove(user)
            self.save()
            return True
        return False
    
    def regenerate_reader_id(self, user):
        """
        Sugeneruoja naują kortelę skaitytojui, priskiria ją ir išsaugo.
        Grąžina naująjį ID.
        """
        while True:
            new_card_id = generate_card_id()
            if not self.get_user_by_id(new_card_id): # Jei tokio ID dar nėra
                break
                
        # Galima pridėti while ciklą unikalumui, kaip darėme registracijoje
        user.id = new_card_id
        self.save()
        return new_card_id

    def update_librarian(self, user, new_username=None, new_password=None):
        """Atnaujina bibliotekininko duomenis."""
        if new_username:
            # !TODO! Čia REIKIA pridėti patikrinimą, ar vardas neužimtas!!!
            user.username = new_username
        if new_password:
            user.password = new_password
        self.save()

    def delete_user_from_db(self, user):
        """
        Fiziškai pašalina vartotoją iš sąrašo ir failo.
        Šį metodą kvies Library klasė po saugumo patikrinimų.
        """
        if user in self.users:
            self.users.remove(user)
            self.save()
            return True
        return False   
        