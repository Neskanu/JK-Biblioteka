"""
FILE: src/ui/reader/account_menu.py
PURPOSE: Valdo skaitytojo paskyros meniu.
RELATIONSHIPS:
  - Naudoja Library servisus.
  - Naudoja Loan ir Book modelius per atributus (taškinė notacija).
CONTEXT:
  - Ištaisyta klaida naudojant objektinę sintaksę vietoje .get().
"""

from src.ui.common import pause, clear_screen, select_object_from_list
from src.ui.ascii_styler import draw_ascii_menu, draw_ascii_table

def run(library, user):
    while True:
        clear_screen()
        # user.active_loans dabar grąžina Mapped[List[Loan]]
        count = len(user.active_loans)
        
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
    """Konvertuoja Loan objektus į Book objektus."""
    my_books = []
    for loan in user.active_loans:
        # Naudojame atributą tiesiogiai
        if loan.book_id:
            book = library.book_manager.get_by_id(loan.book_id)
            if book:
                my_books.append(book)
    return my_books

def _show_my_books(library, user):
    if not user.active_loans:
        print("Neturite knygų.")
        return

    headers = ["Nr.", "Pavadinimas", "Autorius", "Grąžinti iki"]
    data = []
    
    for i, loan in enumerate(user.active_loans, 1):
        # Bandome pasiekti knygą per ORM ryšį, arba ieškome pagal ID
        book = loan.book if loan.book else library.book_manager.get_by_id(loan.book_id)
        author = book.author if book else "Nežinomas"
        
        # FIX: Naudojame taškinę notaciją, nes Loan yra klasė
        title = loan.title if loan.title else "Be pavadinimo"
        due_date = loan.due_date
        
        data.append([i, title, author, due_date])
    
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
    