"""
FAILAS: src/ui/reader/account_menu.py
PASKIRTIS: Leidžia skaitytojams peržiūrėti išduotas knygas ir grąžinti jas.
SUSIJĘ FAILAI:
  - Valdomas reader/main_menu.py
  - Naudoja ascii_styler apipavidalinimui.
KONTEKSTAS:
  - Valdymo konsolė vartotojui  
"""

from itertools import count
from src.ui.common import pause, clear_screen, select_object_from_list
from src.ui.ascii_styler import draw_ascii_menu, draw_ascii_table

def run(library, user):
    """
    Vartotojo turimų knygų ir grąžinimo meniu.
    """
    while True:
        clear_screen()
        # Suskaičiuojame, kiek turi knygų
        count = len(user.active_loans)
        # Meniu piešiame naudodami draw_ascii_menu
        draw_ascii_menu("MANO KNYGOS IR GRĄŽINIMAS", [
            ("1", "Peržiūrėti mano knygas"),
            ("2", "Grąžinti knygą"),
            ("3", "Grąžinti visas knygas"),
            ("0", "Grįžti atgal")
        ])
        print(f"Jūs turite knygų: {count}")
        choice = input("\nPasirinkimas: ")
        clear_screen()
        if choice == '1':
            _show_my_books(library, user)
            pause()
        elif choice == '2':
            _return_process(library, user)
        elif choice == '3':
            # --- Grąžinti knygas po vieną nepatogu, taigi leidžiam grąžinti visas ---
            if not user.active_loans:
                print("\nNeturite ką grąžinti.")
            else:
                confirm = input("Ar tikrai norite grąžinti VISAS knygas? (t/n): ")
                if confirm.lower() == 't':
                    success, msg = library.return_all_books(user.id)
                    print(f"\n{msg}")
                else:
                    print("Atšaukta.")
            pause()
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()

def _get_my_book_objects(library, user):
    """
    Pagalbinė funkcija. Mums reikia paversti active_loans (žodynus) 
    atgal į tikrus Knygų Objektus, kad veiktų 'select_object_from_list' funkcija.
    """
    my_books = [] # Sąrašas knygų objektų, kurias turi vartotojas
    for loan in user.active_loans: # loan yra žodynas su 'book_id' ir 'due_date'
        book = library.book_manager.get_book_by_id(loan['book_id'])
        if book:
            my_books.append(book)
    return my_books

def _show_my_books(library, user):
    """
    Atvaizduoja pasiskolintų knygų sąrašą.
    """
    if not user.active_loans:
        print("Neturite knygų.")
    else:
        headers = ["Nr.", "Pavadinimas", "Autorius", "Grąžinti iki"]
        data = []
        
        for i, loan in enumerate(user.active_loans, 1):
            # --- FIX: Look up the book object to get author details ---
            book = library.book_manager.get_book_by_id(loan['book_id'])
            
            # Jei knyga egzistuoja (nebuvo ištrinta), imame jos autorių
            author = book.author if book else "Nežinomas"
            
            # --- Naudojame 'due_date' iš loan įrašo ---
            due_date = loan.get('due_date', 'N/A')
            
            data.append([i, loan['title'], author, due_date])
        
        draw_ascii_table(headers, data, title="Pasiskolintų Knygų Sąrašas")
        
def _return_process(library, user):
    books = _get_my_book_objects(library, user)
    
    if not books:
        print("\nNeturite knygų, kurias galėtumėte grąžinti.")
        pause()
        return

    selected_book = select_object_from_list(books, "Kurią knygą norite grąžinti?")
    
    if selected_book:
        success, message = library.return_book(user.id, selected_book.id)
        print(f"\n{message}")
        pause()