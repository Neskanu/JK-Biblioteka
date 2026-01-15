"""
FILE: src/ui/reader/discover_menu.py
PURPOSE: Skaitytojo knygų katalogo meniu (Router).
RELATIONSHIPS:
  - Importuoja catalog_browser.py ir borrow_flow.py
CONTEXT:
  - Sujungia paiešką su pasiėmimu į vieną ciklą.
"""

from src.ui.common import clear_screen, pause
from src.ui.ascii_styler import draw_ascii_menu
# Importuojame naujus modulius
from src.ui.reader import catalog_browser, borrow_flow

def run(library, user):
    """Knygų paieškos ir pasiėmimo meniu ciklas."""
    while True:
        clear_screen()
        
        menu_options = [
            ("1", "Rodyti visas knygas"),
            ("2", "Ieškoti knygos"),
            ("0", "Grįžti atgal")
        ]
        
        draw_ascii_menu("KNYGŲ KATALOGAS", menu_options)
        
        choice = input("\nPasirinkimas: ")
        
        selected_book = None

        if choice == '1':
            # 1. Naršymas
            selected_book = catalog_browser.list_all_books(library)
            
        elif choice == '2':
            # 2. Paieška
            selected_book = catalog_browser.search_books(library)
            
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()
            
        # 3. Veiksmas (jei vartotojas kažką pasirinko naršydamas ar ieškodamas)
        if selected_book:
            borrow_flow.process_borrowing(library, user, selected_book)