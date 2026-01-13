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

def draw_ascii_table(headers, rows):
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

    # Pridedame šiek tiek tarpo (2 simbolius) kiekvienam stulpeliui dėl skaitomumo
    col_widths = [w + 2 for w in col_widths]

    # 3. Pagalbinės funkcijos linijų piešimui
    def _draw_separator(chars):
        # chars yra tuple: (kairysis_kampas, horizontali, kryžkelė, dešinysis_kampas)
        line = chars[0] + chars[2].join([chars[1] * w for w in col_widths]) + chars[3]
        print(line)

    def _draw_row(row_data):
        # Formatuojame tekstą dinamiškai pagal apskaičiuotus pločius
        # {:{w}} lygiuoja tekstą kairėje su pločiu w
        row_str = "│" + "│".join([f" {cell:<{w-1}}" for cell, w in zip(row_data, col_widths)]) + "│"
        print(row_str)

    # 4. Lentelės atvaizdavimas
    # Viršutinis rėmelis
    _draw_separator(("┌", "─", "┬", "┐"))
    
    # Antraštė
    _draw_row(headers)
    
    # Antraštės skirtukas
    _draw_separator(("├", "─", "┼", "┤"))
    
    # Duomenų eilutės
    for row in str_rows:
        _draw_row(row)
        
    # Apatinis rėmelis
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