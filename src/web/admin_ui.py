"""
FILE: src/web/admin_ui.py
PURPOSE: Administratoriaus (Bibliotekininko) valdymo pultas.
"""

import streamlit as st
import pandas as pd
import time
from src.web.auth import logout

def render_dashboard():
    library = st.session_state.library
    user = st.session_state.user
    
    # --- ŠONINĖ JUOSTA ---
    st.sidebar.title(f"👤 {user.username} (Admin)")
    menu = st.sidebar.radio(
        "Meniu", 
        ["Statistika", "Knygų valdymas", "Vartotojų valdymas", "Vėluojančios knygos"]
    )
    st.sidebar.divider()
    if st.sidebar.button("Atsijungti", type="primary", use_container_width=True):
        logout()

    # --- 1. STATISTIKA ---
    if menu == "Statistika":
        _render_statistics(library)

    # --- 2. KNYGŲ VALDYMAS ---
    elif menu == "Knygų valdymas":
        _render_books_management(library)

    # --- 3. VARTOTOJŲ VALDYMAS ---
    elif menu == "Vartotojų valdymas":
        _render_users_management(library)

    # --- 4. VĖLUOJANČIOS KNYGOS ---
    elif menu == "Vėluojančios knygos":
        _render_overdue_books(library)


# --- PAGALBINĖS FUNKCIJOS KIEKVIENAM TABUI ---

def _render_statistics(library):
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
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"📚 **Populiariausias žanras:** {stats.get('inventory_top_genre', '-')}")
        st.warning(f"⚠️ **Vid. vėlavimas:** {stats.get('avg_overdue_per_reader', '0')} knygos/žm.")
    with c2:
        st.info(f"📖 **Skaitytojai renkasi:** {stats.get('borrowed_top_genre', '-')}")
        st.success(f"📅 **Vidutiniai metai:** {stats.get('avg_book_year', '-')}")

def _render_books_management(library):
    st.header("📚 Knygų Valdymas")

    with st.expander("➕ Pridėti naują knygą"):
        with st.form("add_book"):
            c1, c2 = st.columns(2)
            title = c1.text_input("Pavadinimas")
            author = c1.text_input("Autorius")
            genre = c2.text_input("Žanras")
            year = c2.number_input("Metai", 1000, 2030, 2023)
            
            if st.form_submit_button("Išsaugoti"):
                if title and author:
                    library.book_manager.add_book(title, author, int(year), genre)
                    st.success(f"Knyga '{title}' pridėta!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Trūksta duomenų.")

    st.divider()
    search = st.text_input("🔍 Ieškoti knygos (Pavadinimas arba Autorius)")
    
    books = library.book_manager.search_books(search) if search else library.book_manager.get_all_books()

    if books:
        data = []
        for b in books:
            row = b.to_dict()
            row['Veiksmas'] = False 
            data.append(row)
        
        df = pd.DataFrame(data).sort_values(by='title')
        st.caption(f"Rasta knygų: {len(books)}")

        edited_df = st.data_editor(
            df,
            key="admin_books",
            width="stretch",
            column_config={
                "Veiksmas": st.column_config.CheckboxColumn("Trinti?", width="small"),
                "title": st.column_config.TextColumn("Pavadinimas"),
                "author": st.column_config.TextColumn("Autorius"),
                "year": st.column_config.NumberColumn("Metai", format="%d"),
                "genre": st.column_config.TextColumn("Žanras"),
                "available_copies": st.column_config.NumberColumn("Likutis"),
                "total_copies": st.column_config.NumberColumn("Fondias"),
                "id": st.column_config.TextColumn("Sistemos ID", width="small")
            },
            disabled=["title", "author", "year", "genre", "id"],
            hide_index=True,
            column_order=["Veiksmas", "title", "author", "year", "genre", "available_copies", "total_copies"]
        )
        
        to_delete = edited_df[edited_df['Veiksmas'] == True]
        if not to_delete.empty:
            if st.button(f"Ištrinti pažymėtas ({len(to_delete)})", type="primary"):
                for _, row in to_delete.iterrows():
                    obj = library.book_manager.get_book_by_id(row['id'])
                    if obj: library.book_manager.books.remove(obj)
                library.book_manager.save()
                st.success("Ištrinta.")
                time.sleep(1)
                st.rerun()
    else:
        st.info("Knygų nerasta.")

def _render_users_management(library):
    st.header("👥 Vartotojų Administravimas")
    tab1, tab2 = st.tabs(["📋 Sąrašas", "➕ Registracija"])
    
    with tab1:
        users = library.user_manager.users
        if users:
            opts = {f"{u.username} ({u.role})": u for u in users}
            sel = st.selectbox("Pasirinkite vartotoją:", list(opts.keys()))
            if sel:
                target = opts[sel]
                st.subheader(f"Redaguojamas: {target.username}")
                c1, c2 = st.columns(2)
                with c1:
                    with st.form("edit_user"):
                        new_name = st.text_input("Vardas", value=target.username)
                        if st.form_submit_button("Atnaujinti"):
                            target.username = new_name
                            library.user_manager.save()
                            st.success("Išsaugota.")
                            st.rerun()
                with c2:
                    st.write("Pavojinga zona")
                    if st.button("Ištrinti vartotoją", type="primary"):
                        success, msg = library.safe_delete_user(target)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Negalima ištrinti:")
                            if isinstance(msg, list):
                                for m in msg: st.write(f"- {m}")
                            else: st.write(msg)
    
    with tab2:
        role = st.radio("Rolė", ["Skaitytojas", "Bibliotekininkas"])
        with st.form("create_user"):
            name = st.text_input("Vardas")
            pw = st.text_input("Slaptažodis (tik adminams)", type="password") if role == "Bibliotekininkas" else ""
            
            if st.form_submit_button("Sukurti"):
                if role == "Skaitytojas":
                    u = library.user_manager.register_reader(name)
                    if u: st.success(f"Sukurta! ID: {u.id}")
                else:
                    if library.user_manager.register_librarian(name, pw):
                        st.success("Admin sukurtas.")
                    else: st.error("Klaida.")

def _render_overdue_books(library):
    st.header("⚠️ Vėluojančios Knygos")
    overdue = library.get_all_overdue_books()
    if overdue:
        df = pd.DataFrame(overdue).rename(columns={'title': 'Knyga', 'user': 'Skaitytojas', 'due_date': 'Terminas'})
        st.dataframe(df, use_container_width=True)
    else:
        st.success("Viskas grąžinta laiku! 🎉")