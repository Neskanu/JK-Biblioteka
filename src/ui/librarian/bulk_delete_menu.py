from src.ui.common import get_int_input, pause, clear_screen
from src.ui.ascii_styler import draw_ascii_table, draw_ascii_menu, print_header

def run(library):
    while True:
        clear_screen()
        # Meniu piešiame naudodami draw_ascii_menu
        menu_options = [
            ("1", "Ištrinti pagal AUTORIŲ"),
            ("2", "Ištrinti pagal ŽANRĄ"),
            ("3", "Ištrinti SENAS knygas (pagal leidimo metus)"),
            ("4", "Nurašyti PRARASTAS knygas (vėluoja > X metų)"),
            ("9", "ATSTATYTI DUOMENIS (Restore Backup)"),
            ("0", "Grįžti atgal")
        ]
        draw_ascii_menu("MASINIS KNYGŲ ŠALINIMAS", menu_options)
                
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
            # Kviečiame naują metodą iš Library, o ne iš book_manager
            candidates = library.get_candidates_lost(years) 
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
    draw_ascii_table(["ID", "Pavadinimas", "Autorius", "Metai"], [[b.id, b.title, b.author, b.year] for b in candidates])

    print("DĖMESIO: Šis veiksmas negrįžtamas (nebent turite atsarginę kopiją).")
    confirm = input(f"Ar tikrai norite ištrinti šias {len(candidates)} knygas? (rašykite 'TAIP' patvirtinimui): ")

    if confirm == 'TAIP':
        count = library.book_manager.batch_delete_books(candidates)
        print(f"\nSėkmingai ištrinta knygų: {count}")
    else:
        print("\nVeiksmas atšauktas.")
    
    pause()