from src.ui.common import print_header, pause, clear_screen, select_object_from_list

def run(library, user):
    """
    Vartotojo turimų knygų ir grąžinimo meniu.
    """
    while True:
        clear_screen()
        print_header(f"MANO PASKYRA (ID: {user.id})")
        
        # Suskaičiuojame, kiek turi knygų
        count = len(user.active_loans)
        print(f"Jūs turite knygų: {count}")
        print("-" * 30)
        
        print("1. Peržiūrėti mano knygas")
        print("2. Grąžinti knygą")
        print("3. Grąžinti visas knygas")
        print("0. Grįžti atgal")

        choice = input("\nPasirinkimas: ")

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
    my_books = []
    for loan in user.active_loans:
        book = library.book_manager.get_book_by_id(loan['book_id'])
        if book:
            my_books.append(book)
    return my_books

def _show_my_books(library, user):
    # Dabar nereikia konvertuoti ID -> Book Obj, nes active_loans jau turi pavadinimą
    if not user.active_loans:
        print("Neturite knygų.")
    else:
        for i, loan in enumerate(user.active_loans, 1):
            print(f"{i}. {loan['title']} (Iki: {loan['due_date']})")

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