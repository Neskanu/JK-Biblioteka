"""
FAILAS: src/ui/ascii_styler.py
PASKIRTIS: Suteikia centralizuotą variklį ASCII stiliaus UI elementų atvaizdavimui.
RYŠIAI:
  - Importuojamas UI valdiklių (pvz., src/ui/librarian/books_menu.py)
  - Nepriklausomas nuo verslo logikos (neimportuoja User ar Book modelių tiesiogiai)
APRAŠYMAS:
  Šis modulis atlieka matematinius skaičiavimus, reikalingus dinamiškam teksto
  lygiavimui lentelėse ir meniu, užtikrinant vienodą vizualinį stilių visoje programoje.
"""

from turtle import title


def draw_ascii_table(headers, rows, title=None):
    """
    Atvaizduoja dinaminę ASCII lentelę pagal pateiktas antraštes ir eilučių duomenis.
    
    Argumentai:
        headers (list): Eilučių sąrašas su antraštėmis.
        rows (list): Sąrašas sąrašų, kur kiekvienas vidinis sąrašas yra duomenų eilutė.
        
    Grąžina:
        None (Spausdina tiesiai į terminalą).
    """
    if not headers or not rows:
        print(">> Nėra duomenų atvaizdavimui.")
        return

    # 1. Konvertuojame visus duomenis į string tipą, kad len() veiktų teisingai
    # Kuriame naują matricą, kad nemodifikuotume originalių objektų
    str_rows = [[str(cell) for cell in row] for row in rows]
    
    # 2. Apskaičiuojame maksimalų plotį kiekvienam stulpeliui
    # Pradedame nuo antraščių ilgio
    col_widths = [len(h) for h in headers]
    
    for row in str_rows:
        for i, cell in enumerate(row):
            # Jei duomenų ląstelė platesnė nei esamas maksimumas, atnaujiname jį
            if len(cell) > col_widths[i]:
                col_widths[i] = len(cell)

    # Pridedame šiek tiek tarpų (2 simbolius) kiekvienam stulpeliui dėl skaitomumo
    col_widths = [w + 2 for w in col_widths]

    # 3. Jei yra pavadinimas, patikriname, ar nereikia išplėsti lentelės
    # Lentelės plotis = sum(stulpeliai) + (stulpelių_skaičius - 1) * 1 (tarpai) + 2 (šoniniai rėmeliai)
    # Tačiau paprastesnis skaičiavimas: sum(col_widths) + len(col_widths) + 1
    total_table_width = sum(col_widths) + len(col_widths) + 1
    
    if title:
        # Pavadinimo plotis su rėmeliais: len(title) + 4 (tarpai + rėmeliai)
        required_width = len(title) + 4
        if required_width > total_table_width:
            # Jei pavadinimas netelpa, likusį plotį pridedame prie paskutinio stulpelio
            diff = required_width - total_table_width
            col_widths[-1] += diff
            # Atnaujiname bendrą plotį
            total_table_width += diff

    # 4. Pagalbinės funkcijos linijų piešimui
    def _draw_separator(chars):
        # chars yra tuple: (kairysis_kampas, horizontali, kryžkelė, dešinysis_kampas)
        line = chars[0] + chars[2].join([chars[1] * w for w in col_widths]) + chars[3]
        print(line)

    def _draw_row(row_data):
        # Formatuojame tekstą dinamiškai pagal apskaičiuotus pločius
        # Užpildome tuščiomis reikšmėmis, jei eilutė trumpesnė už antraštes
        current_row = row_data + [""] * (len(col_widths) - len(row_data))
        # {:{w}} lygiuoja tekstą kairėje su pločiu w
        row_str = "│" + "│".join([f" {cell:<{w-1}}" for cell, w in zip(row_data, col_widths)]) + "│"
        print(row_str)

    # 5. Atvaizdavimas
    if title:
        # Piešiamas pavadinimo blokas
        print(f"┌{'─' * (total_table_width - 2)}┐")
        print(f"│{title.center(total_table_width - 2)}│")
        # Viršutinis rėmelis, kuris jungia pavadinimą su stulpeliais (naudojame ├ ir ┤)
        _draw_separator(("├", "─", "┬", "┤"))
    else:
        # Standartinis viršus
        _draw_separator(("┌", "─", "┬", "┐"))
    
    # Antraštės
    _draw_row(headers)
    
    # Skirtukas po antraštėmis
    _draw_separator(("├", "─", "┼", "┤"))
    
    # Duomenys
    for row in str_rows:
        _draw_row(row)
        
    # Apačia
    _draw_separator(("└", "─", "┴", "┘"))


def draw_ascii_menu(title, options):
    """
    Atvaizduoja centruotą ASCII meniu dėžutę.
    
    Argumentai:
        title (str): Meniu pavadinimas.
        options (list): Eilučių sąrašas (meniu punktai) arba tuple (raktas, aprašymas).
    """
    # Nustatome meniu plotį pagal ilgiausią pasirinkimą arba pavadinimą
    # Dėl estetikos nustatome minimalų 40 simbolių plotį
    max_len = max(len(title), 40)
    
    # Tikriname pasirinkimų ilgius
    for opt in options:
        text = opt if isinstance(opt, str) else f"{opt[0]}. {opt[1]}"
        if len(text) > max_len:
            max_len = len(text)
            
    # Pridedame rėmelio plotį
    width = max_len + 4

    print(f"┌{'─' * width}┐")
    print(f"│{title.center(width)}│")
    print(f"├{'─' * width}┤")
    
    for opt in options:
        # Apdorojame tiek paprastus tekstus, tiek (raktas, aprašymas) poras
        if isinstance(opt, tuple):
            text = f"{opt[0]}. {opt[1]}"
        else:
            text = str(opt)
            
        print(f"│  {text:<{width-2}}│")
        
    print(f"└{'─' * width}┘")

def print_header(title):
    """Atspausdina gražią antraštę (liko iš seniau, turėtų piešti arba kaip meniu, arba kaip lentelę)."""
    print("\n" + "="*50)
    print(f" {title.upper()}")
    print("="*50)