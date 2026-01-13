from src.ui.common import print_header, pause

def run_menu(library, user):
    """
    Vykdo skaitytojo meniu ciklą.
    """
    while True:
        print_header(f"Skaitytojas: {user.username}")
        print("1. Ieškoti knygų")
        print("2. Pasiimti knygą")
        print("3. Grąžinti knygą")
        print("4. Mano pasiimtos knygos")
        print("0. Atsijungti")

        choice = input("\nPasirinkimas: ")

        if choice == '1':
            query = input("Įveskite pavadinimą arba autorių: ")
            results = library.book_manager.search_books(query)
            print_header("Paieškos Rezultatai")
            if results:
                for b in results:
                    print(f"ID: {b.id} | {b}")
            else:
                print("Nieko nerasta.")
            pause()

        elif choice == '2':
            book_id = input("Įveskite Knygos ID: ")
            success, message = library.borrow_book(user.id, book_id)
            print(f"\n{message}")
            pause()

        elif choice == '3':
            book_id = input("Įveskite grąžinamos Knygos ID: ")
            success, message = library.return_book(user.id, book_id)
            print(f"\n{message}")
            pause()

        elif choice == '4':
            print_header("Mano Knygos")
            if not user.borrowed_books_ids:
                print("Neturite pasiimtų knygų.")
            else:
                for b_id in user.borrowed_books_ids:
                    book = library.book_manager.get_book_by_id(b_id)
                    if book:
                        print(f"- {book.title} (Grąžinti iki: {book.due_date})")
                    else:
                        print(f"- Knyga nerasta (ID: {b_id})")
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")