from src.ui.common import print_header, pause, clear_screen

def run(library):
    """Statistikos sub-meniu."""
    while True:
        clear_screen()
        print_header("STATISTIKA IR ATASKAITOS")
        print("1. Bendroji bibliotekos statistika")
        print("2. Vėluojančių knygų sąrašas")
        print("0. Grįžti atgal")

        choice = input("\nPasirinkimas: ")

        if choice == '1':
            books = library.book_manager.get_all_books()
            borrowed = len([b for b in books if b.is_borrowed])
            users_count = len(library.user_manager.users)
            
            print_header("Bendroji Statistika")
            print(f"Vartotojų sistemoje:  {users_count}")
            print(f"Iš viso knygų:        {len(books)}")
            print(f" - Paskolinta:        {borrowed}")
            print(f" - Laisva:            {len(books) - borrowed}")
            pause()

        elif choice == '2':
            overdue = library.get_all_overdue_books()
            print_header("Vėluojančios Knygos")
            if not overdue:
                print("Šaunu! Vėluojančių knygų nėra.")
            else:
                print(f"Rasta vėluojančių: {len(overdue)}\n")
                for b in overdue:
                    print(f"Knyga: '{b.title}'")
                    print(f"   Terminas: {b.due_date}")
                    print(f"   Skolininko ID: {b.borrower_id}")
                    print("-" * 30)
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()