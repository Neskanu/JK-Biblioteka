import os

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

def print_header(title):
    """Atspausdina gražią antraštę."""
    print("\n" + "="*50)
    print(f" {title.upper()}")
    print("="*50)

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