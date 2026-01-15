"""
FILE: src/ui/librarian/user_management.py
PURPOSE: Rodo vartotojų sąrašą, leidžia redaguoti ir trinti.
RELATIONSHIPS:
  - Naudoja ascii_styler lentelėms.
  - Vykdo safe_delete_user logiką iš library.py
"""

from src.ui.common import pause, clear_screen, get_int_input
from src.ui.ascii_styler import draw_ascii_table, print_header

def manage_users_loop(library):
    """Pagrindinis ciklas vartotojų peržiūrai ir redagavimui."""
    while True:
        clear_screen()
        users = library.user_manager.users
        
        if not users:
            print_header("VARTOTOJŲ SĄRAŠAS")
            print("Vartotojų nėra.")
            pause()
            break

        # Atvaizduojame lentelę
        headers = ["Nr.", "Rolė", "ID / Prisijungimas", "Vardas"]
        data = []
        
        for i, u in enumerate(users, 1):
            role_lt = "Skaitytojas" if u.role == 'reader' else "Admin"
            display_id = u.id if u.role == 'reader' else u.username
            data.append([i, role_lt, display_id, u.username])
        
        draw_ascii_table(headers, data, title="VARTOTOJŲ SĄRAŠAS")
            
        print("0. Grįžti atgal")
        
        choice = get_int_input("\nPasirinkite vartotoją redagavimui (Nr.): ")
        
        if choice == 0:
            break
            
        if 1 <= choice <= len(users):
            selected_user = users[choice - 1]
            if selected_user.role == 'reader':
                _edit_reader(library, selected_user)
            else:
                _edit_librarian(library, selected_user)
        else:
            print("Neteisingas numeris.")
            pause()

def _edit_reader(library, user):
    """Konkretaus skaitytojo redagavimo meniu."""
    while True:
        clear_screen()
        print_header(f"REDAGUOJAMAS: {user.username}")
        print(f"Kortelės ID: {user.id}")
        print("-" * 30)
        print("1. Išduoti naują kortelę (Regeneruoti ID)")
        print("2. Ištrinti skaitytoją")
        print("0. Grįžti")
        
        choice = input("\nPasirinkimas: ")
        
        if choice == '1':
            old_id = user.id
            new_id = library.user_manager.regenerate_reader_id(user)
            print(f"\nSėkmingai! Senas ID: {old_id} -> Naujas ID: {new_id}")
            pause()
            
        elif choice == '2':
            if _confirm_delete(library, user):
                break 
        elif choice == '0':
            break

def _edit_librarian(library, user):
    """Konkretaus bibliotekininko redagavimo meniu."""
    while True:
        clear_screen()
        print_header(f"REDAGUOJAMAS ADMIN: {user.username}")
        print("1. Pakeisti vardą")
        print("2. Pakeisti slaptažodį")
        print("3. Ištrinti vartotoją")
        print("0. Grįžti")
        
        choice = input("\nPasirinkimas: ")
        
        if choice == '1':
            new_name = input("Naujas vartotojo vardas: ")
            library.user_manager.update_librarian(user, new_username=new_name)
            print("Vardas atnaujintas.")
            pause()
            
        elif choice == '2':
            new_pwd = input("Naujas slaptažodis: ")
            library.user_manager.update_librarian(user, new_password=new_pwd)
            print("Slaptažodis atnaujintas.")
            pause()
            
        elif choice == '3':
            if _confirm_delete(library, user):
                break
        elif choice == '0':
            break

def _confirm_delete(library, user):
    """Pagalbinė funkcija trynimui."""
    confirm = input(f"Ar tikrai ištrinti vartotoją '{user.username}'? (t/n): ")
    if confirm.lower() == 't':
        success, response = library.safe_delete_user(user)
        if success:
            print(f"\n{response}")
            pause()
            return True
        else:
            print("\nKLAIDA: Negalima ištrinti.")
            if isinstance(response, list):
                print("Vartotojas turi negrąžintų knygų:")
                for title in response:
                    print(f"- {title}")
            else:
                print(response)
            pause()
            return False
    return False