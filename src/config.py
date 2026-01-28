"""
FILE: src/config.py
PURPOSE: Centralizuota konfigūracijos ir konstantų saugykla.
RELATIONSHIPS:
  - Importuojamas įvairiuose servisuose (pvz., loan_service.py) ir validacijos moduliuose.
CONTEXT:
  - Leidžia lengvai keisti verslo taisykles (pvz., paskolos trukmę) vienoje vietoje,
    neliečiant logikos failų.
"""
import os

# --- MySQL KONFIGŪRACIJA ---
DB_CONFIG = {
    'user': 'DB',           # Pakeiskite į savo MySQL vartotoją
    'password': 'msqVycia182!',           # Pakeiskite į savo slaptažodį
    'host': 'localhost',
    'database': 'jk_biblioteka',
    'charset': 'utf8mb4',
    'cursorclass': 'DictCursor' # Tai panaudosime database.py faile
}

# Skolinimo taisyklės
LOAN_PERIOD_DAYS = 14   # Kiek dienų galima laikyti knygą
MAX_BOOKS_PER_USER = 5  # Maksimalus knygų kiekis vienam skaitytojui
FINE_PER_DAY = 0.50 # 50 centų už dieną

# Duomenų failų pavadinimai (liko nuo sqlite implementacijos)
BOOKS_FILENAME = 'books.json'
USERS_FILENAME = 'users.json'
BACKUP_FILENAME = 'books_backup.json'

# Datos formatai
DATE_FORMAT = "%Y-%m-%d"