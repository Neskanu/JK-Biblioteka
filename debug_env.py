# FILE: debug_env.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Priverstinai užkrauname .env iš naujo
load_dotenv(override=True)

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')

print("\n--- DIAGNOSTIKA ---")
print(f"1. .env failas egzistuoja: {os.path.exists('.env')}")
print(f"2. Vartotojas (Python mato): '{user}'")
print(f"3. Host (Python mato): '{host}'")
if password:
    print(f"4. Slaptažodis: {len(password)} simbolių (Pirmas: '{password[0]}', Paskutinis: '{password[-1]}')")
else:
    print("4. Slaptažodis: NĖRA!")

# 5. Bandome jungtis tiesiogiai
print("\n--- BANDOMAS RYŠYS ---")
url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        print("Sėkmė! Prisijungimas pavyko.")
        res = conn.execute(text("SELECT VERSION()"))
        print(f"MySQL versija: {res.scalar()}")
except Exception as e:
    print(f"KLAIDA: {e}")