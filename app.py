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

# --- KONFIGŪRACIJA ---
st.set_page_config(
    page_title="JK Biblioteka",
    page_icon="📚",
    layout="wide"
)

# --- SESIJOS INICIJAVIMAS ---
if 'library' not in st.session_state:
    st.session_state.library = Library()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- NAVIGACIJA ---
def main():
    if st.session_state.user is None:
        # Prisijungimo puslapis
        auth.login_page() 
    else:
        # Patikriname rolę ir rodome atitinkamą UI
        if st.session_state.user.role == 'librarian':
            # ČIA BUVO KLAIDA: Pridedame argumentą (st.session_state.library)
            admin_ui.render_dashboard(st.session_state.library)
            
        elif st.session_state.user.role == 'reader':
            # Tikėtina, kad ir reader_ui ateityje reikės bibliotekos objekto
            # Jei reader_ui.render_dashboard() dar nepakeista, šis pakeitimas gali mesti klaidą.
            # Jei reader_ui dar senas, palikite skliaustus tuščius: reader_ui.render_dashboard()
            # Bet geriausia praktika - perduoti visur.
            try:
                reader_ui.render_dashboard(st.session_state.library)
            except TypeError:
                reader_ui.render_dashboard()

if __name__ == "__main__":
    main()