"""
FILE: src/config.py
PURPOSE: Centralizuota konfigūracijos ir konstantų saugykla.
RELATIONSHIPS:
  - Importuojamas įvairiuose servisuose (pvz., loan_service.py) ir validacijos moduliuose.
CONTEXT:
  - Leidžia lengvai keisti verslo taisykles (pvz., paskolos trukmę) vienoje vietoje,
    neliečiant logikos failų.
"""

# Skolinimo taisyklės
LOAN_PERIOD_DAYS = 14   # Kiek dienų galima laikyti knygą
MAX_BOOKS_PER_USER = 5  # Maksimalus knygų kiekis vienam skaitytojui

# Duomenų failų pavadinimai (jei ateityje reiktų keisti)
BOOKS_FILENAME = 'books.json'
USERS_FILENAME = 'users.json'
BACKUP_FILENAME = 'books_backup.json'

# Datos formatai
DATE_FORMAT = "%Y-%m-%d"