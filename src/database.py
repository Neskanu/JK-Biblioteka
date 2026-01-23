"""
FILE: src/database.py
PURPOSE: Valdo tiesioginį ryšį su SQLite duomenų baze ir lentelių kūrimą.
RELATIONSHIPS:
  - Naudojamas src/book_manager.py ir src/user_manager.py duomenų operacijoms.
  - Pakeičia senąjį src/data_manager.py funkcionalumą.
CONTEXT:
  - Centralizuota vieta SQL užklausų vykdymui užtikrina, kad nereikia kartoti prisijungimo kodo.
"""

import sqlite3
import os

# Nustatome DB failo vietą
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'library.db')

def get_connection():
    """
    Sukuria ir grąžina ryšį su duomenų baze.
    Nustatome row_factory, kad galėtume pasiekti stulpelius pagal pavadinimą.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Leidžia rezultatus pasiekti kaip dict: row['title']
    return conn

def initialize_db():
    """
    Sukuria reikiamas lenteles, jei jos dar neegzistuoja.
    Šią funkciją reikia iškviesti programos paleidimo pradžioje (main.py).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Knygų lentelė
    # Naudojame TEXT id, nes jūsų sistema generuoja UUID
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            total_copies INTEGER DEFAULT 1,
            available_copies INTEGER DEFAULT 1
        )
    ''')

    # 2. Vartotojų lentelė
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            password TEXT -- Gali būti NULL skaitytojams
        )
    ''')

    # 3. Paskolų (Loans) lentelė - Svarbiausias pokytis
    # Vietoje sąrašo JSON faile, čia turime atskirą įrašą kiekvienam paskolinimui.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            book_id TEXT NOT NULL,
            due_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Duomenų bazė inicijuota: {DB_FILE}")