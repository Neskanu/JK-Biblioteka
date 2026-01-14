"""
FAILAS: src/ui/librarian/stats_menu.py
PASKIRTIS: Rodo statistinius duomenis ir vėluojančių knygų ataskaitas.
RYŠIAI:
  - Ima duomenis iš Library valdiklio.
  - Naudoja draw_ascii_table iš ui/ascii_styler.py.
"""

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
            # 1. Bendroji statistika
            clear_screen()
            books = library.book_manager.get_all_books()
            borrowed = len([b for b in books if b.available_copies < b.total_copies])
            users_count = len(library.user_manager.users)
            draw_ascii_table(
                ["Statistika", "Reikšmė",], 
                             [
                                ["Vartotojų sistemoje", users_count],
                                ["Iš viso knygų", len(books)],
                                [" - Paskolinta", borrowed],
                                [" - Laisva", len(books) - borrowed]
                             ],
                title="Bendroji Bibliotekos Statistika"
                )
            pause()
            
        elif choice == '2':
            # 2. Vėluojančios knygos
            # library.get_all_overdue_books() grąžina: [{'title':..., 'user':..., 'due_date':...}, ...]
            overdue = library.get_all_overdue_books()
            clear_screen()
            if not overdue:
                print("Šaunu! Vėluojančių knygų nėra.")
            else:
                # Naudojame žodyno raktus ['title']
                table_data = []
                for item in overdue:
                    table_data.append(
                        [
                         item['title'], # Knygos pavadinimas
                         item['due_date'], # Grąžinimo data
                         item['user'] # Vartotojo vardas
                        ]
                    )
                draw_ascii_table(
                                ["Knyga", "Terminas", "Skolininkas"],
                                table_data, 
                                title="Vėluojančių Knygų Sąrašas"
                                )    
            pause()

        elif choice == '3':
            # --- NAUJAS PUNKTAS ---
            stats = library.get_advanced_statistics()
            clear_screen()
            draw_ascii_table(["Statistika", "Reikšmė"],                              
                                                    [
                                                    ["Dominuojantis žanras lentynose", stats['inventory_top_genre']],
                                                     ["Skaitytojai dažniausiai renkasi", stats['borrowed_top_genre']],
                                                     ["Vidutiniškai vėluoja (knygų/žm.)", stats['avg_overdue_per_reader']],
                                                     ["Vidutiniai knygų leidimo metai", stats['avg_book_year']]
                                                    ], 
                                                    title="Išplėstinė Analizė"
                            )
                    
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()