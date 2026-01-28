"""
FILE: src/database.py
PURPOSE: Valdo ryšį su MySQL duomenų baze per PyMySQL.
RELATIONSHIPS:
  - Importuoja DB_CONFIG iš src/config.py.
  - Naudojamas Repozitorijose užklausų vykdymui.
CONTEXT:
  - Naudoja 'pymysql' biblioteką.
  - Automatiškai konfigūruoja DictCursor rezultatus.
"""

import pymysql
import pymysql.cursors
from src.config import DB_CONFIG

def get_connection():
    """
    Sukuria ir grąžina ryšį su MySQL duomenų baze.
    """
    # Išimame 'cursorclass' stringą iš config ir paverčiame tikra klase
    config = DB_CONFIG.copy()
    if 'cursorclass' in config:
        del config['cursorclass']
    
    try:
        conn = pymysql.connect(
            **config,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        print(f"Klaida jungiantis prie DB: {e}")
        raise

def initialize_db():
    """
    SVARBU: Sukuria duomenų bazę IR lenteles.
    """
    # 1. Prisijungiame prie MySQL SERVERIO (be duomenų bazės pasirinkimo)
    # Kad galėtume įvykdyti "CREATE DATABASE"
    server_config = DB_CONFIG.copy()
    target_db = server_config.pop('database') # Išimame DB pavadinimą laikinai
    if 'cursorclass' in server_config:
        del server_config['cursorclass']

    try:
        # Jungiamės tiesiog prie localhost (be db)
        conn = pymysql.connect(**server_config)
        with conn.cursor() as cursor:
            # Sukuriame duomenų bazę, jei nėra
            print(f"Tikrinama duomenų bazė: {target_db}...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {target_db} DEFAULT CHARACTER SET utf8mb4")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Klaida kuriant duomenų bazę: {e}")
        return # Jei nepavyko sukurti DB, toliau tęsti neverta

    # 2. Dabar jau kai DB egzistuoja, jungiames įprastai ir kuriame lenteles
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            
            # 1. Knygų lentelė
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id VARCHAR(36) PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    year INT,
                    genre VARCHAR(100),
                    total_copies INT DEFAULT 1,
                    available_copies INT DEFAULT 1
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # 2. Vartotojų lentelė
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    password VARCHAR(255)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # 3. Paskolų lentelė
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    book_id VARCHAR(36) NOT NULL,
                    title VARCHAR(255),
                    due_date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        
        conn.commit()
        conn.close()
        print("MySQL struktūra sėkmingai atnaujinta.")
    except Exception as e:
        print(f"Lentelių kūrimo klaida: {e}")