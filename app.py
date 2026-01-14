"""
FILE: app.py
PURPOSE: Streamlit web sąsaja JK Bibliotekai.
RELATIONSHIPS:
  - Bendrauja tiesiogiai su src.library.Library klase.
  - Pakeičia konsolinį UI.
"""

import streamlit as st
import pandas as pd
from src.library import Library

# --- KONFIGŪRACIJA ---
st.set_page_config(
    page_title="Justo Kvederio Vardo Biblioteka",
    page_icon="📚",
    layout="wide"
)

# --- SESIJOS VALDYMAS (State Management) ---
# Streamlit kodas vykdomas iš naujo kaskart paspaudus mygtuką.
# Todėl bibliotekos objektą ir prisijungusį vartotoją saugome sesijoje.

if 'library' not in st.session_state:
    st.session_state.library = Library()

if 'user' not in st.session_state:
    st.session_state.user = None

library = st.session_state.library

# --- PAGALBINĖS FUNKCIJOS ---

def login():
    st.markdown("## 🔐 Prisijungimas")
    
    tab1, tab2 = st.tabs(["Skaitytojas", "Bibliotekininkas"])
    
    with tab1:
        with st.form("reader_login"):
            card_id = st.text_input("Kortelės ID (pvz., AB1234)")
            submit = st.form_submit_button("Prisijungti")
            
            if submit:
                user = library.user_manager.get_user_by_id(card_id)
                if user and user.role == 'reader':
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Neteisingas ID arba vartotojas nerastas.")

    with tab2:
        with st.form("admin_login"):
            username = st.text_input("Vartotojo vardas")
            password = st.text_input("Slaptažodis", type="password")
            submit = st.form_submit_button("Prisijungti")
            
            if submit:
                user = library.user_manager.authenticate_librarian(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Neteisingi prisijungimo duomenys.")

def logout():
    st.session_state.user = None
    st.rerun()

# --- BIBLIOTEKININKO SĄSAJA ---

def admin_dashboard():
    st.sidebar.title(f"👤 {st.session_state.user.username} (Admin)")
    menu = st.sidebar.radio("Meniu", ["Statistika", "Knygų valdymas", "Vartotojai", "Vėluojančios knygos"])
    
    if st.sidebar.button("Atsijungti"):
        logout()

    if menu == "Statistika":
        st.header("📊 Bibliotekos Statistika")
        
        # Gauname statistiką
        books = library.book_manager.get_all_books()
        borrowed = len([b for b in books if b.available_copies < b.total_copies])
        users_count = len(library.user_manager.users)
        stats = library.get_advanced_statistics()
        
        # Atvaizduojame korteles (Metrics)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Vartotojai", users_count)
        col2.metric("Knygų fondas", len(books))
        col3.metric("Paskolinta", borrowed)
        col4.metric("Laisva", len(books) - borrowed)
        
        st.divider()
        st.subheader("Išplėstinė analizė")
        st.info(f"📚 **Populiariausias žanras:** {stats.get('inventory_top_genre', '-')}")
        st.info(f"📖 **Skaitytojai renkasi:** {stats.get('borrowed_top_genre', '-')}")
        st.warning(f"⚠️ **Vid. vėlavimas:** {stats.get('avg_overdue_per_reader', '0')} knygos/žm.")

    elif menu == "Knygų valdymas":
        st.header("📚 Knygų Valdymas")
        
        with st.expander("Pridėti naują knygą"):
            with st.form("add_book"):
                title = st.text_input("Pavadinimas")
                author = st.text_input("Autorius")
                genre = st.text_input("Žanras")
                year = st.number_input("Metai", min_value=1000, max_value=2030, step=1)
                submit = st.form_submit_button("Pridėti knygą")
                
                if submit:
                    if title and author:
                        library.book_manager.add_book(title, author, int(year), genre)
                        st.success(f"Knyga '{title}' pridėta!")
                    else:
                        st.error("Būtina įvesti pavadinimą ir autorių.")
        
        # Rodyti knygų lentelę
        books = library.book_manager.get_all_books()
        if books:
            # Konvertuojame objektus į dict sąrašą DataFrame'ui
            data = [b.to_dict() for b in books]
            df = pd.DataFrame(data)
            # Paslepiame ID stulpelį, nes jis ilgas ir negražus
            st.dataframe(df.drop(columns=['id']), width='stretch')
        else:
            st.info("Biblioteka tuščia.")

    elif menu == "Vartotojai":
        st.header("👥 Vartotojų Sąrašas")
        users = library.user_manager.users
        if users:
            data = [{"ID": u.id, "Vardas": u.username, "Rolė": u.role} for u in users]
            st.dataframe(pd.DataFrame(data), width='stretch')

    elif menu == "Vėluojančios knygos":
        st.header("⚠️ Vėluojančios Knygos")
        overdue = library.get_all_overdue_books()
        if overdue:
            st.dataframe(pd.DataFrame(overdue), width='stretch')
        else:
            st.success("Vėluojančių knygų nėra! 🎉")

# --- SKAITYTOJO SĄSAJA ---

def reader_dashboard():
    user = st.session_state.user
    st.sidebar.title(f"👋 Sveiki, {user.username}")
    st.sidebar.info(f"Kortelė: {user.id}")
    
    menu = st.sidebar.radio("Meniu", ["Mano knygos", "Knygų katalogas"])
    
    if st.sidebar.button("Atsijungti"):
        logout()

    if menu == "Mano knygos":
        st.header("📚 Mano Pasiimtos Knygos")
        
        if not user.active_loans:
            st.info("Neturite pasiėmę jokių knygų.")
        else:
            # Rodome lentelę
            loans_df = pd.DataFrame(user.active_loans)
            st.dataframe(loans_df, width='stretch')
            
            # Grąžinimo forma
            st.divider()
            st.subheader("Grąžinti knygą")
            
            # Sudarome sąrašą pasirinkimui
            loan_options = {f"{l['title']} (iki {l['due_date']})": l['book_id'] for l in user.active_loans}
            selected_loan_text = st.selectbox("Pasirinkite knygą grąžinimui", list(loan_options.keys()))
            
            if st.button("Grąžinti pasirinktą knygą"):
                book_id = loan_options[selected_loan_text]
                success, msg = library.return_book(user.id, book_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            
            if st.button("Grąžinti VISAS knygas", type="primary"):
                success, msg = library.return_all_books(user.id)
                st.success(msg)
                st.rerun()

    elif menu == "Knygų katalogas":
        st.header("🔎 Katalogas")
        
        # Paieška
        search_query = st.text_input("Ieškoti pagal pavadinimą arba autorių")
        
        if search_query:
            books = library.book_manager.search_books(search_query)
        else:
            # Rodome tik laisvas knygas pagal nutylėjimą
            all_books = library.book_manager.get_all_books()
            books = [b for b in all_books if b.available_copies > 0]
        
        if books:
            for book in books:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(f"{book.title}")
                        st.caption(f"{book.author} | {book.year} | {book.genre}")
                        st.text(f"Likutis: {book.available_copies}/{book.total_copies}")
                    with col2:
                        # Unikalus raktas mygtukui būtinas cikle
                        if st.button("Pasiimti", key=f"borrow_{book.id}"):
                            success, msg = library.borrow_book(user.id, book.id)
                            if success:
                                st.toast(msg, icon="✅")
                                st.rerun() # Perkrauname, kad atsinaujintų likučiai
                            else:
                                st.toast(msg, icon="❌")
        else:
            st.warning("Knygų nerasta.")

# --- PAGRINDINIS PROGRAMOS CIKLAS ---

def main():
    if st.session_state.user is None:
        login()
    else:
        if st.session_state.user.role == 'librarian':
            admin_dashboard()
        elif st.session_state.user.role == 'reader':
            reader_dashboard()

if __name__ == "__main__":
    main()