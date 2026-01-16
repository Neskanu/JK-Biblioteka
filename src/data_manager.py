"""
FAILAS: src/data_manager.py
PASKIRTIS: Tvarko kelių nustatymą iki duomenų failų (JSON), veikiant tiek kodo, tiek .exe režimu.
RYŠIAI:
  - Naudojamas book_manager.py ir user_manager.py duomenų užkrovimui.
  - Importuoja sys ir os bibliotekas sistemos keliams nustatyti.
KONTEKSTAS:
  - Perrašytas, kad išspręstų "Frozen Path" problemą naudojant PyInstaller.
  - Užtikrina duomenų patvarumą (persistence) sukompiliuotoje versijoje.
"""

import sys
import json
import os

def get_base_path():
    """
    Nustato bazinį projekto kelią.
    
    Logika:
      - Jei programa sukompiliuota (sys.frozen), bazinis kelias yra ten, kur yra .exe failas.
      - Jei programa leidžiama kaip kodas, bazinis kelias yra projekto šaknis (dviem lygiais aukščiau).
    """
    if getattr(sys, 'frozen', False):
        # Sukompiliuota programa (.exe)
        # sys.executable nurodo patį .exe failą
        base_path = os.path.dirname(sys.executable)
    else:
        # Standartinis Python skriptas
        # __file__ yra src/data_manager.py -> dirname = src/ -> dirname = root
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(current_file)
        base_path = os.path.dirname(src_dir)
    
    return base_path

def get_data_file_path(filename):
    """
    Grąžina pilną kelią iki failų duomenų kataloge.
    """
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(src_dir)
    return os.path.join(project_root, 'data', filename)

def load_data(filepath):
    """
    Nuskaito duomenis iš JSON failo.
    
    Parametrai:
    - filepath: kelias iki failo (pvz., 'data/books.json').
    
    Grąžina:
    - list: Duomenų sąrašas (pvz., knygų žodynai).
    - Jei failo nėra arba jis sugadintas, grąžina tuščią sąrašą [].
    """
    # 1. Patikriname, ar failas egzistuoja
    if not os.path.exists(filepath):
        # Jei failo nėra (pirmas paleidimas), grąžiname tuščią sąrašą,
        # kad programa nenulūžtų.
        return []

    try:
        # 2. Atidarome failą skaitymui ('r' - read)
        # encoding='utf-8' būtinas lietuviškoms raidėms (ąčęė...)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except (json.JSONDecodeError, IOError):
        # Jei failas yra tuščias arba sugadintas (nevalidus JSON),
        # grąžiname tuščią sąrašą vietoj klaidos metimo.
        print(f"Įspėjimas: Failas {filepath} sugadintas arba tuščias. Pradedama nuo nulio.")
        return []

def save_data(filepath, data):
    """
    Įrašo duomenis į JSON failą.
    
    Parametrai:
    - filepath: kur saugoti.
    - data: sąrašas žodynų (list of dicts).
    """
    try:
        # 3. Užtikriname, kad egzistuoja direktorija (pvz., 'data/')
        # Jei aplanko 'data' nėra, os.makedirs jį sukurs.
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # 4. Atidarome failą rašymui ('w' - write)
        with open(filepath, 'w', encoding='utf-8') as f:
            # indent=4 padaro failą gražų ir skaitomą žmogui (su tarpais)
            # ensure_ascii=False leidžia įrašyti lietuviškas raides, o ne kodus
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    except IOError as e:
        print(f"Klaida įrašant į failą {filepath}: {e}")