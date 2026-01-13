from src.ui.common import print_header, pause, clear_screen, select_object_from_list

def run(library, user):
    """
    Vartotojo turimų knygų ir grąžinimo meniu.
    """
    while True:
        clear_screen()
        print_header(f"MANO PASKYRA (ID: {user.id})")
        
        # Suskaičiuojame, kiek turi knygų
        count = len(user.borrowed_books_ids)
        print(f"Jūs turite knygų: {count}")
        print("-" * 30)
        
        print("1. Peržiūrėti mano knygas")
        print("2. Grąžinti knygą")
        print("0. Grįžti atgal")

        choice = input("\nPasirinkimas: ")

        if choice == '1':
            _show_my_books(library, user)
            pause()
        elif choice == '2':
            _return_process(library, user)
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()

def _get_my_book_objects(library, user):
    """Pagalbinė funkcija, paverčianti ID sąrašą į objektų sąrašą."""
    my_books = []
    for b_id in user.borrowed_books_ids:
        book = library.book_manager.get_book_by_id(b_id)
        if book:
            my_books.append(book)
    return my_books

def _show_my_books(library, user):
    print("\n--- Pasiimtos Knygos ---")
    books = _get_my_book_objects(library, user)
    
    if not books:
        print("Sąrašas tuščias.")
    else:
        for i, book in enumerate(books, 1):
            print(f"{i}. {book.title} (Grąžinti iki: {book.due_date})")

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