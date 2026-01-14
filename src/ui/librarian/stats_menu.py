from src.ui.common import pause, clear_screen
from src.ui.ascii_styler import draw_ascii_menu, draw_ascii_table, print_header 

def run(library):
    """Statistikos sub-meniu."""
    while True:
        clear_screen()
        # Meniu piešiame naudodami draw_ascii_menu
        menu_options = [
            ("1", "Bendroji bibliotekos statistika"),
            ("2", "Vėluojančių knygų sąrašas"),
            ("3", "Išplėstinė analizė"),
            ("0", "Grįžti atgal")
        ]
        draw_ascii_menu("STATISTIKA", menu_options)
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            clear_screen
            books = library.book_manager.get_all_books()
            borrowed = len([b for b in books if b.available_copies < b.total_copies])
            users_count = len(library.user_manager.users)
            print_header("Bendroji Bibliotekos Statistika")
            draw_ascii_table(["Statistika", "Reikšmė"], [
                ["Vartotojų sistemoje", users_count],
                ["Iš viso knygų", len(books)],
                [" - Paskolinta", borrowed],
                [" - Laisva", len(books) - borrowed]
            ])
            pause()
            
        elif choice == '2':
            overdue = library.get_all_overdue_books()

            print_header("Vėluojančios Knygos")
            if not overdue:
                print("Šaunu! Vėluojančių knygų nėra.")
            else:
                draw_ascii_table(["ID", "Pavadinimas", "Autorius", "Metai"],
                                 [[b.id, b.title, b.author, b.year] for b in overdue])    
            pause()

        elif choice == '3':
            # --- NAUJAS PUNKTAS ---
            stats = library.get_advanced_statistics()
            
            print_header("IŠPLĖSTINĖ ANALIZĖ")
            
            print(f"📚  Dominuojantis žanras lentynose:  {stats['inventory_top_genre']}")
            print(f"🔥  Skaitytojai dažniausiai renkasi: {stats['borrowed_top_genre']}")
            print("-" * 50)
            print(f"⚠️  Vidutiniškai vėluojama (knygų/žm.): {stats['avg_overdue_per_reader']}")
            print(f"📅  Vidutiniai knygų leidimo metai:     {stats['avg_book_year']}")
            
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()