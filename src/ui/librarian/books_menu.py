# FAILAS: src/ui/librarian/books_menu.py
# PASKIRTIS: Valdo vartotojo sąsają knygų administravimui.
# RYŠIAI:
#   - Importuoja draw_ascii_table iš src/ui/ascii_styler.py
#   - Kviečia metodus iš library.book_manager

from src.ui.common import get_int_input, get_valid_string, get_valid_string, get_valid_year, get_valid_year, pause, clear_screen, select_object_from_list # Meniu bendros funkcijos
from src.ui.librarian import bulk_delete_menu # Masinio trynimo meniu
from src.ui.ascii_styler import draw_ascii_table, draw_ascii_menu

def run(library):
    """Knygų valdymo sub-meniu."""
    while True:
        clear_screen()
    # Meniu piešiame naudodami draw_ascii_menu
        menu_options = [
            ("1", "Pridėti naują knygą"),
            ("2", "Masinis šalinimas ir atstatymas"),
            ("3", "Ištrinti konkrečią knygą"),
            ("4", "Rodyti visas knygas (Lentelė)"),
            ("0", "Grįžti atgal")
        ]
        draw_ascii_menu("KNYGŲ VALDYMAS", menu_options)
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            print("\n--- Nauja Knyga ---")
            print("(Rašykite 'CANCEL', jei norite nutraukti)")
            
            # Naudojame validaciją
            title = get_valid_string("Pavadinimas: ")
            if title.upper() == 'CANCEL': continue # Galimybė atšaukti

            author = get_valid_string("Autorius: ")
            genre = get_valid_string("Žanras: ")
            year = get_valid_year("Leidimo metai: ")
            
            # Papildomai: galime formatuoti tekstą, kad duomenų bazė būtų graži
            title = title.title()   # "haris poteris" -> "Haris Poteris"
            author = author.title() # "j.k. rowling" -> "J.K. Rowling"
            genre = genre.capitalize() # "fantastika" -> "Fantastika"

            # Kviečiame book_manager
            # Pastaba: Add_book metodas dabar jau moka padidinti kiekį,
            # jei knyga tokiu pavadinimu/autoriumi jau yra.
            book = library.book_manager.add_book(title, author, year, genre)
            
            print(f"\nSĖKMĖ: Knyga įtraukta/atnaujinta!")
            print(f"Dabar turime kopijų: {book.total_copies}")
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
            if not books:
                print("Biblioteka tuščia.")
            else:
                # --- ASCII LENTELĖS IMPLEMENTACIJA ---
                # 1. Paruošiame Antraštes
                headers = ["ID (Trumpas)", "Autorius", "Pavadinimas", "Metai", "Likutis"]
                
                # 2. Paruošiame Eilutes
                rows = []
                for b in books:
                    short_id = b.id[-4:]  # Paskutiniai 4 simboliai
                    qty_info = f"{b.available_copies}/{b.total_copies}"
                    rows.append([short_id, b.author, b.title, b.year, qty_info])
                
                # 3. Atvaizduojame
                draw_ascii_table(headers, rows, title="Knygų Sąrašas")
                # -------------------------------------
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()