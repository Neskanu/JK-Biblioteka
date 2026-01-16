"""
FILE: src/web/admin_ui.py
PURPOSE: Streamlit administratoriaus sąsaja.
RELATIONSHIPS:
  - Kviečiamas iš app.py.
  - Naudoja Library klasę duomenų manipuliavimui.
CONTEXT:
  - Atnaujinta: Knygų kiekio keitimo logika (Total vs Available sinchronizacija).
  - Apsauga: Neleidžia sumažinti bendro kiekio žemiau paskolinto kiekio.
"""

import streamlit as st # sukuria web UI
import pandas as pd # duomenų lentelėms
import plotly.express as px # diagramoms
import uuid # unikalių ID knygoms generavimui
from datetime import datetime # datos valdymui

from src.models import Book # knygų modelis reikalingas naujos knygos sukūrimui

def render_dashboard(library):
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("Valdymo Skydas")
        page = st.radio("Pasirinkite sritį:", ["Vartotojai", "Knygos", "Statistika"])
        
        st.divider()
        st.caption(f"Viso vartotojų: {len(library.user_repository.get_all())}")
        total_books = sum(b.total_copies for b in library.book_repository.books)
        st.caption(f"Viso knygų: {total_books}")

        st.divider()
        if st.button("🚪 Atsijungti"):
            st.session_state.user = None
            st.rerun()

    st.title(f"📚 {page}")

    if page == "Vartotojai":
        _render_users_view(library)
    elif page == "Knygos":
        _render_books_view(library)
    elif page == "Statistika":
        _render_stats_view(library)

# --- VIEW FUNKCIJOS ---

def _render_users_view(library):
    """Vartotojų valdymas."""
    
    # A. REGISTRACIJA
    with st.expander("➕ Registruoti naują vartotoją"):
        col1, col2 = st.columns([1, 2])
        with col1:
            role_choice = st.radio("Rolė", ["Skaitytojas", "Bibliotekininkas"], horizontal=False)
        with col2:
            new_username = st.text_input("Vartotojo vardas")
            
            if role_choice == "Skaitytojas":
                new_card_id = st.text_input("Kortelės ID (XX1111)", max_chars=6).upper()
                if st.button("Registruoti Skaitytoją"):
                    if new_username and new_card_id:
                        success, msg = library.auth_service.register_reader(new_username, new_card_id)
                        if success: st.success(msg)
                        else: st.error(msg)
                    else:
                        st.warning("Užpildykite visus laukus.")
            else:
                new_password = st.text_input("Slaptažodis", type="password")
                if st.button("Registruoti Admin"):
                    if new_username and new_password:
                        success = library.auth_service.register_librarian(new_username, new_password)
                        if success: st.success(f"Admin {new_username} sukurtas.")
                        else: st.error("Vartotojas jau egzistuoja.")
                    else:
                        st.warning("Užpildykite visus laukus.")

    st.divider()

    # B. VARTOTOJŲ SĄRAŠAS
    users = library.user_repository.get_all()
    if not users:
        st.info("Vartotojų nėra.")
        return

    # Paruošiame duomenis
    user_data = []
    for u in users:
        user_data.append({
            "id": u.id,
            "Vardas": u.username,
            "Rolė": "Skaitytojas" if u.role == 'reader' else "Admin",
            "Kortelė": u.id,
        })
    df = pd.DataFrame(user_data)
    
    # ID naudojame kaip indeksą, kad paslėptume jį vaizde
    df.set_index("id", inplace=True)
    
    st.write("Paspauskite ant eilutės redagavimui:")
    selection = st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # C. REDAGAVIMAS
    if selection.selection.rows:
        # Paimame objektą pagal ID (kuris dabar yra indeksas)
        # selection.selection.rows grąžina eilučių numerius (0, 1, 2...)
        # Mums reikia susieti eilutės numerį su vartotojų sąrašu
        selected_row_idx = selection.selection.rows[0]
        selected_user = users[selected_row_idx]

        with st.container(border=True):
            st.subheader(f"Redaguojamas: {selected_user.username}")
            
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Vardas", value=selected_user.username, key=f"n_{selected_user.id}")
                if st.button("Atnaujinti vardą"):
                    if new_name:
                        selected_user.username = new_name
                        library.user_repository.save()
                        st.success("Išsaugota!")
                        st.rerun()

                if selected_user.role == 'reader':
                    st.caption("Kortelės valdymas")
                    new_id = st.text_input("Naujas ID", key=f"id_{selected_user.id}").upper()
                    if st.button("Keisti kortelę"):
                        s, m = library.user_repository.regenerate_reader_id(selected_user, new_id)
                        if s: st.success(m); st.rerun()
                        else: st.error(m)
                else:
                    st.caption("Saugumas")
                    new_pass = st.text_input("Naujas slaptažodis", type="password", key=f"p_{selected_user.id}")
                    if st.button("Keisti slaptažodį"):
                        if new_pass:
                            selected_user.password = new_pass
                            library.user_repository.save()
                            st.success("Pakeista.")

            with c2:
                st.write("")
                st.write("")
                if st.button("🗑️ Ištrinti vartotoją", type="primary"):
                    s, m = library.safe_delete_user(selected_user)
                    if s: st.success(m); st.rerun()
                    else: st.error("Negalima ištrinti (turi skolų).")

            if selected_user.role == 'reader':
                st.divider()
                st.write("📚 **Pasiimtos knygos**")
                if selected_user.active_loans:
                    for loan in selected_user.active_loans:
                        bc, ac = st.columns([4, 1])
                        with bc:
                            st.text(f"📖 {loan['title']} (Iki: {loan['due_date']})")
                        with ac:
                            if st.button("Grąžinti", key=f"ret_{selected_user.id}_{loan['book_id']}"):
                                success, msg = library.return_book(selected_user.id, loan['book_id'])
                                if success:
                                    st.success(f"Grąžinta: {loan['title']}")
                                    st.rerun()
                                else:
                                    st.error(msg)
                else:
                    st.info("Knygų nėra.")

