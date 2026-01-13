from src.models import Librarian, Reader
from src.data_manager import load_data, save_data

DATA_FILE = 'data/users.json'

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
        """Registruoja naują skaitytoją."""
        # Patikriname, ar vardas neužimtas (nebūtina, bet gera praktika)
        if self.get_user_by_username(username):
            return None # Vartotojas jau yra
            
        new_reader = Reader(username)
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
    
        