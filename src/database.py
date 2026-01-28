"""
FILE: src/database.py
PURPOSE: Valdo SQLAlchemy ORM sesijas ir ryšį su MySQL.
RELATIONSHIPS:
  - Importuoja DATABASE_URL iš src/config.py.
  - Naudojamas visuose Repositories ir Models failuose.
CONTEXT:
  - Pakeista iš raw PyMySQL į SQLAlchemy.
  - Naudoja 'scoped_session' geresniam darbui su Streamlit (thread-safety).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from src.config import DATABASE_URL

# 1. Sukuriame variklį (Engine)
# pool_recycle=3600 reikalinga MySQL, kad ryšys nenutrūktų po ilgo neveikimo
engine = create_engine(DATABASE_URL, pool_recycle=3600, echo=False)

# 2. Sukuriame sesijų gamyklą
# scoped_session užtikrina, kad kiekviena gija (thread) gaus savo atskirą sesiją.
# Tai kritiškai svarbu web aplikacijoms (pvz., Streamlit).
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# 3. Deklaratyvi bazinė klasė, nuo kurios paveldės visi modeliai
Base = declarative_base()

def get_db():
    """
    Pagalbinė funkcija sesijos gavimui (Dependency Injection stiliui).
    Užtikrina, kad sesija būtų uždaryta po darbo.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_db():
    """
    Sukuria lenteles duomenų bazėje, jei jų nėra.
    Kviečiama programos pradžioje.
    """
    import src.models  # Importuojame modelius, kad SQLAlchemy juos 'pamatytų'
    
    # Base.metadata.create_all patikrina DB ir sukuria trūkstamas lenteles
    Base.metadata.create_all(bind=engine)
    print("ORM: Duomenų bazės struktūra patikrinta/atnaujinta.")