from src.ui.common import print_header, pause, clear_screen, select_object_from_list

def run(library, user):
    """
    Knygų paieškos ir skolinimosi meniu.
    """
    while True:
        clear_screen()
        print_header("KNYGŲ KATALOGAS")
        print("1. Ieškoti pagal pavadinimą/autorių")
        print("2. Rodyti visas laisvas knygas") # Nauja patogi funkcija
        print("0. Grįžti atgal")

        choice = input("\nPasirinkimas: ")

        if choice == '1':
            _search_and_borrow(library, user)
        elif choice == '2':
            _browse_available(library, user)
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()

def _search_and_borrow(library, user):
    print("\n--- Paieška ---")
    query = input("Įveskite paieškos frazę: ")
    results = library.book_manager.search_books(query)
    
    # Filtruojame, kad rodytų tik laisvas knygas (neprivaloma, bet patogu)
    # Galima rodyti ir užimtas, bet su prierašu (PAIMTA)
    
    selected_book = select_object_from_list(results, "Pasirinkite knygą, kurią norite pasiimti")
    
    if selected_book:
        _process_borrow(library, user, selected_book)

def _browse_available(library, user):
    # Rodo tik tas knygas, kurios nėra paskolintos
    all_books = library.book_manager.get_all_books()
    available_books = [b for b in all_books if not b.is_borrowed]
    
    selected_book = select_object_from_list(available_books, "Pasirinkite knygą")
    
    if selected_book:
        _process_borrow(library, user, selected_book)

def _process_borrow(library, user, book):
    """Pagalbinė funkcija skolinimosi veiksmui atlikti."""
    # Pabandome pasiskolinti
    success, message = library.borrow_book(user.id, book.id)
    
    if success:
        print(f"\nSĖKMĖ: {message}")
    else:
        print(f"\nKLAIDA: {message}")
    pause()