def _render_books_view(library):
    """Knygų valdymas: Pridėjimas, Redagavimas, Trynimas."""
    # Patikriname, ar nėra "atidėtos" žinutės iš praeito paspaudimo

    # --- 0. NAUJOS KNYGOS PRIDĖJIMAS (NAUJA DALIS) ---
    with st.expander("➕ Pridėti naują knygą", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input("Pavadinimas")
            new_author = st.text_input("Autorius")
        with col2:
            new_genre = st.text_input("Žanras")
            c_year, c_copies = st.columns(2)
            new_year = c_year.number_input("Metai", min_value=-1000, max_value=datetime.now().year + 1, value=datetime.now().year)
            new_copies = c_copies.number_input("Kiekis", min_value=1, value=1)
        
        if st.button("Išsaugoti knygą"):
            if new_title and new_author:
                try:
                    # 1. Sugeneruojame unikalų ID
                    new_id = uuid.uuid4().hex[:8].upper()
                    
                    # 2. Bandome pridėti knygą per servisą
                    # Svarbu: perduodame atskirus duomenis, o ne objektą, 
                    # nes servisas pats atlieka validaciją ir kūrimą.
                    library.inventory_service.add_book(
                        title=new_title,
                        author=new_author,
                        year=new_year,
                        genre=new_genre
                    )
                    
                    # 3. Jei klaidų nebuvo - rodome sėkmę
                    st.success(f"Knyga '{new_title}' sėkmingai pridėta! (ID: {new_id})")
                                        
                except ValueError as e:
                    # Čia pagauname Jūsų sukurtą klaidą iš inventory_service
                    # pvz.: "Knygos metai negali būti ateityje"
                    st.error(str(e))
                    
                except Exception as e:
                    # Apsauga nuo bet kokių kitų nenumatytų klaidų
                    st.error(f"Įvyko nenumatyta klaida: {e}")
                    
            else:
                st.warning("Privaloma įvesti pavadinimą ir autorių.")

    # --- 1. MASINIO TRYNIMO ĮRANKIAI ---
    with st.expander("🗑️ Masinis Knygų Nurašymas"):
        tab_list, tab_year, tab_author, tab_genre = st.tabs(["Pagal ID sąrašą", "Pagal metus", "Pagal Autorių", "Pagal Žanrą"])
        
        # ... (Ši dalis lieka tokia pati kaip anksčiau) ...
        # (Taupydamas vietą, jos nekartoju, jei turite seną kodą. Jei reikia - sakykite)
        # Svarbiausia, kad viršuje atsirado "Pridėti naują knygą".
        
        # A. Pagal ID sąrašą
        with tab_list:
            ids_input = st.text_area("ID sąrašas (kiekvienas naujoje eilutėje)", height=100)
            if st.button("Trinti pagal ID", type="primary"):
                if ids_input.strip():
                    id_list = [line.strip() for line in ids_input.split('\n') if line.strip()]
                    books_to_delete, skipped = [], []
                    for bid in id_list:
                        book = library.book_repository.get_by_id(bid)
                        if book:
                            s, m = library.safe_delete_book(book)
                            if s: books_to_delete.append(book) # Tik vizualizacijai, nes safe_delete jau ištrynė
                            else: skipped.append(bid)
                    
                    if books_to_delete: st.success(f"Ištrinta: {len(books_to_delete)}")
                    if skipped: st.error(f"Nepavyko (paskolinta/nerasta): {len(skipped)}")
                    if books_to_delete: st.rerun()

        # B. Pagal metus
        with tab_year:
            year_threshold = st.number_input("Ištrinti iki metų (imtinai):", min_value=-1000, max_value=datetime.now().year + 1, value=1990)
            candidates = [b for b in library.book_repository.books if b.year <= year_threshold]
            if candidates:
                if st.button(f"Trinti senas knygas ({len(candidates)} rasta)"):
                    deleted_count = 0
                    for b in list(candidates): # Kuriame kopiją iteravimui
                        s, m = library.safe_delete_book(b)
                        if s: deleted_count += 1
                    st.session_state.delete_success_msg = f"Sėkmingai ištrinta knygų: {deleted_count}"
                    st.rerun()
            else: st.info("Nėra senų knygų.")

        # C. Pagal Autorių
        with tab_author:
            # 1. Gauname visų autorių sąrašą
            # Pastaba: geriau naudoti get_all(), jei repo tai palaiko, vietoj tiesioginio .books
            all_books = library.book_repository.get_all() 
            authors = sorted(list(set(b.author for b in all_books if b.author)))
            
            if authors:
                sel_auth = st.selectbox("Pasirinkite autorių", authors)
                
                # 2. IŠ ANKSTO susirandame kandidatus trynimui
                # Taip kodas tampa švaresnis ir nereikia skaičiuoti mygtuko viduje
                candidates = [b for b in all_books if b.author == sel_auth]
                candidate_count = len(candidates)
                
                # 3. Mygtukas rodo iš anksto suskaičiuotą kiekį
                if st.button(f"Trinti visas '{sel_auth}' knygas (Rasta: {candidate_count})", type="primary"):
                    if candidate_count > 0:
                        # 4. Surenkame ID sąrašą
                        ids_to_delete = [b.id for b in candidates]
                        
                        # 5. Naudojame InventoryService masiniam trynimui 
                        # (tai geriau nei sukti ciklą UI dalyje)
                        deleted_real_count = library.inventory_service.batch_delete(ids_to_delete)
                        
                        # 6. Įrašome žinutę ir perkrauname
                        st.session_state.delete_success_msg = f"Sėkmingai ištrinta knygų: {deleted_real_count}"
                        st.rerun()
                    else:
                        st.warning("Nėra ką trinti.")

        # D. Pagal Žanrą
        with tab_genre:
            # 1. Gauname visus duomenis
            all_books = library.book_repository.get_all()
            
            # 2. Išfiltruojame unikalius žanrus
            # (b.genre if b.genre - apsauga, kad neįtrauktume tuščių reikšmių)
            genres = sorted(list(set(b.genre for b in all_books if b.genre)))
            
            if genres:
                sel_genre = st.selectbox("Pasirinkite žanrą", genres)
                
                # 3. IŠ ANKSTO surandame kandidatus (kad parodytume skaičių mygtuke)
                candidates = [b for b in all_books if b.genre == sel_genre]
                candidate_count = len(candidates)
                
                # 4. Mygtukas
                # Svarbu: key="btn_del_genre" padeda Streamlit atskirti šį mygtuką nuo autoriaus mygtuko
                if st.button(f"Trinti visas '{sel_genre}' knygas (Rasta: {candidate_count})", type="primary", key="btn_del_genre"):
                    if candidate_count > 0:
                        ids_to_delete = [b.id for b in candidates]
                        
                        # 5. Masinis trynimas per servisą
                        deleted_real_count = library.inventory_service.batch_delete(ids_to_delete)
                        
                        # 6. Žinutė ir perkrovimas
                        st.session_state.delete_success_msg = f"Sėkmingai ištrinta knygų: {deleted_real_count} (Žanras: {sel_genre})"
                        st.rerun()
                    else:
                        st.warning("Nėra ką trinti.")
            else:
                st.info("Bibliotekoje kol kas nėra knygų su nurodytais žanrais.")

        if 'delete_success_msg' in st.session_state:
            st.success(st.session_state.delete_success_msg)
            # Iškart ištriname, kad perkrovus puslapį dar kartą, žinutė nebekabotų
            del st.session_state.delete_success_msg

    st.divider()

    # --- 2. PAGRINDINĖ LENTELĖ ---
    books = library.book_repository.get_all()
    if not books:
        st.info("Bibliotekoje knygų nėra. Pridėkite naują viršuje!")
        return

    data_for_df = []
    for b in books:
        item = b.to_dict()
        item["Šalinti"] = False
        data_for_df.append(item)
    
    df = pd.DataFrame(data_for_df)
    df.set_index("id", inplace=True)

    column_config = {
        "title": st.column_config.TextColumn("Pavadinimas", width="large", required=True),
        "author": st.column_config.TextColumn("Autorius", width="medium", required=True),
        "year": st.column_config.NumberColumn("Metai", format="%d"),
        "total_copies": st.column_config.NumberColumn("Viso"),
        "available_copies": st.column_config.NumberColumn("Laisva", disabled=True),
        "genre": st.column_config.TextColumn("Žanras"),
        "Šalinti": st.column_config.CheckboxColumn("Trinti?", default=False),
        "active_loans": None 
    }
    
    st.info("Redaguokite duomenis tiesiogiai lentelėje.")
    edited_df = st.data_editor(df, column_config=column_config, hide_index=True, width='stretch', key="book_editor")

    if st.button("💾 Išsaugoti pakeitimus lentelėje", type="primary"):
        changes = 0
        errors = []
        
        for book_id, row in edited_df.iterrows():
            book = library.book_repository.get_by_id(book_id)
            if not book: continue

            # 1. TRYNIMAS
            if row['Šalinti']:
                s, m = library.safe_delete_book(book)
                if s: changes += 1
                else: errors.append(m)
                continue

            # 2. REDAGAVIMAS
            modified = False
            if book.title != row['title']: book.title = row['title']; modified = True
            if book.author != row['author']: book.author = row['author']; modified = True
            if int(book.year) != int(row['year']): book.year = int(row['year']); modified = True
            if book.genre != row['genre']: book.genre = row['genre']; modified = True
            
            # Kiekio keitimas
            new_total = int(row['total_copies'])
            if int(book.total_copies) != new_total:
                diff = new_total - book.total_copies
                if book.available_copies + diff < 0:
                    errors.append(f"Knyga '{book.title}': negalima mažinti kiekio (paskolinta).")
                else:
                    book.total_copies = new_total
                    book.available_copies += diff
                    modified = True
            
            if modified: changes += 1
        
        library.book_repository.save()
        
        if errors:
            for e in errors: st.error(e)
        if changes > 0:
            st.success("Duomenys atnaujinti.")
            st.rerun()

def _render_stats_view(library):
    """Statistika su pyragu."""
    stats = library.get_advanced_statistics()
    st.subheader("Bendroji Statistika")
    
    # 1. Duomenų paruošimas diagramai
    all_books = library.book_repository.books
    total_copies = sum(b.total_copies for b in all_books)
    available_copies = sum(b.available_copies for b in all_books)
    borrowed_copies = total_copies - available_copies

    # Padaliname ekraną: Skaičiai | Diagrama
    col_metrics, col_chart = st.columns([1, 1])

    with col_metrics:
        st.write("### Skaičiai")
        st.metric("Viso Knygų (Kopijų)", total_copies)
        st.metric("Skaitytojų", len([u for u in library.user_repository.users if u.role == 'reader']))
        st.metric("Paskolinta šiuo metu", borrowed_copies)
        st.metric("Vėlavimų vidurkis", stats.get('avg_overdue_per_reader', '-'))

    with col_chart:
        # 2. Braižome Pyragą (Donut Chart)
        if total_copies > 0:
            chart_data = pd.DataFrame({
                "Būsena": ["Laisva", "Paskolinta"],
                "Kiekis": [available_copies, borrowed_copies]
            })
            
            # Naudojame Plotly Express
            fig = px.pie(
                chart_data, 
                values='Kiekis', 
                names='Būsena', 
                title='Fondo užimtumas',
                color='Būsena',
                color_discrete_map={'Laisva':'#2ecc71', 'Paskolinta':'#e74c3c'}, # Žalia ir Raudona
                hole=0.4 # Padaro "spurgą"
            )
            # Paslepiame legendą, jei norime švaresnio vaizdo, arba paliekame
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Nėra duomenų diagramai.")

    st.divider()
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.write("📊 **Populiariausi Žanrai**")
        st.write(f"Fonde daugiausia: **{stats.get('inventory_top_genre', '-')}**")
        st.write(f"Skaitytojai renkasi: **{stats.get('borrowed_top_genre', '-')}**")
        st.write(f"Vid. knygų metai: **{stats.get('avg_book_year', '-')}**")
    with col_right:
        st.write("⚠️ **Vėlavimai**")
        overdue = library.get_all_overdue_books()
        if overdue:
            st.error(f"Vėluojančių knygų: {len(overdue)}")
            st.dataframe(pd.DataFrame(overdue), width='stretch', hide_index=True)
        else:
            st.success("Vėlavimų nėra!")