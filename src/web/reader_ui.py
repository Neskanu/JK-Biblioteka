"""
FILE: src/web/reader_ui.py
PURPOSE: Skaitytojo sąsaja (Knygų paieška ir paskyra).
"""

import streamlit as st
import pandas as pd
import time
from src.web.auth import logout

def render_dashboard():
    library = st.session_state.library
    user = st.session_state.user
    
    with st.sidebar:
        st.title(f"👋 {user.username}")
        st.info(f"ID: {user.id}")
        menu = st.radio("Meniu", ["Knygų katalogas", "Mano knygos"])
        st.divider()
        if st.button("Atsijungti", type="primary", width='content'):
            logout()

    if menu == "Knygų katalogas":
        _render_catalog(library, user)
    elif menu == "Mano knygos":
        _render_my_books(library, user)

def _render_catalog(library, user):
    st.header("🔎 Knygų Katalogas")
    books = library.book_repository.get_all()
    
    if not books:
        st.warning("Tuščia.")
        return

    data = []
    for b in books:
        row = b.to_dict()
        row['Pasirinkti'] = False
        row['Likutis'] = f"{b.available_copies}/{b.total_copies}"
        data.append(row)

    df = pd.DataFrame(data)
    search = st.text_input("🔍 Paieška")
    if search:
        df = df[df['title'].str.contains(search, case=False) | df['author'].str.contains(search, case=False)]

    st.caption("Pažymėkite knygas norėdami pasiimti 👇")
    edited = st.data_editor(
        df, key="cat_ed", width="stretch",
        column_config={
            "Pasirinkti": st.column_config.CheckboxColumn("Imti?", width="small"),
            "title": st.column_config.TextColumn("Pavadinimas"),
            "author": st.column_config.TextColumn("Autorius"),
            "year": st.column_config.NumberColumn("Leidimo metai", format="%d"),
            "genre": st.column_config.TextColumn("Žanras"),
            "Likutis": st.column_config.TextColumn("Laisva / Iš viso", width="small")
        },
        disabled=["title", "author", "year", "genre", "Likutis"],
        hide_index=True,
        column_order=["Pasirinkti", "title", "author", "year", "genre", "Likutis"]
    )

    selected = edited[edited['Pasirinkti'] == True]
    if not selected.empty:
        if st.button(f"Pasiimti ({len(selected)})", type="primary"):
            succ_count = 0
            for _, row in selected.iterrows():
                succ, _ = library.borrow_book(user.id, row['id'])
                if succ: succ_count += 1
            
            if succ_count > 0:
                st.toast(f"Paimta: {succ_count}!", icon="✅")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Nepavyko pasiimti (galbūt limitas ar nėra kopijų).")

def _render_my_books(library, user):
    st.header("📚 Mano Knygos")
    if not user.active_loans:
        st.info("Neturite knygų.")
        return

    data = []
    for l in user.active_loans:
        r = l.copy()
        r['Grąžinti'] = False
        data.append(r)
    
    df = pd.DataFrame(data)
    edited = st.data_editor(
        df, key="my_ed", width="stretch",
        column_config={
            "Grąžinti": st.column_config.CheckboxColumn("Grąžinti?", width="small"),
            "due_date": st.column_config.TextColumn("Terminas", width="medium")
        },
        disabled=["title", "due_date", "book_id"],
        hide_index=True,
        column_order=["Grąžinti", "title", "due_date"]
    )

    to_return = edited[edited['Grąžinti'] == True]
    if not to_return.empty:
        if st.button(f"Grąžinti ({len(to_return)})", type="primary"):
            for _, row in to_return.iterrows():
                library.return_book(user.id, row['book_id'])
            st.success("Grąžinta!")
            time.sleep(1)
            st.rerun()