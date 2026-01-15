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
    
    with st.sidebar:
        st.title(f"👋 Sveiki, {user.username}")
        st.info(f"Kortelė: {user.id}")
        
        menu = st.radio(
            "Meniu", 
            ["Knygų katalogas", "Mano knygos"],
            captions=["Ieškoti ir pasiimti knygas", "Grąžinti turimas knygas"]
        )
        
        st.divider()
        if st.button("Atsijungti", type="primary", width=stretch):
            logout()

    # --- 1. KNYGŲ KATALOGAS (INTERAKTYVI LENTELĖ) ---
    if menu == "Knygų katalogas":
        st.header("🔎 Knygų Katalogas")
        
        all_books = library.book_manager.get_all_books()
        if not all_books:
            st.warning("Biblioteka tuščia.")
            return

        # 1. Paruošiame duomenis
        # Rodome tik tas knygas, kurias galima pasiimti (available > 0), 
        # arba visas su indikacija. Kad būtų paprasčiau - rodome visas, bet leidžiame rinktis.
        
        data = []
        for b in all_books:
            # Sukuriame žodyną kiekvienai eilutei
            row = b.to_dict()
            # Pridedame stulpelį "Pasirinkti", kuris pradžioje yra False (nepažymėtas)
            row['Pasirinkti'] = False
            # Pridedame formatuotą likutį
            row['Likutis'] = f"{b.available_copies}/{b.total_copies}"
            data.append(row)

        df = pd.DataFrame(data)

        # Filtravimas (Paieška)
        search_query = st.text_input("🔍 Paieška (Pavadinimas/Autorius)")
        if search_query:
            mask = (
                df['title'].str.contains(search_query, case=False) | 
                df['author'].str.contains(search_query, case=False)
            )
            df = df[mask]

        # 2. Interaktyvi lentelė (st.data_editor)
        # column_config leidžia konfigūruoti, kaip atrodo stulpeliai (pvz., checkbox)
        
        st.caption("Pažymėkite varneles prie knygų, kurias norite pasiimti 👇")
        
        edited_df = st.data_editor(
            df,
            key="catalog_editor", # Svarbu unikalus raktas
            column_config={
                "Pasirinkti": st.column_config.CheckboxColumn(
                    "Imti?",
                    help="Pažymėkite norėdami pasiimti",
                    default=False,
                    width=small
                ),
                "title": "Pavadinimas",
                "author": "Autorius",
                "year": "Metai",
                "genre": "Žanras",
                "Likutis": "Laisva vnt.",
            },
            # Paslepiame techninius stulpelius
            disabled=["title", "author", "year", "genre", "Likutis"], # Neleidžiame redaguoti teksto
            hide_index=True,
            column_order=["Pasirinkti", "title", "author", "year", "genre", "Likutis"] # Pirmas stulpelis - varnelė
        )

        # 3. Veiksmo mygtukas
        # Išfiltruojame tik tas eilutes, kurias vartotojas pažymėjo (kur 'Pasirinkti' yra True)
        selected_books = edited_df[edited_df['Pasirinkti'] == True]
        
        if not selected_books.empty:
            count = len(selected_books)
            st.info(f"Pasirinkote knygų: {count}")
            
            if st.button(f"Pasiimti pasirinktas ({count})", type="primary"):
                success_count = 0
                errors = []
                
                # Iteruojame per pasirinktas knygas ir bandome skolintis
                for index, row in selected_books.iterrows():
                    success, msg = library.borrow_book(user.id, row['id'])
                    if success:
                        success_count += 1
                    else:
                        errors.append(f"{row['title']}: {msg}")
                
                # Rezultatų atvaizdavimas
                if success_count > 0:
                    st.toast(f"Sėkmingai paimta knygų: {success_count}!", icon="✅")
                
                if errors:
                    for err in errors:
                        st.error(err)
                
                if success_count > 0:
                    # Palaukiame ir perkrauname, kad atsinaujintų sąrašas
                    import time
                    time.sleep(1.5)
                    st.rerun()

    # --- 2. MANO KNYGOS (INTERAKTYVI LENTELĖ) ---
    elif menu == "Mano knygos":
        st.header("📚 Mano Pasiimtos Knygos")
        
        if not user.active_loans:
            st.info("Šiuo metu neturite pasiskolinę knygų.")
        else:
            # Paruošiame duomenis su checkbox
            data = []
            for loan in user.active_loans:
                # loan yra žodynas {'book_id':..., 'title':..., 'due_date':...}
                row = loan.copy()
                row['Grąžinti'] = False # Checkbox stulpelis
                data.append(row)
            
            loans_df = pd.DataFrame(data)
            
            st.caption("Pažymėkite varneles prie knygų, kurias norite grąžinti 👇")
            
            edited_loans = st.data_editor(
                loans_df,
                key="loans_editor",
                column_config={
                    "Grąžinti": st.column_config.CheckboxColumn(
                        "Grąžinti?",
                        default=False
                    ),
                    "title": "Pavadinimas",
                    "due_date": "Terminas",
                    "book_id": "ID"
                },
                disabled=["title", "due_date", "book_id"],
                hide_index=True,
                column_order=["Grąžinti", "title", "due_date"]
            )
            
            # Veiksmai su pažymėtomis
            selected_returns = edited_loans[edited_loans['Grąžinti'] == True]
            
            if not selected_returns.empty:
                count = len(selected_returns)
                # Mygtukas atsiranda tik kai kažkas pažymėta
                if st.button(f"Grąžinti pasirinktas ({count})", type="primary"):
                    for index, row in selected_returns.iterrows():
                        library.return_book(user.id, row['book_id'])
                    
                    st.success(f"Sėkmingai grąžinta knygų: {count}")
                    import time
                    time.sleep(1)
                    st.rerun()
            
            st.divider()
            # Paliekame "Grąžinti viską" kaip atsarginį variantą
            with st.expander("Kiti veiksmai"):
                if st.button("Grąžinti VISAS knygas iš karto"):
                    success, msg = library.return_all_books(user.id)
                    st.success(msg)
                    st.rerun()

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