from secrets import choice
import sys
from src.library import Library
from src.ui.librarian import main_menu as librarian_ui
from src.ui.reader import main_menu as reader_ui
from src.ui.common import pause, print_header, clear_screen

# Sukuriame bibliotekos egzempliorių (vieną kartą visai programai)
library = Library()

def bootstrap_system():
    """Užtikrina, kad sistemoje yra bent vienas administratorius."""
    admins = [u for u in library.user_manager.users if u.role == 'librarian']
    if not admins:
        print("Pirmas paleidimas: Kuriamas 'admin'.")
        library.user_manager.register_librarian("admin", "admin")
        print("Prisijungimas -> Vartotojas: admin, Slaptažodis: admin")

def main():
    bootstrap_system()
    
    while True:
        clear_screen()
        print_header("BIBLIOTEKOS SISTEMA")
        print("1. Bibliotekininko prisijungimas")
        print("2. Skaitytojo prisijungimas")
        print("3. Išeiti")
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            username = input("Vartotojas: ")
            password = input("Slaptažodis: ")
            user = library.user_manager.authenticate_librarian(username, password)
            
            if user:
                # Kviečiame per naują importo vardą
                librarian_ui.run_menu(library, user) 
            else:
                print("Klaida: Neteisingi duomenys.")

        elif choice == '2':
            card_id = input("Įveskite Kortelės ID: ")
            user = library.user_manager.get_user_by_id(card_id)
            
            if user and user.role == 'reader':
                # Perduodame valdymą į reader modulį
                reader_ui.run_menu(library, user)
            else:
                print("Klaida: Kortelė nerasta arba neteisingas ID.")
                pause()

        elif choice == '3':
            clear_screen()
            print("Viso gero!")
            sys.exit()
        
        else:
            print("Neteisingas pasirinkimas.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma nutraukta.")