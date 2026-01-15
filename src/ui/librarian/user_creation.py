"""
FILE: src/ui/librarian/user_creation.py
PURPOSE: Atsakingas už naujų vartotojų (skaitytojų ir adminų) registraciją.
RELATIONSHIPS:
  - Importuoja UI pagalbines funkcijas is src/ui/common.py
  - Kviečiamas iš users_menu.py
CONTEXT:
  - Atskira logika kūrimui, kad nemaišytume su redagavimu.
"""

from src.ui.common import pause
from src.ui.ascii_styler import print_header

def register_reader(library):
    """Tvarko skaitytojo registracijos procesą."""
    print_header("Skaitytojo Registracija")
    name = input("Vartotojo vardas: ")
    if not name:
        print("Vardas negali būti tuščias.")
        pause()
        return

    new_user = library.user_manager.register_reader(name)
    if new_user:
        print(f"Skaitytojas sukurtas! ID: [ {new_user.id} ]")
        print("Būtinai perduokite šį ID skaitytojui.")
    else:
        print("Klaida: Nepavyko sukurti (galbūt vardas užimtas).")
    pause()

def register_librarian(library):
    """Tvarko bibliotekininko registracijos procesą."""
    print_header("Kolegos (Admin) Registracija")
    name = input("Vartotojo vardas: ")
    pwd = input("Slaptažodis: ")
    
    if not name or not pwd:
        print("Vardas ir slaptažodis yra privalomi.")
        pause()
        return

    if library.user_manager.register_librarian(name, pwd):
        print("Bibliotekininkas sėkmingai užregistruotas.")
    else:
        print("Vartotojas jau egzistuoja.")
    pause()