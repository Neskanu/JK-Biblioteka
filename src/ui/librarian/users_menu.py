"""
FILE: src/ui/librarian/users_menu.py
PURPOSE: Pagrindinis meniu vartotojų valdymo kategorijai.
RELATIONSHIPS:
  - Importuoja user_creation.py ir user_management.py
  - Veikia kaip valdiklis (Router).
CONTEXT:
  - Išskaidytas failas geresniam skaitomumui.
"""

from src.ui.common import pause, clear_screen
from src.ui.ascii_styler import draw_ascii_menu
# Importuojame naujus modulius
from src.ui.librarian import user_creation, user_management

def run(library):
    """Vartotojų valdymo sub-meniu."""
    while True:
        clear_screen()
        
        menu_options = [
            ("1", "Registruoti naują Skaitytoją"),
            ("2", "Registruoti naują Bibliotekininką"),
            ("3", "Redaguoti / Trinti vartotojus (Sąrašas)"),
            ("0", "Grįžti atgal")
        ]
        
        draw_ascii_menu("VARTOTOJŲ VALDYMAS", menu_options)

        choice = input("\nPasirinkimas: ")

        if choice == '1':
            user_creation.register_reader(library)
        elif choice == '2':
            user_creation.register_librarian(library)
        elif choice == '3':
            user_management.manage_users_loop(library)
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()