from src.ui.common import print_header, pause, clear_screen
# Importuojame sub-meniu modulius
from src.ui.librarian import books_menu, users_menu, stats_menu

def run_menu(library, user):
    """
    Pagrindinis bibliotekininko meniu, kuris nukreipia į atitinkamus failus.
    """
    while True:
        clear_screen()
        print_header(f"BIBLIOTEKININKAS: {user.username}")
        print("1. Knygų valdymas")
        print("2. Vartotojų valdymas")
        print("3. Statistika")
        print("0. Atsijungti")
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            # Kviečiame 'run' funkciją iš books_menu failo
            books_menu.run(library)
        elif choice == '2':
            users_menu.run(library)
        elif choice == '3':
            stats_menu.run(library)
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()