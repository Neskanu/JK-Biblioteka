"""
FILE: src/web/reader_ui.py
PURPOSE: Skaitytojo sąsaja su patobulintu klaidų valdymu.
RELATIONSHIPS:
  - Naudoja pandas duomenų atvaizdavimui.
  - Kviekia library.borrow_book ir library.return_book.
CONTEXT:
  - PRIDĖTA: Detalus klaidų atvaizdavimas ir Debug informacija nesėkmės atveju.
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
    
    # Visada gauname naujausius duomenis iš DB
    library.book_repository.refresh_cache() 
    books = library.book_repository.get_all()
    
    if not books:
        st.warning("Biblioteka tuščia.")
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
            successes = []
            errors = []
            
            progress_bar = st.progress(0)
            total = len(selected)

            for idx, (_, row) in enumerate(selected.iterrows()):
                # Iškviečiame logiką ir gauname žinutę
                # Pastaba: library.borrow_book turi priimti user_id arba user objektą
                try:
                    success, message = library.borrow_book(user, row['id'])
                    
                    if success:
                        successes.append(f"✅ {row['title']}: {message}")
                    else:
                        errors.append(f"❌ {row['title']}: {message}")
                except Exception as e:
                    errors.append(f"💥 {row['title']}: Kritinė klaida - {str(e)}")
                
                progress_bar.progress((idx + 1) / total)

            # Rezultatų atvaizdavimas
            if successes:
                st.success(f"Sėkmingai paimta: {len(successes)}")
                for s in successes:
                    st.write(s)
            
            if errors:
                st.error(f"Nepavyko paimti: {len(errors)}")
                for e in errors:
                    st.write(e)
                
                # --- DEBUG INFO ---
                # with st.expander("Techninė informacija (Debug)"):
                #     st.write("Vartotojo ID:", user.id)
                #     st.write("Bandyta imti:", selected[['id', 'title']].to_dict('records'))
                #     st.write("Session State User:", vars(user))

            # Perkrauname tik jei viskas pavyko, kitaip paliekame klaidą ekrane
            if not errors and successes:
                time.sleep(1.5)
                st.rerun()

def _render_my_books(library, user):
    st.header("📚 Mano Knygos")
    
    # Atnaujiname vartotojo duomenis iš DB, kad matytume tikras paskolas
    # (nes session_state.user gali būti pasenęs)
    current_user = library.user_repository.get_by_id(user.id)
    
    if not current_user or not current_user.active_loans:
        st.info("Neturite pasiėmę knygų.")
        return

    data = []
    for l in current_user.active_loans:
        # Užtikriname, kad turime dict (SQL grąžina dict, bet kartais objektus)
        r = l.copy() if isinstance(l, dict) else l.__dict__.copy()
        r['Grąžinti'] = False
        data.append(r)
    
    df = pd.DataFrame(data)
    edited = st.data_editor(
        df, key="my_ed", width="stretch",
        column_config={
            "Grąžinti": st.column_config.CheckboxColumn("Grąžinti?", width="small"),
            "due_date": st.column_config.TextColumn("Terminas", width="medium"),
            "title": st.column_config.TextColumn("Pavadinimas"),
        },
        disabled=["title", "due_date", "book_id"],
        hide_index=True,
        column_order=["Grąžinti", "title", "due_date"]
    )

    to_return = edited[edited['Grąžinti'] == True]
    if not to_return.empty:
        if st.button(f"Grąžinti ({len(to_return)})", type="primary"):
            successes = []
            errors = []

            for _, row in to_return.iterrows():
                try:
                    success, message = library.return_book(current_user, row['book_id'])
                    if success:
                        successes.append(f"✅ {row.get('title', 'Knyga')}")
                    else:
                        errors.append(f"❌ {row.get('title', 'Knyga')}: {message}")
                except Exception as e:
                     errors.append(f"💥 Kritinė klaida grąžinant ID {row.get('book_id')}: {e}")

            if successes:
                st.success(f"Grąžinta: {len(successes)}")
            
            if errors:
                st.error("Klaidos grąžinant knygas:")
                for e in errors:
                    st.write(e)
            else:
                time.sleep(1)
                st.rerun()