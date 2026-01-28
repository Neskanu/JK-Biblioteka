"""
FILE: app.py
PURPOSE: Pagrindinis aplikacijos paleidimo failas (Entry Point).
RELATIONSHIPS:
  - Inicijuoja duomenų bazę ir Library servisą.
  - Valdo navigaciją tarp Prisijungimo, Admin ir Skaitytojo sąsajų.
CONTEXT:
  - Pataisyta: Pridėtas 'return' po prisijungimo lango, kad kodas nelūžtų.
  - Pataisyta: Suvienodinti funkcijų pavadinimai (render_dashboard).
"""

import streamlit as st
from src.library import Library
from src.web import auth, admin_ui, reader_ui
from src.database import initialize_db

# --- KONFIGŪRACIJA (Turi būti pirma) ---
st.set_page_config(
    page_title="JK Biblioteka",
    page_icon="📚",
    layout="wide"
)

# --- INICIALIZACIJA ---
def init_app():
    """Užtikrina, kad DB ir Library objektas egzistuoja sesijoje."""
    if 'initialized' not in st.session_state:
        initialize_db()
        st.session_state.initialized = True
        
    if 'library' not in st.session_state:
        st.session_state.library = Library()

    if 'user' not in st.session_state:
        st.session_state.user = None

def main():
    init_app()
    
    # 1. Jei vartotojas neprisijungęs -> Rodome Login ir stabdome
    if not st.session_state.user:
        auth.render_login()
        return # SVARBU: Čia sustojame, kad toliau kodas nebebūtų vykdomas
        
    # 2. Jei vartotojas prisijungęs -> Gauname duomenis
    user = st.session_state.user
    library = st.session_state.library
    
    # 3. Nukreipiame pagal rolę
    # Pastaba: user yra SQLAlchemy objektas, todėl pasiekiame atributą .role
    if user.role == 'librarian':
        # Admin UI reikalauja library objekto
        admin_ui.render_dashboard(library) 
    elif user.role == 'reader':
        # Reader UI pasiima library iš session_state, bet dėl saugumo galime ir paduoti
        reader_ui.render_dashboard()
    else:
        st.error(f"Neatpažinta rolė: {user.role}")

if __name__ == "__main__":
    main()