"""
FILE: src/web/auth.py
PURPOSE: Streamlit vartotojo sąsaja prisijungimui.
RELATIONSHIPS:
  - Kviečiama iš app.py.
  - Naudoja src/services/auth_service.py.
CONTEXT:
  - Atnaujinta: Atskirti prisijungimo langai Skaitytojui (be slaptažodžio) ir Adminui.
"""

import streamlit as st
from src.services.auth_service import AuthService

def render_login():
    """
    Atvaizduoja prisijungimo formą su dviem pasirinkimais: Skaitytojas arba Bibliotekininkas.
    """
    st.title("📚 Bibliotekos Sistema")
    
    # Centruojame
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        st.subheader("Prisijungimas")
        
        # Sukuriame skirtukus (Tabs)
        tab_reader, tab_admin = st.tabs(["👤 Skaitytojas", "🛡️ Bibliotekininkas"])
        
        # --- 1. SKAITYTOJO PRISIJUNGIMAS ---
        with tab_reader:
            with st.form("reader_login"):
                st.write("Įveskite savo vardą (arba ID):")
                username = st.text_input("Vartotojo vardas")
                submit_reader = st.form_submit_button("Prisijungti", type="primary")
                
                if submit_reader:
                    if username:
                        _perform_login(username, None) # Slaptažodis nereikalingas
                    else:
                        st.warning("Įveskite vardą.")

        # --- 2. BIBLIOTEKININKO PRISIJUNGIMAS ---
        with tab_admin:
            with st.form("admin_login"):
                st.write("Administracinė prieiga:")
                admin_user = st.text_input("Vartotojo vardas")
                admin_pass = st.text_input("Slaptažodis", type="password")
                submit_admin = st.form_submit_button("Prisijungti", type="primary")
                
                if submit_admin:
                    if admin_user and admin_pass:
                        _perform_login(admin_user, admin_pass)
                    else:
                        st.warning("Įveskite abu laukus.")

def _perform_login(username, password):
    """
    Vidinė funkcija atlikti prisijungimą per servisą.
    """
    # Kuriame servisą
    auth_service = AuthService() # Jis pats susikurs UserRepository viduje
    
    # Bandome autentifikuoti
    user = auth_service.authenticate(username, password)
    
    if user:
        # Sėkmės atveju
        st.session_state['user'] = user
        st.session_state['role'] = user.role
        
        st.success(f"Sveiki sugrįžę, {user.username}!")
        st.rerun()
    else:
        st.error("Neteisingi duomenys arba vartotojas nerastas.")

def logout():
    """Atsijungimo funkcija."""
    if 'user' in st.session_state:
        del st.session_state['user']
    if 'role' in st.session_state:
        del st.session_state['role']
    st.rerun()