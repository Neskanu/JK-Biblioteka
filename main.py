from secrets import choice
import sys
from src.library import Library
from src.ui.librarian import main_menu as librarian_ui
from src.ui.reader import main_menu as reader_ui
from src.ui.common import pause, clear_screen
from src.ui.ascii_styler import draw_ascii_menu, print_header

# Sukuriame bibliotekos egzempliorių (vieną kartą visai programai)
library = Library()

def bootstrap_system():
    """Užtikrina, kad sistemoje yra bent vienas administratorius."""
    admins = [u for u in library.user_repository.get_all() if u.role == 'librarian']
    if not admins:
        print("Pirmas paleidimas: Kuriamas 'admin'.")
        library.auth_service.register_librarian("admin", "admin")
        print("Prisijungimas -> Vartotojas: admin, Slaptažodis: admin")

def main():
    bootstrap_system()
    
    while True:
        clear_screen()
        # Meniu piešiame naudodami draw_ascii_menu
        menu_options = [
            ("1", "Bibliotekininko prisijungimas"),
            ("2", "Skaitytojo prisijungimas"),
            ("3", "Išeiti")
        ]
        draw_ascii_menu("BIBLIOTEKOS SISTEMA", menu_options)
                
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            clear_screen()
            print_header("BIBLIOTEKININKO PRISIJUNGIMAS")
            username = input("Vartotojas: ")
            password = input("Slaptažodis: ")
            user = library.auth_service.authenticate_librarian(username, password)
            
            if user:
                # Kviečiame per naują importo vardą
                librarian_ui.run_menu(library, user) 
            else:
                print("Klaida: Neteisingi duomenys.")
                pause()

        elif choice == '2':
            clear_screen()
            print_header("SKAITYTOJO PRISIJUNGIMAS")
            card_id = input("Įveskite Kortelės ID: ")
            user = library.user_repository.find_by_id(card_id)
            
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