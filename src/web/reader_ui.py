"""
FAILAS: src/web/reader_ui.py
PASKIRTIS: Skaitytojo vartotojo sąsaja (UI) knygų katalogui ir asmeninei bibliotekai.
RYŠIAI:
  - Importuoja auth.logout sesijos valdymui.
  - Naudoja Library fasadą (library.borrow_book, library.return_book).
  - Atvaizduoja duomenis naudojant Pandas ir Streamlit.
KONTEKSTAS:
  - PATAISYMAS (V3): Sutvarkytas '_render_my_books' duomenų paruošimas.
    Pašalintas 'l.__dict__', kuris įtraukdavo '_sa_instance_state' ir gadino 'data_editor' veikimą.
    Dabar duomenys lentelėje yra "švarūs", todėl mygtukas "Grąžinti" veikia korektiškai.
"""

import streamlit as st
import pandas as pd
import time
from src.web.auth import logout

def render_dashboard():
    """
    Pagrindinė funkcija, inicijuojanti skaitytojo skydelį.
    Nustato šoninį meniu ir nukreipia į atitinkamą vaizdą.
    """
    library = st.session_state.library
    user = st.session_state.user
    
    with st.sidebar:
        st.title(f"👋 {user.username}")
        st.info(f"ID: {user.id}")
        # Pridėta nauja navigacijos parinktis „Naujienos“
        menu = st.radio("Meniu", ["✨ Naujienos", "🔎 Knygų katalogas", "📚 Mano knygos"])
        st.divider()
        if st.button("Atsijungti", type="primary", width='content'):
            logout()

    if menu == "✨ Naujienos":
        _render_news(library, user)
    elif menu == "🔎 Knygų katalogas":
        _render_catalog(library, user)
    elif menu == "Mano knygos":
        _render_my_books(library, user)

def _render_news(library, user):
    """
    Rodo vėliausiai į biblioteką įtrauktas knygas (naudojant created_at lauką).
    """
    st.header("✨ Naujausios knygos bibliotekoje")
    st.write("Susipažinkite su šviežiausiais papildymais mūsų lentynose!")

    all_books = library.book_repository.get_all()
    
    # Rūšiuojame knygas pagal created_at lauką (nuo naujausios)
    # Jei created_at nėra (seni įrašai), naudojame minimalią datą
    new_arrivals = sorted(
        all_books, 
        key=lambda x: getattr(x, 'created_at', None) or pd.Timestamp.min, 
        reverse=True
    )[:5] # Rodome 5 naujausias

    if not new_arrivals:
        st.info("Naujienų kol kas nėra.")
        return

    # Atvaizdavimas kortelėmis
    for book in new_arrivals:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(book.title)
                st.write(f"✍️ **Autorius:** {book.author}")
                st.caption(f"📂 Žanras: {book.genre} | 📅 Metai: {book.year}")
            with col2:
                st.write(f"📦 Likutis: {book.available_copies}/{book.total_copies}")
                if book.available_copies > 0:
                    if st.button("Pasiimti", key=f"news_{book.id}"):
                        _direct_borrow(library, user, book)
                else:
                    st.button("Išduota", disabled=True, key=f"news_dis_{book.id}")

def _render_catalog(library, user):
    """
    Atvaizduoja visų knygų sąrašą su paieška ir galimybe pasiskolinti.
    """
    st.header("🔎 Knygų Katalogas")
    
    books = library.book_repository.get_all()
    
    if not books:
        st.warning("Biblioteka tuščia.")
        return

    # Konvertuojame objektus į dict sąrašą
    data = []
    for b in books:
        # Book modelis turi to_dict metodą, todėl čia viskas gerai
        row = b.to_dict()
        row['Pasirinkti'] = False
        row['Likutis'] = f"{b.available_copies}/{b.total_copies}"
        data.append(row)

    df = pd.DataFrame(data)

    # Paieška
    search = st.text_input("🔍 Paieška")
    if search:
        df = df[df['title'].str.contains(search, case=False) | df['author'].str.contains(search, case=False)]

    st.caption("Pažymėkite knygas norėdami pasiimti 👇")
    
    # Interaktyvi lentelė
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
            _process_borrowing(library, user, selected)

def _process_borrowing(library, user, selected_df):
    """
    Apdoroja knygų paėmimą.
    """
    successes = []
    errors = []
    
    progress_bar = st.progress(0)
    total = len(selected_df)

    for idx, (_, row) in enumerate(selected_df.iterrows()):
        try:
            # Perduodame user.id, o ne visą user objektą
            success, message = library.borrow_book(user.id, row['id'])
            
            if success:
                successes.append(f"✅ {row['title']}: {message}")
            else:
                errors.append(f"❌ {row['title']}: {message}")
        except Exception as e:
            errors.append(f"💥 {row['title']}: Kritinė klaida - {str(e)}")
        
        progress_bar.progress((idx + 1) / total)

    if successes:
        st.success(f"Sėkmingai paimta: {len(successes)}")
        for s in successes: st.write(s)
    
    if errors:
        st.error(f"Nepavyko paimti: {len(errors)}")
        for e in errors: st.write(e)

    if not errors and successes:
        time.sleep(1.5)
        st.rerun()

def _render_my_books(library, user):
    """
    Atvaizduoja vartotojo turimas knygas.
    """
    st.header("📚 Mano Knygos")
    
    # Gauname naujausius duomenis iš DB
    current_user = library.user_repository.get_by_id(user.id)
    
    if not current_user or not current_user.active_loans:
        st.info("Neturite pasiėmę knygų.")
        return

    # --- PATAISYMAS ČIA ---
    data = []
    for l in current_user.active_loans:
        # Saugiai ištraukiame duomenis. 
        # Loan objektas neturi 'to_dict', o '__dict__' naudoti negalima dėl SQLAlchemy vidinių duomenų.
        if isinstance(l, dict):
            row = l.copy()
        else:
            # Rankiniu būdu surenkame tik reikalingus laukus
            row = {
                "book_id": l.book_id,
                "title": l.title,
                "due_date": l.due_date
            }
        
        row['Grąžinti'] = False
        data.append(row)
    # ----------------------
    
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
            _process_returning(library, current_user, to_return)

def _process_returning(library, user, return_df):
    """
    Apdoroja knygų grąžinimą.
    """
    successes = []
    errors = []

    for _, row in return_df.iterrows():
        try:
            # Perduodame user.id, o ne visą user objektą
            success, message = library.return_book(user.id, row['book_id'])
            
            title = row.get('title', 'Knyga')
            if success:
                successes.append(f"✅ {title}")
            else:
                errors.append(f"❌ {title}: {message}")
        except Exception as e:
                errors.append(f"💥 Kritinė klaida grąžinant ID {row.get('book_id')}: {e}")

    if successes:
        st.success(f"Grąžinta: {len(successes)}")
    
    if errors:
        st.error("Klaidos grąžinant knygas:")
        for e in errors: st.write(e)
    else:
        time.sleep(1)
        st.rerun()