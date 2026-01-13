from src.ui.common import print_header, get_int_input, pause

def run_menu(library, user):
    """
    Vykdo bibliotekininko meniu ciklą.
    """
    while True:
        print_header(f"Bibliotekininkas: {user.username}")
        print("1. Pridėti naują knygą")
        print("2. Ištrinti senas knygas")
        print("3. Registruoti naują Skaitytoją")
        print("4. Registruoti naują Bibliotekininką")
        print("5. Rodyti visas knygas")
        print("6. Rodyti vėluojančias knygas")
        print("7. Statistika")
        print("0. Atsijungti")
        
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
            print("\n--- Skaitytojo Registracija ---")
            name = input("Vartotojo vardas: ")
            new_user = library.user_manager.register_reader(name)
            if new_user:
                print(f"Skaitytojas sukurtas! ID: {new_user.id}")
                print("(Būtinai perduokite šį ID skaitytojui)")
            else:
                print("Klaida: Vartotojas tokiu vardu jau egzistuoja.")
            pause()

        elif choice == '4':
            print("\n--- Kolegos Registracija ---")
            name = input("Vartotojo vardas: ")
            pwd = input("Slaptažodis: ")
            if library.user_manager.register_librarian(name, pwd):
                print("Bibliotekininkas užregistruotas.")
            else:
                print("Vartotojas jau egzistuoja.")
            pause()

        elif choice == '5':
            books = library.book_manager.get_all_books()
            print_header("Knygų Sąrašas")
            for b in books:
                print(f"{b.id:<38} | {b}")
            pause()

        elif choice == '6':
            overdue = library.get_all_overdue_books()
            print_header("Vėluojančios Knygos")
            if not overdue:
                print("Šaunu, vėluojančių nėra.")
            for b in overdue:
                print(f"'{b.title}' (Terminas: {b.due_date}, Skolininkas: {b.borrower_id})")
            pause()

        elif choice == '7':
            books = library.book_manager.get_all_books()
            borrowed = len([b for b in books if b.is_borrowed])
            print_header("Statistika")
            print(f"Iš viso knygų: {len(books)}")
            print(f"Paskolinta:   {borrowed}")
            print(f"Laisva:       {len(books) - borrowed}")
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()