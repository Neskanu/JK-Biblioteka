from src.ui.common import print_header, pause, clear_screen

def run(library):
    """Vartotojų valdymo sub-meniu."""
    while True:
        clear_screen()
        print_header("VARTOTOJŲ VALDYMAS")
        print("1. Registruoti naują Skaitytoją")
        print("2. Registruoti naują Bibliotekininką")
        print("0. Grįžti atgal")

        choice = input("\nPasirinkimas: ")

        if choice == '1':
            print("\n--- Skaitytojo Registracija ---")
            name = input("Vartotojo vardas: ")
            new_user = library.user_manager.register_reader(name)
            
            if new_user:
                print(f"Skaitytojas '{new_user.username}' sukurtas!")
                print(f"KORTELĖS ID: [ {new_user.id} ]")
                print("(Būtinai perduokite šį ID skaitytojui)")
            else:
                print("Klaida: Vartotojas tokiu vardu jau egzistuoja.")
            pause()

        elif choice == '2':
            print("\n--- Kolegos Registracija ---")
            name = input("Vartotojo vardas: ")
            pwd = input("Slaptažodis: ")
            if library.user_manager.register_librarian(name, pwd):
                print("Bibliotekininkas užregistruotas.")
            else:
                print("Vartotojas jau egzistuoja.")
            pause()

        elif choice == '0':
            break
        else:
            print("Neteisingas pasirinkimas.")
            pause()