"""
FILE: src/ui/reader/catalog_browser.py
PURPOSE: Atsakingas už knygų paiešką ir atvaizdavimą skaitytojui.
RELATIONSHIPS:
  - Naudoja draw_ascii_table iš ui/ascii_styler.py
  - Grąžina pasirinktą knygos objektą arba None.
CONTEXT:
  - Atskirtas nuo pasiėmimo logikos, kad būtų galima lengviau tobulinti paiešką.
"""

from src.ui.common import clear_screen, pause, get_int_input, select_object_from_list
from src.ui.ascii_styler import draw_ascii_table

def search_books(library):
    """
    Vykdo knygų paiešką pagal vartotojo įvestį.
    Grąžina pasirinktą knygą arba None.
    """
    print("\n--- Knygų Paieška ---")
    query = input("Įveskite pavadinimą arba autorių: ")
    
    results = library.book_manager.search_books(query)
    
    if not results:
        print("Nieko nerasta.")
        pause()
        return None
        
    return select_object_from_list(results, "Pasirinkite knygą peržiūrai")

def list_all_books(library):
    """
    Rodo visas bibliotekos knygas lentelėje.
    Grąžina pasirinktą knygą arba None.
    """
    clear_screen()
    books = library.book_manager.get_all_books()
    
    if not books:
        print("Biblioteka tuščia.")
        pause()
        return None

    # Paruošiame duomenis lentelei
    headers = ["Nr.", "Autorius", "Pavadinimas", "Žanras", "Likutis"]
    data = []
    
    for i, b in enumerate(books, 1):
        availability = f"{b.available_copies}/{b.total_copies}"
        data.append([i, b.author, b.title, b.genre, availability])
    
    draw_ascii_table(headers, data, title="KNYGŲ KATALOGAS")
    
    print("0. Grįžti")
    choice = get_int_input("\nPasirinkite knygos numerį pasiėmimui (arba 0): ")
    
    if choice == 0:
        return None
        
    if 1 <= choice <= len(books):
        return books[choice - 1]
    else:
        print("Neteisingas pasirinkimas.")
        pause()
        return None