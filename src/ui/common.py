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

def pause():
    """Sustabdo ekraną, kad vartotojas spėtų perskaityti rezultatą."""
    input("\nSpauskite ENTER, kad tęstumėte...")