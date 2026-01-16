"""
FAILAS: src/data_manager.py
PASKIRTIS: Tvarko duomenų (JSON) užkrovimą ir saugojimą su detaliu registravimu (logging).
RYŠIAI:
  - Naudojamas book_manager.py ir user_manager.py duomenų operacijoms.
  - Generuoja 'debug.log' failą šalia vykdomosios programos.
KONTEKSTAS:
  - Pridėtas logging funkcionalumas padeda diagnozuoti problemas sukompiliuotoje versijoje.
"""

import json
import os
import sys
import logging

# --- LOGGING KONFIGŪRACIJA ---

# Nustatome, kur kurti log failą. 
# Jei programa sukompiliuota (.exe), logas bus šalia jos.
# Jei leidžiama per Python, logas bus šalia šio skripto.
if getattr(sys, 'frozen', False):
    base_log_dir = os.path.dirname(sys.executable)
else:
    base_log_dir = os.path.dirname(os.path.abspath(__file__))

log_file_path = os.path.join(base_log_dir, 'debug.log')

# Konfigūruojame logerį: rašysime laiką, lygį (INFO/ERROR) ir žinutę
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8' # Būtina lietuviškiems simboliams
)

logging.info("--- DUOMENŲ VALDYMO MODULIS INICIJUOTAS ---")

def get_base_path():
    """
    Nustato bazinį projekto kelią.
    """
    if getattr(sys, 'frozen', False):
        # .exe režimas: kelias iki .exe failo katalogo
        path = os.path.dirname(sys.executable)
        logging.debug(f"[PATH] Veikiama .exe režimu. Bazinė direktorija: {path}")
        return path
    else:
        # Skripto režimas: grįžtame du lygius aukštyn nuo src/data_manager.py
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logging.debug(f"[PATH] Veikiama Python skripto režimu. Bazinė direktorija: {path}")
        return path

def get_data_file_path(filename):
    """
    Grąžina pilną kelią iki failų duomenų kataloge ir tai užfiksuoja.
    """
    base_path = get_base_path()
    full_path = os.path.join(base_path, 'data', filename)
    logging.debug(f"[PATH] Sukonstruotas kelias failui '{filename}': {full_path}")
    return full_path

def load_data(filepath):
    """
    Nuskaito duomenis iš JSON failo su registravimu.
    """
    logging.info(f"[READ] Bandoma nuskaityti failą: {filepath}")

    if not os.path.exists(filepath):
        logging.warning(f"[READ] Failas NERASTAS: {filepath}")
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"[READ] Sėkmingai nuskaityta įrašų: {len(data)}")
            return data
            
    except json.JSONDecodeError as e:
        logging.error(f"[READ] JSON struktūros klaida faile {filepath}: {e}")
        return []
    except Exception as e:
        logging.critical(f"[READ] Kritinė klaida skaitant failą {filepath}: {e}")
        return []

def save_data(filepath, data):
    """
    Įrašo duomenis į JSON failą su registravimu.
    """
    logging.info(f"[WRITE] Bandoma įrašyti {len(data)} įrašų į: {filepath}")
    
    try:
        # Užtikriname, kad egzistuoja direktorija
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"[WRITE] Sukurta trūkstama direktorija: {directory}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info(f"[WRITE] Duomenys sėkmingai išsaugoti.")
            
    except Exception as e:
        logging.error(f"[WRITE] Klaida įrašant į failą {filepath}: {e}")