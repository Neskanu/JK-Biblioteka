import os
from datetime import datetime # <--- Reikia šito importo metams tikrinti

def clear_screen():
    """Išvalo terminalo ekraną (veikia ant Windows ir Mac/Linux)."""
    # 'nt' reiškia Windows
    if os.name == 'nt':
        os.system('cls')
    # Visi kiti (Mac, Linux)
    else:
        os.system('clear')

def pause():
    """Sustabdo ekraną, kad vartotojas spėtų perskaityti rezultatą."""
    input("\nSpauskite ENTER, kad tęstumėte...")

def get_int_input(prompt):
    """
    Prašo vartotojo įvesti skaičių tol, kol įves teisingai.
    Apsaugo programą nuo 'nulūžimo', jei įvedamos raidės.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Klaida: Prašome įvesti skaičių.")

def get_valid_string(prompt, min_length=1):
    """
    Prašo įvesti tekstą, kol jis atitinka minimalų ilgį.
    Taip pat automatiškai sutvarko tarpus.
    """
    while True:
        value = input(prompt).strip() # .strip() pašalina tarpus priekyje ir gale
        if len(value) >= min_length:
            # Galime automatiškai padaryti gražų formatavimą (Title Case)
            # Bet atsargiai - kai kurie pavadinimai turi būti specifiniai.
            # Paprasčiausias variantas - tiesiog grąžinti sutvarkytą stringą.
            return value
        print(f"Klaida: Laukas negali būti tuščias (min. {min_length} simb.).")

def get_valid_year(prompt):
    """
    Prašo įvesti metus. Turi būti skaičius, ir logiškame rėžyje.
    """
    current_year = datetime.now().year
    while True:
        try:
            value_str = input(prompt)
            value = int(value_str)
            
            # Rėžiai: Nuo Gutenberg'o spaudos (1400) iki kitų metų (leidyba į priekį)
            # Galite keisti rėžius pagal poreikį (pvz. nuo 0)
            if 1000 <= value <= current_year + 1:
                return value
            else:
                print(f"Klaida: Metai turi būti tarp 1000 ir {current_year + 1}.")
        except ValueError:
            print("Klaida: Įveskite sveikąjį skaičių (pvz., 2023).")

def get_positive_int(prompt):
    """Skaičius turi būti > 0."""
    while True:
        try:
            val = int(input(prompt))
            if val > 0:
                return val
            print("Skaičius turi būti teigiamas.")
        except ValueError:
            print("Įveskite skaičių.")

def select_object_from_list(objects, prompt="Pasirinkite numerį"):
    """
    Parodo objektų sąrašą su numeriais ir leidžia vartotojui pasirinkti vieną.
    Grąžina pasirinktą objektą arba None, jei atšaukia.
    """
    if not objects:
        print("Sąrašas tuščias.")
        return None

    print("\n--- Rasti rezultatai ---")
    # enumerate pradeda skaičiuoti nuo 0, todėl pridedame start=1, kad vartotojui rodytų 1, 2, 3...
    for index, obj in enumerate(objects, start=1):
        # Spausdiname: 1. Knygos Pavadinimas - Autorius
        print(f"{index}. {obj.title} - {obj.author} ({obj.year})")
    
    print("0. Atšaukti")
    print("-" * 30)

    while True:
        try:
            choice = int(input(f"{prompt} (0-{len(objects)}): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(objects):
                # Grąžiname objektą iš sąrašo (indeksas yra choice - 1)
                return objects[choice - 1]
            else:
                print("Blogas numeris. Bandykite dar kartą.")
        except ValueError:
            print("Įveskite skaičių.")