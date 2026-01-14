from src.ui.common import pause, clear_screen, get_int_input, get_valid_string
from src.ui.ascii_styler import print_header, draw_ascii_menu, draw_ascii_table

def run(library):
    """Vartotojų valdymo sub-meniu."""
    while True:
        clear_screen()
        menu_options = [
            ("1", "Registruoti naują Skaitytoją"),
            ("2", "Registruoti naują Bibliotekininką"),
            ("3", "Redaguoti / Trinti vartotojus"),
            ("0", "Grįžti atgal")
        ]
        draw_ascii_menu("VARTOTOJŲ VALDYMAS", menu_options)
        
        choice = input("\nPasirinkimas: ")

        if choice == '1':
            _register_reader(library)
        elif choice == '2':
            _register_librarian(library)
        elif choice == '3':
            _manage_users(library)
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()

def _register_reader(library):
    clear_screen()
    print_header("SKAITYTOJO REGISTRACIJA")
    print("(Rašykite 'CANCEL', jei norite nutraukti)")
    name = get_valid_string("Vartotojo vardas (min 3 simboliai): ", min_length=3)

    if name.upper() == 'CANCEL':
        return
    
    # Formatuojame vardą gražiai (pvz. jonas -> Jonas)
    name = name.title()

    new_user = library.user_manager.register_reader(name)
    if new_user:
        print(f"Skaitytojas sukurtas! ID: [ {new_user.id} ]")
    else:
        print("Klaida: Nepavyko sukurti (galbūt vardas užimtas).")
    pause()

def _register_librarian(library):
    clear_screen()
    print_header("BIBLIOTEKININKO REGISTRACIJA")
    print("(Rašykite 'CANCEL', jei norite nutraukti)")
    # --- VALIDACIJA ---
    name = get_valid_string("Vartotojo vardas (min 3 simboliai): ", min_length=3)
    
    if name.upper() == 'CANCEL':
        return
    
    # Formatuojame vardą gražiai (pvz. jonas -> Jonas)
    name = name.title()
    pwd = get_valid_string("Slaptažodis: min 6 simboliai ", min_length=6)

    if library.user_manager.register_librarian(name, pwd):
        print("Bibliotekininkas užregistruotas.")
    else:
        print("Vartotojas jau egzistuoja.")
    pause()

def _manage_users(library):
    """Rodo vartotojų sąrašą ir leidžia pasirinkti."""
    while True:
        clear_screen()
        draw_ascii_table(["Nr.", "Rolė", "ID / Vartotojas"],
            [[i+1, "Skaitytojas" if u.role == 'reader' else "Admin", f"{u.id} ({u.username})"] for i, u in enumerate(library.user_manager.users)], title="Vartotojų Sąrašas"
        )
        users = library.user_manager.users
        
        # print(f"{'Nr.':<4} | {'Rolė':<12} | {'ID / Vartotojas'}")
        # print("-" * 50)
        # for i, u in enumerate(users, 1):
        #     display_name = u.id if u.role == 'reader' else u.username
        #     role_lt = "Skaitytojas" if u.role == 'reader' else "Admin"
        #     print(f"{i:<4} | {role_lt:<12} | {display_name} ({u.username})")
            
        print("-" * 50)
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
    """Skaitytojo redagavimo UI."""
    while True:
        clear_screen()
        draw_ascii_menu(f"REDAGUOJAMAS SKAITYTOJAS: {user.username}", [
            ("1", "Išduoti naują kortelę"),
            ("2", "Ištrinti skaitytoją"),
            ("0", "Grįžti")
        ])
                
        choice = input("\nPasirinkimas: ")
        
        if choice == '1':
            old_id = user.id
            # UI paprašo user_manager atlikti darbą
            new_id = library.user_manager.regenerate_reader_id(user)
            print(f"\nSėkmingai! Senas ID: {old_id} -> Naujas ID: {new_id}")
            pause()
            
        elif choice == '2':
            confirm = input("Ar tikrai ištrinti šį skaitytoją? (t/N): ")
            if confirm.lower() == 't':
                # UI kreipiasi į Library dėl saugaus trynimo
                success, response = library.safe_delete_user(user)
                
                if success:
                    print(f"\n{response}")
                    pause()
                    break # Vartotojas ištrintas, išeiname iš meniu
                else:
                    print("\nKLAIDA: Negalima ištrinti. Skaitytojas turi knygų:")
                    # response šiuo atveju yra knygų sąrašas
                    for title in response:
                        print(f"- {title}")
                    pause()
                    
        elif choice == '0':
            break

def _edit_librarian(library, user):
    """Bibliotekininko redagavimo UI."""
    while True:
        clear_screen()
        draw_ascii_menu(f"REDAGUOJAMAS ADMIN: {user.username}", [
            ("1", "Pakeisti vardą"),
            ("2", "Pakeisti slaptažodį"),
            ("3", "Ištrinti vartotoją"),
            ("0", "Grįžti")
        ])
        
        choice = input("\nPasirinkimas: ")
        
        if choice == '1':
            new_name = get_valid_string("Naujas vartotojo vardas (min 3 simboliai): ", min_length=3)
            library.user_manager.update_librarian(user, new_username=new_name)
            print("Vardas atnaujintas.")
            pause()
            
        elif choice == '2':
            new_pwd = get_valid_string("Naujas slaptažodis (min 6 simboliai): ", min_length=6)
            library.user_manager.update_librarian(user, new_password=new_pwd)
            print("Slaptažodis atnaujintas.")
            pause()
            
        elif choice == '3':
            confirm = input("Ar tikrai ištrinti šį administratorių? (t/n): ")
            if confirm.lower() == 't':
                # Adminai knygų neturi, bet vis tiek naudojame safe_delete nuoseklumui
                success, msg = library.safe_delete_user(user)
                print(f"\n{msg}")
                pause()
                break
                
        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()