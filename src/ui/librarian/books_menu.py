from src.ui.common import print_header, get_int_input, pause, clear_screen, select_object_from_list # Meniu bendros funkcijos
from src.ui.librarian import bulk_delete_menu # Masinio trynimo meniu


def run(library):
    """Knygų valdymo sub-meniu."""
    while True:
        clear_screen()
        print_header("KNYGŲ VALDYMAS")
        print("1. Pridėti naują knygą")
        print("2. Masinis šalinimas ir atstatymas")
        print("3. Ištrinti konkrečią knygą")
        print("4. Rodyti visas knygas")
        print("0. Grįžti atgal")
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            print("\n--- Nauja Knyga ---")
            title = input("Pavadinimas: ")
            author = input("Autorius: ")
            genre = input("Žanras: ")
            year = get_int_input("Leidimo metai: ")
            library.book_manager.add_book(title, author, year, genre)
            print("Knyga sėkmingai pridėta!")
            pause()

        elif choice == '2':
            # Kviečiame sub-meniu modulį
            bulk_delete_menu.run(library)

        elif choice == '3':
            # --- KONKREČIOS KNYGOS TRYNIMAS ---
            print("\n--- Konkrečios knygos šalinimas ---")
            query = input("Įveskite pavadinimą paieškai: ")
            results = library.book_manager.search_books(query)
            
            target_book = select_object_from_list(results, "Kurią knygą ištrinti?")
            
            if target_book:
                is_fully_returned = (target_book.available_copies == target_book.total_copies)
                if not is_fully_returned:
                    print(f"\nKLAIDA: Knyga '{target_book.title}' yra paskolinta! Pirma ją reikia grąžinti.")
                else:
                    confirm = input(f"Ar tikrai norite ištrinti '{target_book.title}'? (t/n): ")
                    if confirm.lower() == 't':
                        # Čia reikėtų metodo book_manager.remove_book_by_id (jo dar neturime, tuoj sukursime)
                        # Arba tiesiog išimame iš sąrašo tiesiogiai:
                        library.book_manager.books.remove(target_book)
                        library.book_manager.save()
                        print("Knyga ištrinta.")
                    else:
                        print("Atšaukta.")
            pause()

        elif choice == '4':
            books = library.book_manager.get_all_books()
            clear_screen()
            print_header("Knygų Sąrašas")
            if not books:
                print("Biblioteka tuščia.")
            else:
                print(f"{'ID ':<8} | {'Laisvų/Iš viso kopijų':<20} | {'Autorius':<30} | {'Pavadinimas'}")
                print("-" * 80)
                for b in books:
                    # Atspausdiname eilės numerį sąraše
                    short_id = b.id[-4:]  # Paskutinės 4 raidės
                    qty_info = f"{b.available_copies}/{b.total_copies}"
                    print(f"{short_id:<15} | {qty_info:<8} | {b.author:<20} | {b.title}")
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()