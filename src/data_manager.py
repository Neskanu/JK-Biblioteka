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
import logging

# --- LOGGING KONFIGŪRACIJA ---
# Nustatome, kur bus log failas.
# Jei tai .exe, log failas bus šalia .exe.
if getattr(sys, 'frozen', False):
    app_dir = os.path.dirname(sys.executable)
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(app_dir, 'debug.log')

# Konfigūruojame logerį
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8' # Svarbu lietuviškoms raidėms
)

# Pirmas įrašas paleidžiant modulį
logging.info(f"--- SISTEMA STARTUOJA ---")
logging.info(f"Vykdymo vieta (App Dir): {app_dir}")
logging.info(f"Ar sukompiliuota (Frozen): {getattr(sys, 'frozen', False)}")

def get_base_path():
    """
    Nustato bazinį projekto kelią.
    """
    if getattr(sys, 'frozen', False):
        # Sukompiliuota programa (.exe) -> Imame .exe failo aplanką
        base_path = os.path.dirname(sys.executable)
    else:
        # Skriptas -> Imame projekto šaknį (src tėvinį aplanką)
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(current_file)
        base_path = os.path.dirname(src_dir)
    
    return base_path

def get_data_file_path(filename):
    """
    Grąžina pilną kelią iki failo 'data' kataloge.
    SVARBU: Naudoja get_base_path(), kad veiktų ir sukompiliavus.
    """
    base_path = get_base_path()
    return os.path.join(base_path, 'data', filename)

def load_data(filepath):
    """
    Nuskaito duomenis iš JSON failo.
    """
    if not os.path.exists(filepath):
        # Naudojame logging, kad matytume, jog kuriamas naujas failas
        logging.info(f"Failas nerastas, bus sukurtas naujas: {filepath}")
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except (json.JSONDecodeError, IOError) as e:
        # Pakeista iš print į logging.warning
        logging.warning(f"Failas {filepath} sugadintas arba tuščias ({e}). Pradedama nuo nulio.")
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