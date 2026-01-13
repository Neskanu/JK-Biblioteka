from src.ui.common import print_header, get_int_input, pause, clear_screen

def run(library):
    while True:
        clear_screen()
        print_header("MASINIS KNYGŲ ŠALINIMAS")
        print("1. Ištrinti pagal AUTORIŲ")
        print("2. Ištrinti pagal ŽANRĄ")
        print("3. Ištrinti SENAS knygas (pagal leidimo metus)")
        print("4. Nurašyti PRARASTAS knygas (vėluoja > X metų)")
        print("-" * 40)
        print("9. ATSTATYTI DUOMENIS (Restore Backup)")
        print("0. Grįžti atgal")
        
        choice = input("\nPasirinkimas: ")
        
        candidates = []

        if choice == '1':
            author = input("Įveskite autoriaus vardą/pavardę: ")
            candidates = library.book_manager.get_candidates_by_author(author)
            _confirm_and_delete(library, candidates)
            
        elif choice == '2':
            genre = input("Įveskite žanrą: ")
            candidates = library.book_manager.get_candidates_by_genre(genre)
            _confirm_and_delete(library, candidates)
            
        elif choice == '3':
            year = get_int_input("Ištrinti senesnes nei (metai): ")
            candidates = library.book_manager.get_candidates_by_year(year)
            _confirm_and_delete(library, candidates)
            
        elif choice == '4':
            years = get_int_input("Kiek metų vėluoja knyga? (pvz., 5): ")
            candidates = library.book_manager.get_candidates_lost(years)
            _confirm_and_delete(library, candidates)

        elif choice == '9':
            print("\n--- Duomenų atstatymas ---")
            confirm = input("DĖMESIO: Visi dabartiniai duomenys bus pakeisti backup failo duomenimis. Tęsti? (t/n): ")
            if confirm.lower() == 't':
                success, msg = library.book_manager.restore_from_backup()
                print(f"\n{msg}")
                pause()
            
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()

def _confirm_and_delete(library, candidates):
    """
    Pagalbinė funkcija, kuri parodo sąrašą ir paprašo patvirtinimo.
    """
    if not candidates:
        print("\nNerasta jokių knygų, atitinkančių kriterijus (arba jos visos paskolintos).")
        pause()
        return

    clear_screen()
    print_header(f"RASTA KNYGŲ ŠALINIMUI: {len(candidates)}")
    
    # Rodyti pirmas 20, kad neužkištume ekrano
    for i, book in enumerate(candidates):
        if i >= 20:
            print(f"... ir dar {len(candidates) - 20} knygų.")
            break
        print(f"- {book.title} ({book.author}, {book.year})")

    print("-" * 50)
    print("DĖMESIO: Šis veiksmas negrįžtamas (nebent turite backup).")
    confirm = input(f"Ar tikrai norite ištrinti šias {len(candidates)} knygas? (rašykite 'TAIP' patvirtinimui): ")

    if confirm == 'TAIP':
        count = library.book_manager.batch_delete_books(candidates)
        print(f"\nSėkmingai ištrinta knygų: {count}")
    else:
        print("\nVeiksmas atšauktas.")
    
    pause()