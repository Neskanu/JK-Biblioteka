"""
FILE: app.py
PURPOSE: Pagrindinis Streamlit aplikacijos taškas.
RELATIONSHIPS:
  - Inicijuoja src.library.Library
  - Nukreipia į src.web.auth, admin_ui arba reader_ui
"""

import streamlit as st
from src.library import Library
from src.web import auth, admin_ui, reader_ui
from src.database import initialize_db  # <--- PRIDĖTI ŠĮ IMPORTĄ

initialize_db()

# --- KONFIGŪRACIJA ---
st.set_page_config(
    page_title="JK Biblioteka",
    page_icon="📚",
    layout="wide"
)

# --- SESIJOS INICIJAVIMAS ---
if 'library' not in st.session_state:
    initialize_db() # <--- SVARBU: Iškviesti funkciją čia, PRIEŠ Library()
    st.session_state.library = Library()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- NAVIGACIJA ---
def main():
    if not st.session_state.user:
        # Prisijungimo langas
        auth.render_login()
    else:
        # Pagrindinis meniu pagal rolę
        user = st.session_state.user
        
        if user.role == 'librarian':
            admin_ui.show_admin_ui()
        elif user.role == 'reader':
            reader_ui.render_dashboard() 
            
if __name__ == "__main__":
    main()