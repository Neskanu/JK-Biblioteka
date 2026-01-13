from src.ui.common import print_header, pause, clear_screen
# Importuojame sub-modulius
from src.ui.reader import discover_menu, account_menu

def run_menu(library, user):
    """
    Pagrindinis skaitytojo meniu.
    """
    while True:
        clear_screen()
        print_header(f"SVEIKI SUGRĮŽĘ, {user.username.upper()}")
        print("1. Knygų katalogas (Paieška, Naujienos)")
        print("2. Mano knygos ir Grąžinimas")
        print("0. Atsijungti")
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            discover_menu.run(library, user)
        elif choice == '2':
            account_menu.run(library, user)
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()