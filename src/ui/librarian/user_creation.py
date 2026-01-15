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
    
    # 1. Gauti vartotojo vardą
    while True:
        name = input("Vartotojo vardas: ").strip()
        if name:
            break
        print("Vardas negali būti tuščias.")

    print("Įveskite kortelės kodą (Formatas: XX1111)")
    print("Arba palikite tuščią, kad atšauktumėte.")

    # 2. Pridėti kortelę ir registruoti
    while True:
        card_id = input("Kortelės ID: ").strip().upper()
        
        # Leidžiame atšaukti, jei bibliotekininkas neturi kortelės
        if not card_id:
            print("Registracija atšaukta.")
            pause()
            return

        # UI surenka abu parametrus ir siunčia į servisą
        success, msg = library.user_manager.register_reader(name, card_id)

        print(f"\n>> {msg}") # Išspausdiname rezultatą iš serviso
        
        if success:
            # Jei pavyko - laukiame paspaudimo ir išeiname iš funkcijos
            pause()
            break 
        else:
            # Jei nepavyko (pvz. blogas formatas), ciklas kartojasi
            pass

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