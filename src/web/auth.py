"""
FILE: src/web/auth.py
PURPOSE: Streamlit vartotojo sąsaja prisijungimui.
RELATIONSHIPS:
  - Naudoja src/services/auth_service.py.
CONTEXT:
  - Atnaujinta: Skaitytojai jungiasi su ID, Adminai su Vardu/Slaptažodžiu.
"""

import streamlit as st
from src.services.auth_service import AuthService

def render_login():
    st.title("📚 Bibliotekos Sistema")
    
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        st.subheader("Prisijungimas")
        
        tab_reader, tab_admin = st.tabs(["👤 Skaitytojas", "🛡️ Bibliotekininkas"])
        
        # --- 1. SKAITYTOJAS (Pagal ID) ---
        with tab_reader:
            with st.form("reader_login"):
                st.info("Įveskite savo Skaitytojo ID (pvz., UUID arba kortelės nr).")
                # Pakeistas label ir kintamojo pavadinimas
                reader_id = st.text_input("Skaitytojo ID")
                submit_reader = st.form_submit_button("Prisijungti", type="primary")
                
                if submit_reader:
                    if reader_id:
                        _perform_reader_login(reader_id.strip())
                    else:
                        st.warning("Įveskite ID.")

        # --- 2. ADMIN (Pagal Vardą) ---
        with tab_admin:
            with st.form("admin_login"):
                st.write("Administracinė prieiga:")
                admin_user = st.text_input("Vartotojo vardas")
                admin_pass = st.text_input("Slaptažodis", type="password")
                submit_admin = st.form_submit_button("Prisijungti", type="primary")
                
                if submit_admin:
                    if admin_user and admin_pass:
                        _perform_admin_login(admin_user.strip(), admin_pass.strip())
                    else:
                        st.warning("Įveskite abu laukus.")

def _perform_reader_login(user_id):
    """Prisijungimas tik su ID."""
    auth_service = AuthService()
    user = auth_service.authenticate_reader(user_id)
    
    if user:
        _set_session(user)
    else:
        st.error(f"Skaitytojas su ID '{user_id}' nerastas.")

def _perform_admin_login(username, password):
    """Prisijungimas su Vardu ir Slaptažodžiu."""
    auth_service = AuthService()
    user = auth_service.authenticate_admin(username, password)
    
    if user:
        _set_session(user)
    else:
        st.error("Neteisingas vardas arba slaptažodis.")

def _set_session(user):
    """Pagalbinė funkcija sesijos nustatymui."""
    st.session_state['user'] = user
    st.session_state['role'] = user.role
    st.success(f"Sveiki, {user.username}!")
    st.rerun()

def logout():
    if 'user' in st.session_state:
        del st.session_state['user']
    if 'role' in st.session_state:
        del st.session_state['role']
    st.rerun()