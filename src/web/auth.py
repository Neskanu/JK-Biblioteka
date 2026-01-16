"""
FILE: src/web/auth.py
PURPOSE: Tvarko vartotojų prisijungimą ir atsijungimą.
"""

import streamlit as st

def login_page():
    st.markdown("## 🔐 Prisijungimas prie Bibliotekos")
    
    tab1, tab2 = st.tabs(["Skaitytojas", "Bibliotekininkas"])
    
    library = st.session_state.library
    
    # --- SKAITYTOJO PRISIJUNGIMAS ---
    with tab1:
        with st.form("reader_login"):
            card_id = st.text_input("Kortelės ID (pvz., AB1234)")
            submit = st.form_submit_button("Prisijungti")
            
            if submit:
                user = library.user_repository.get_by_id(card_id)
                if user and user.role == 'reader':
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Neteisingas ID arba vartotojas nerastas.")

    # --- ADMIN PRISIJUNGIMAS ---
    with tab2:
        with st.form("admin_login"):
            username = st.text_input("Vartotojo vardas")
            password = st.text_input("Slaptažodis", type="password")
            submit = st.form_submit_button("Prisijungti")
            
            if submit:
                user = library.auth_service.authenticate_librarian(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Neteisingi prisijungimo duomenys.")

def logout():
    st.session_state.user = None
    st.rerun()