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
    # Šoninė juosta
    st.sidebar.title(f"👤 {st.session_state.user.username} (Admin)")
    menu = st.sidebar.radio(
        "Meniu", 
        ["Statistika", "Knygų valdymas", "Vartotojų valdymas", "Vėluojančios knygos"]
    )
    
    st.sidebar.divider()
    if st.sidebar.button("Atsijungti", type="primary", use_container_width=True):
        logout()

    # --- 1. STATISTIKA ---
    if menu == "Statistika":
        st.header("📊 Bibliotekos Statistika")
        
        books = library.book_manager.get_all_books()
        borrowed = len([b for b in books if b.available_copies < b.total_copies])
        users_count = len(library.user_manager.users)
        stats = library.get_advanced_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Vartotojai", users_count)
        col2.metric("Knygų fondas", len(books))
        col3.metric("Paskolinta", borrowed)
        col4.metric("Laisva", len(books) - borrowed)
        
        st.divider()
        st.subheader("Išplėstinė analizė")
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"📚 **Populiariausias žanras:** {stats.get('inventory_top_genre', '-')}")
            st.warning(f"⚠️ **Vid. vėlavimas:** {stats.get('avg_overdue_per_reader', '0')} knygos/žm.")
        with c2:
            st.info(f"📖 **Skaitytojai renkasi:** {stats.get('borrowed_top_genre', '-')}")
            st.success(f"📅 **Vidutiniai metai:** {stats.get('avg_book_year', '-')}")

    # --- 2. KNYGŲ VALDYMAS (SU PAIEŠKA) ---
    elif menu == "Knygų valdymas":
        st.header("📚 Knygų Valdymas")

        # 1. Pridėjimo forma (sutraukta)
        with st.expander("➕ Pridėti naują knygą"):
            with st.form("add_book"):
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Pavadinimas")
                    author = st.text_input("Autorius")
                with col2:
                    genre = st.text_input("Žanras")
                    year = st.number_input("Metai", min_value=1000, max_value=2030, step=1, value=2023)
                
                # Papildomai: kopijų kiekis (jei backend palaiko, jei ne - default 1)
                # Standartinė add_book funkcija prideda 1 vnt. Galima kviesti cikle, jei reiktų daugiau.
                
                submit = st.form_submit_button("Išsaugoti knygą")
                
                if submit:
                    if title and author:
                        library.book_manager.add_book(title, author, int(year), genre)
                        st.success(f"Knyga '{title}' sėkmingai pridėta!")
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Būtina įvesti pavadinimą ir autorių.")

        st.divider()

        # 2. Paieška ir filtravimas
        col_search, col_sort = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("🔍 Ieškoti knygos (Pavadinimas arba Autorius)")
        
        # Gauname knygas
        if search_query:
            # Naudojame backend paiešką arba filtruojame patys
            books = library.book_manager.search_books(search_query)
        else:
            books = library.book_manager.get_all_books()

        # 3. Lentelė
        if books:
            # Paruošiame duomenis atvaizdavimui
            data = []
            for b in books:
                row = b.to_dict()
                # Pridedame stulpelį trynimui/veiksmams
                row['Veiksmas'] = False 
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Rūšiavimas (jei reikia)
            df = df.sort_values(by='title')

            st.caption(f"Rasta knygų: {len(books)}")

            # Interaktyvi lentelė
            edited_df = st.data_editor(
                df,
                key="admin_books_editor",
                width="stretch",
                column_config={
                    "Veiksmas": st.column_config.CheckboxColumn("Trinti?", width="small"),
                    "title": "Pavadinimas",
                    "author": "Autorius",
                    "year": st.column_config.NumberColumn("Metai", format="%d"),
                    "genre": "Žanras",
                    "available_copies": "Laisva",
                    "total_copies": "Viso",
                    "id": st.column_config.TextColumn("ID", width="small")
                },
                disabled=["title", "author", "year", "genre", "available_copies", "total_copies", "id"],
                hide_index=True,
                column_order=["Veiksmas", "title", "author", "year", "genre", "available_copies", "total_copies"]
            )
            
            # Trynimo logika
            to_delete = edited_df[edited_df['Veiksmas'] == True]
            if not to_delete.empty:
                st.error(f"DĖMESIO: Pažymėjote {len(to_delete)} knygų trynimui.")
                if st.button("Patvirtinti trynimą", type="primary"):
                    deleted_count = 0
                    for index, row in to_delete.iterrows():
                        # Čia reiktų tiesioginės trynimo funkcijos pagal ID
                        # Kadangi manager turi remove metodą pagal objektą, surandame objektą
                        book_obj = library.book_manager.get_book_by_id(row['id'])
                        if book_obj:
                            library.book_manager.books.remove(book_obj)
                            deleted_count += 1
                    
                    library.book_manager.save()
                    st.success(f"Ištrinta knygų: {deleted_count}")
                    import time
                    time.sleep(1)
                    st.rerun()

        else:
            st.info("Knygų nerasta.")

    # --- 3. VARTOTOJŲ VALDYMAS (REDAGAVIMAS IR KŪRIMAS) ---
    elif menu == "Vartotojų valdymas":
        st.header("👥 Vartotojų Administravimas")
        
        tab1, tab2 = st.tabs(["📋 Sąrašas ir Redagavimas", "➕ Registruoti naują"])
        
        # --- TAB 1: SĄRAŠAS IR REDAGAVIMAS ---
        with tab1:
            users = library.user_manager.users
            if not users:
                st.info("Vartotojų nėra.")
            else:
                # 1. Pasirenkame vartotoją iš sąrašo
                user_options = {f"{u.username} ({u.role}) - ID: {u.id}": u for u in users}
                selected_label = st.selectbox("Pasirinkite vartotoją redagavimui:", list(user_options.keys()))
                
                if selected_label:
                    target_user = user_options[selected_label]
                    
                    st.divider()
                    st.subheader(f"Redaguojamas: {target_user.username}")
                    
                    col1, col2 = st.columns(2)
                    
                    # Forma redagavimui
                    with col1:
                        with st.form("edit_user_form"):
                            new_name = st.text_input("Vartotojo vardas", value=target_user.username)
                            
                            new_pass = ""
                            if target_user.role == 'librarian':
                                new_pass = st.text_input("Naujas slaptažodis (palikite tuščią, jei nekeičiate)", type="password")
                            
                            save_btn = st.form_submit_button("Atnaujinti duomenis")
                            
                            if save_btn:
                                # Atnaujiname vardą
                                target_user.username = new_name
                                # Atnaujiname slaptažodį (tik adminams)
                                if target_user.role == 'librarian' and new_pass:
                                    target_user.password = new_pass # Čia reiktų hashinimo, bet mokomaisiais tikslais ok
                                
                                library.user_manager.save()
                                st.success("Duomenys atnaujinti!")
                                st.rerun()

                    # Trynimo mygtukas
                    with col2:
                        st.write("Pavojinga zona")
                        if st.button(f"Ištrinti vartotoją {target_user.username}", type="primary"):
                            success, msg = library.safe_delete_user(target_user)
                            if success:
                                st.success(msg)
                                import time
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Klaida trinant vartotoją:")
                                # Jei msg yra sąrašas (knygų pavadinimai)
                                if isinstance(msg, list):
                                    st.write("Vartotojas turi negrąžintų knygų:")
                                    for item in msg:
                                        st.text(f"- {item}")
                                else:
                                    st.write(msg)

        # --- TAB 2: REGISTRUOTI NAUJĄ ---
        with tab2:
            role_choice = st.radio("Kį norite registruoti?", ["Skaitytojas", "Bibliotekininkas (Admin)"])
            
            with st.form("create_user_form"):
                name = st.text_input("Vartotojo vardas / Vardas Pavardė")
                
                password = ""
                if role_choice == "Bibliotekininkas (Admin)":
                    password = st.text_input("Slaptažodis", type="password")
                
                submit_create = st.form_submit_button("Sukurti vartotoją")
                
                if submit_create:
                    if not name:
                        st.error("Įveskite vardą.")
                    else:
                        if role_choice == "Skaitytojas":
                            new_u = library.user_manager.register_reader(name)
                            if new_u:
                                st.success(f"Skaitytojas sukurtas! Jo kortelės ID: **{new_u.id}**")
                                st.info("Būtinai perduokite ID skaitytojui.")
                            else:
                                st.error("Nepavyko sukurti (toks vardas galbūt jau yra).")
                        else:
                            if not password:
                                st.error("Bibliotekininkui būtinas slaptažodis.")
                            else:
                                if library.user_manager.register_librarian(name, password):
                                    st.success(f"Administratorius '{name}' sėkmingai sukurtas.")
                                else:
                                    st.error("Toks vartotojas jau egzistuoja.")

    # --- 4. VĖLUOJANČIOS KNYGOS ---
    elif menu == "Vėluojančios knygos":
        st.header("⚠️ Vėluojančios Knygos")
        overdue = library.get_all_overdue_books()
        if overdue:
            # Paverčiame į DataFrame gražesniam vaizdui
            df_overdue = pd.DataFrame(overdue)
            # Pervadiname stulpelius
            df_overdue = df_overdue.rename(columns={
                'title': 'Knyga', 
                'user': 'Skaitytojas', 
                'due_date': 'Terminas'
            })
            st.dataframe(df_overdue, use_container_width=True)
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
        if st.button("Atsijungti", type="primary", width='stretch'):
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
                    width="small"
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