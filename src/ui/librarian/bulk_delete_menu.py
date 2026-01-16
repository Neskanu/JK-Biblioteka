"""
FAILAS: src/ui/librarian/bulk_delete_menu.py
PASKIRTIS: Bibliotekininko meniu, skirtas masiniam knygų šalinimui.
VEIKIMO PRINCIPAS:
  1. Vartotojas pasirenka kriterijų (autorius, žanras, metai).
  2. Sistema surenka knygas iš BookRepository.
  3. Vartotojas patvirtina veiksmą.
  4. Sistema surenka knygų ID ir siunčia juos į InventoryService masiniam trynimui.
RYŠIAI:
  - Naudoja: library.book_repository (paieškai).
  - Naudoja: library.inventory_service (trynimui).
"""

from datetime import datetime, timedelta
from src.ui.common import get_int_input, pause, clear_screen
from src.ui.ascii_styler import draw_ascii_table, draw_ascii_menu

def run(library):
    while True:
        clear_screen()
        # Meniu
        menu_options = [
            ("1", "Ištrinti pagal AUTORIŲ"),
            ("2", "Ištrinti pagal ŽANRĄ"),
            ("3", "Ištrinti SENAS knygas (pagal leidimo metus)"),
            ("4", "Pažymėtos kaip PRARASTOS knygos"),
            ("0", "Grįžti atgal")
        ]
        draw_ascii_menu("MASINIS KNYGŲ ŠALINIMAS", menu_options)
                
        choice = input("\nPasirinkimas: ")
        
        # 1. Paimame VISAS knygas iš repozitorijos
        all_books = library.book_repository.get_all()
        candidates = []

        if choice == '1':
            author_input = input("Įveskite autoriaus vardą (arba jo dalį): ").strip().lower()
            
            # PAKEITIMAS: Naudojame 'in' vietoje '=='
            # Tai leis rasti "George Orwell" įvedus tik "orwell"
            candidates = [
                b for b in all_books 
                if b.author and author_input in b.author.lower()
            ]
            _confirm_and_delete(library, candidates)
            
        elif choice == '2':
            genre_input = input("Įveskite žanrą (arba dalį): ").strip().lower()
            
            # PAKEITIMAS: Taip pat ir žanrui
            candidates = [
                b for b in all_books 
                if b.genre and genre_input in b.genre.lower()
            ]
            _confirm_and_delete(library, candidates)
            
        elif choice == '3':
            year_limit = get_int_input("Ištrinti senesnes nei (metai): ")
            # Filtruojame pagal metus
            candidates = [
                b for b in all_books 
                if b.year < year_limit
            ]
            _confirm_and_delete(library, candidates)
            
        elif choice == '4':
            # --- LOGIKA PRARASTOMS KNYGOMS (Per Vartotojus) ---
            years = get_int_input("Kiek metų vėluoja grąžinimas?: ")
            
            # Data: Šiandien minus X metų
            cutoff_date = datetime.now() - timedelta(days=years*365)
            
            lost_book_ids = []
            
            # 1. Gauname visus vartotojus
            if hasattr(library, 'user_repository'):
                users = library.user_repository.get_all()
                
                print(f"DEBUG: Tikrinami {len(users)} vartotojai dėl vėlavimų...")

                for user in users:
                    # Tikriname, ar vartotojas turi pasiskolintų knygų sąrašą
                    # Dažniausiai tai būna 'borrowed_books' arba 'loans'
                    loans = getattr(user, 'borrowed_books', [])
                    
                    for loan in loans:
                        # Priklausomai nuo to, ar loan yra žodynas (dict), ar objektas
                        # Bandome gauti datą ir knygos ID
                        if isinstance(loan, dict):
                            due_date_str = loan.get('due_date') or loan.get('return_date')
                            book_id = loan.get('book_id') or loan.get('id')
                        else:
                            # Jei tai objektas
                            due_date_str = getattr(loan, 'due_date', None)
                            book_id = getattr(loan, 'book_id', None)

                        if due_date_str and book_id:
                            try:
                                # Konvertuojame datą iš string į datetime
                                # Tikimės formato YYYY-MM-DD
                                due_dt = datetime.strptime(due_date_str, "%Y-%m-%d")
                                
                                # Jei grąžinimo data yra senesnė nei riba -> knyga prarasta
                                if due_dt < cutoff_date:
                                    lost_book_ids.append(book_id)
                            except ValueError:
                                # Jei data blogo formato, ignoruojame
                                continue

                # 2. Surandame knygų objektus pagal rastus ID
                # (tik tas knygas, kurios vis dar egzistuoja bibliotekoje)
                candidates = [b for b in all_books if b.id in lost_book_ids]
                
                if not candidates and years > 100:
                    print("Patarimas: Patikrinkite, ar teisingai įvedėte metus.")
                
                _confirm_and_delete(library, candidates)
            else:
                print("\nKLAIDA: Nerasta 'user_repository'.")
                pause()

        # elif choice == '9':
        #     print("\n--- DUOMENŲ ATSTATYMAS ---")
        #     confirm = input("DĖMESIO: Visi duomenys bus perrašyti iš atsarginės kopijos. Tęsti? (t/n): ")
        #     if confirm.lower() == 't':
        #         success, msg = library.book_repository.restore_backup()
        #         if success:
        #             print(f"\n✅ {msg}")
        #         else:
        #             print(f"\n❌ {msg}")
        #     else:
        #         print("Atšaukta.")
        #     pause()
            
        # elif choice == '0':
        #     break
        # else:
        #     print("Neteisingas pasirinkimas.")
        #     pause()

def _confirm_and_delete(library, candidates):
    """
    Pagalbinė funkcija, kuri parodo sąrašą ir paprašo patvirtinimo.
    """
    if not candidates:
        print("\nNerasta jokių knygų, atitinkančių kriterijus.")
        pause()
        return

    clear_screen()
    # Atvaizduojame lentelę
    table_data = [[b.id, b.title, b.author, b.year] for b in candidates]
    draw_ascii_table(["ID", "Pavadinimas", "Autorius", "Metai"], table_data)

    print("\nDĖMESIO: Šis veiksmas negrįžtamas.")
    confirm = input(f"Ar tikrai norite ištrinti šias {len(candidates)} knygas? (rašykite 'TAIP' patvirtinimui): ")

    if confirm.strip().upper() == 'TAIP':
        # --- ESMINIS PATAISYMAS ---
        # 1. Ištraukiame tik ID iš knygų objektų
        # Tai būtina, nes InventoryService.batch_delete tikisi ID sąrašo, o ne objektų
        ids_to_delete = [b.id for b in candidates]
        
        # 2. Siunčiame ID sąrašą į InventoryService
        count = library.inventory_service.batch_delete(ids_to_delete)
        
        print(f"\nSėkmingai ištrinta knygų: {count}")
    else:
        print("\nVeiksmas atšauktas.")
    
    pause()