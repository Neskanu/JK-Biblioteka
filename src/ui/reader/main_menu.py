"""
FAILAS: src/ui/reader/main_menu.py
PASKIRTIS: Pagrindinis navigacijos centras skaitytojams.
RYŠIAI:
  - Naudoja bendrus UI įrankius iš src/ui/ascii_styler.py
"""
from src.ui.common import pause, clear_screen
from src.ui.reader import discover_menu, account_menu
from src.ui.ascii_styler import draw_ascii_menu
from src.ui.reader.dashboard import show_user_fines

def run_menu(library, user):
    """
    Pagrindinis skaitytojo meniu.
    """
    while True:
        clear_screen()
        # Meniu piešiame naudodami draw_ascii_menu
        menu_options = [
            ("1", "Knygų katalogas ir paieška"),
            ("2", "Mano knygos ir grąžinimas"),
            ("3", "Mano skolos ir baudos"),
            ("0", "Atsijungti")
        ]
        draw_ascii_menu("SKAITYTOJO MENIU", menu_options)
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            discover_menu.run(library, user)
        elif choice == '2':
            account_menu.run(library, user)
        elif choice == '3':
            show_user_fines(library, user)
            pause()
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()