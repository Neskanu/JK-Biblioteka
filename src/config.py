"""
FILE: src/config.py
PURPOSE: Centralizuota konfigūracijos saugykla.
CONTEXT:
  - Atnaujinta DEBUG versija: Rodo, kokius duomenis užkrauna.
  - Priverstinai ieško .env failo projekto šakniniame aplanke.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Randame tikslų kelią iki .env failo
# (Šis failas yra src/config.py, todėl .env yra vienu lygiu aukščiau)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

print(f"DEBUG: Ieškoma .env failo čia: {ENV_PATH}")

# 2. Užkrauname konfigūraciją
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print("DEBUG: .env failas RASTAS ir užkrautas.")
else:
    print("!!! DĖMESIO !!! .env failas NERASTAS. Naudojami numatytieji nustatymai.")

# --- DUOMENŲ BAZĖS KONFIGŪRACIJA ---
DB_USER = os.getenv('DB_USER', 'DB')
DB_PASSWORD = os.getenv('DB_PASSWORD', '') 
DB_HOST = os.getenv('DB_HOST', '127.0.0.1') # Pakeistas default į 127.0.0.1
DB_NAME = os.getenv('DB_NAME', 'jk_biblioteka')
DB_PORT = os.getenv('DB_PORT', '3306')

# Spausdiname, ką programa mato (saugumo sumetimais slepiame slaptažodį)
print(f"DEBUG: Konfigūracija -> Host: {DB_HOST}, User: {DB_USER}, DB: {DB_NAME}")
if len(DB_PASSWORD) > 0:
    print("DEBUG: Slaptažodis užkrautas (nėra tuščias).")
else:
    print("!!! KLAIDA: Slaptažodis yra tuščias! Patikrinkite .env failą.")

# SQLAlchemy Connection String
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- VERSLO TAISYKLĖS ---
LOAN_PERIOD_DAYS = 14
MAX_BOOKS_PER_USER = 5
FINE_PER_DAY = 0.50
DATE_FORMAT = "%Y-%m-%d"