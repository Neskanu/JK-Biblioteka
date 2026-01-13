from src.ui.common import print_header, get_int_input, pause, clear_screen, select_object_from_list

def run(library):
    """Knygų valdymo sub-meniu."""
    while True:
        clear_screen()
        print_header("KNYGŲ VALDYMAS")
        print("1. Pridėti naują knygą")
        print("2. Ištrinti senas knygas")
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
            print("\n--- Knygų Šalinimas ---")
            year = get_int_input("Ištrinti senesnes nei (metai): ")
            count = library.book_manager.remove_old_books(year)
            print(f"Pašalinta knygų: {count}")
            pause()

        elif choice == '3':
            # --- NAUJA LOGIKA: KONKREČIOS KNYGOS TRYNIMAS ---
            print("\n--- Konkrečios knygos šalinimas ---")
            query = input("Įveskite pavadinimą paieškai: ")
            results = library.book_manager.search_books(query)
            
            target_book = select_object_from_list(results, "Kurią knygą ištrinti?")
            
            if target_book:
                if target_book.is_borrowed:
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
                print(f"{'ID (pabaiga)':<15} | {'Metai':<6} | {'Autorius':<20} | {'Pavadinimas'}")
                print("-" * 80)
                for b in books:
                    short_id = "..." + b.id[-12:] 
                    status = "(PAIMTA)" if b.is_borrowed else ""
                    print(f"{short_id:<15} | {b.year:<6} | {b.author:<20} | {b.title} {status}")
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()