"""
FILE: src/data_manager.py
PURPOSE: Atsakingas už duomenų šaltinio inicializaciją.
RELATIONSHIPS:
  - Importuoja initialize_db iš src/database.py.
  - Naudojamas src/library.py.
CONTEXT:
  - Anksčiau valdė JSON failus. 
  - Dabar tai yra 'Dummy' klasė, kuri tiesiog užtikrina, kad DB lentelės sukurtos.
"""

from src.database import initialize_db

class DataManager:
    """
    Valdo duomenų persistenciją (išsaugojimą/užkrovimą).
    SQLAlchemy atveju dauguma metodų yra tušti, nes DB veikia realiu laiku.
    """
    
    def __init__(self):
        """
        Konstruktorius. Paleidžia duomenų bazės struktūros sukūrimą.
        """
        print("Inicijuojama duomenų bazė...")
        initialize_db()

    def load_data(self):
        """
        Suderinamumo metodas.
        SQL atveju duomenų nereikia 'užkrauti' į atmintį starto metu.
        """
        pass

    def save_data(self):
        """
        Suderinamumo metodas.
        SQL atveju duomenys įrašomi (commit) operacijų metu.
        """
        pass