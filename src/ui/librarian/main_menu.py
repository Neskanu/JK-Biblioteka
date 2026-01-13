from src.ui.common import pause, clear_screen
# Importuojame sub-meniu modulius
from src.ui.librarian import books_menu, users_menu, stats_menu
from src.ui.ascii_styler import draw_ascii_menu

def run_menu(library, user):
    """
    Pagrindinis bibliotekininko meniu, kuris nukreipia į atitinkamus failus.
    """
    while True:
        clear_screen()
        # Meniu piešiame naudodami draw_ascii_menu
        menu_options = [
            ("1", "Knygų valdymas"),
            ("2", "Vartotojų valdymas"),
            ("3", "Statistika"),
            ("0", "Atsijungti")
        ]
        draw_ascii_menu("BIBLIOTEKININKO MENIU", menu_options)
                
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