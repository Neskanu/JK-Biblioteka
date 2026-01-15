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

import streamlit as st
import pandas as pd

def render_dashboard(library):
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("Valdymo Skydas")
        page = st.radio("Pasirinkite sritį:", ["Vartotojai", "Knygos", "Statistika"])
        
        st.divider()
        st.caption(f"Viso vartotojų: {len(library.user_manager.users)}")
        total_books = sum(b.total_copies for b in library.book_manager.books)
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
                        success, msg = library.user_manager.register_reader(new_username, new_card_id)
                        if success: st.success(msg)
                        else: st.error(msg)
                    else:
                        st.warning("Užpildykite visus laukus.")
            else:
                new_password = st.text_input("Slaptažodis", type="password")
                if st.button("Registruoti Admin"):
                    if new_username and new_password:
                        success = library.user_manager.register_librarian(new_username, new_password)
                        if success: st.success(f"Admin {new_username} sukurtas.")
                        else: st.error("Vartotojas jau egzistuoja.")
                    else:
                        st.warning("Užpildykite visus laukus.")

    st.divider()

    # B. VARTOTOJŲ SĄRAŠAS
    users = library.user_manager.get_all()
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
                        library.user_manager.save()
                        st.success("Išsaugota!")
                        st.rerun()

                if selected_user.role == 'reader':
                    st.caption("Kortelės valdymas")
                    new_id = st.text_input("Naujas ID", key=f"id_{selected_user.id}").upper()
                    if st.button("Keisti kortelę"):
                        s, m = library.user_manager.regenerate_reader_id(selected_user, new_id)
                        if s: st.success(m); st.rerun()
                        else: st.error(m)
                else:
                    st.caption("Saugumas")
                    new_pass = st.text_input("Naujas slaptažodis", type="password", key=f"p_{selected_user.id}")
                    if st.button("Keisti slaptažodį"):
                        if new_pass:
                            selected_user.password = new_pass
                            library.user_manager.save()
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
    """Knygų sąrašas su redagavimu ir automatinu Available atnaujinimu."""
    books = library.book_manager.get_all()
    if not books:
        st.info("Bibliotekoje knygų nėra.")
        return

    data_for_df = []
    for b in books:
        item = b.to_dict()
        item["Šalinti"] = False
        data_for_df.append(item)
    
    df = pd.DataFrame(data_for_df)
    df.set_index("id", inplace=True) # Slepiame ID

    column_config = {
        "title": st.column_config.TextColumn("Pavadinimas", width="large", required=True),
        "author": st.column_config.TextColumn("Autorius", width="medium", required=True),
        "year": st.column_config.NumberColumn("Metai", format="%d", min_value=0, max_value=2100),
        "total_copies": st.column_config.NumberColumn("Viso", min_value=1),
        "available_copies": st.column_config.NumberColumn("Laisva", disabled=True),
        "genre": st.column_config.TextColumn("Žanras"),
        "Šalinti": st.column_config.CheckboxColumn("Ištrinti?", default=False),
        "active_loans": None 
    }

    st.info("💡 Redaguokite informaciją tiesiai lentelėje.")
    
    edited_df = st.data_editor(
        df, 
        column_config=column_config, 
        hide_index=True, 
        width='stretch', 
        key="book_editor"
    )

    if st.button("💾 Išsaugoti pakeitimus", type="primary"):
        changes_count, delete_count = 0, 0
        books_to_delete, skipped = [], []
        errors = []
        
        for book_id, row in edited_df.iterrows():
            book_obj = library.book_manager.get_by_id(book_id)
            
            if book_obj:
                # 1. TRYNIMAS
                if row['Šalinti']:
                    if book_obj.available_copies < book_obj.total_copies: 
                        skipped.append(book_obj.title)
                    else: 
                        books_to_delete.append(book_obj)
                    continue

                # 2. REDAGAVIMAS
                changed = False
                
                # Standartiniai laukai
                if book_obj.title != row['title']: book_obj.title = row['title']; changed = True
                if book_obj.author != row['author']: book_obj.author = row['author']; changed = True
                if int(book_obj.year) != int(row['year']): book_obj.year = int(row['year']); changed = True
                if book_obj.genre != row['genre']: book_obj.genre = row['genre']; changed = True
                
                # KIEKIO KEITIMAS (SVARBU: Automatinis available atnaujinimas)
                new_total = int(row['total_copies'])
                if int(book_obj.total_copies) != new_total:
                    diff = new_total - book_obj.total_copies
                    
                    # PATIKRINIMAS: Ar sumažinus kiekį, 'available' netaps neigiamas?
                    # Tai reikštų, kad bandome ištrinti knygas, kurios dabar yra pas skaitytojus.
                    if book_obj.available_copies + diff < 0:
                        errors.append(f"Negalima sumažinti '{book_obj.title}' iki {new_total} vnt. (Paskolinta: {book_obj.total_copies - book_obj.available_copies})")
                    else:
                        book_obj.total_copies = new_total
                        book_obj.available_copies += diff
                        changed = True

                if changed: changes_count += 1
        
        # Vykdome veiksmus
        if books_to_delete: delete_count = library.book_manager.batch_delete_books(books_to_delete)
        library.book_manager.save()
        
        # Atvaizduojame rezultatus
        if skipped: st.error(f"Negalima trinti (paskolinta): {', '.join(skipped)}")
        if errors: 
            for e in errors: st.error(e)
            
        if changes_count > 0 or delete_count > 0:
            st.success(f"Atnaujinta: {changes_count}. Ištrinta: {delete_count}.")
            st.rerun()
        elif not skipped and not errors:
             st.info("Pakeitimų nerasta.")

def _render_stats_view(library):
    """Statistika."""
    stats = library.get_advanced_statistics()
    st.subheader("Bendroji Statistika")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Viso Knygų", len(library.book_manager.books))
    c2.metric("Skaitytojų", len([u for u in library.user_manager.users if u.role == 'reader']))
    c3.metric("Vid. knygų metai", stats.get('avg_book_year', '-'))
    c4.metric("Vėlavimų vidurkis", stats.get('avg_overdue_per_reader', '-'))
    st.divider()
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.write("📊 **Žanrai**")
        st.write(f"Fonde: **{stats.get('inventory_top_genre', '-')}**")
        st.write(f"Skaitomiausias: **{stats.get('borrowed_top_genre', '-')}**")
    with col_right:
        st.write("⚠️ **Vėlavimai**")
        overdue = library.get_all_overdue_books()
        if overdue:
            st.error(f"Vėluojančių knygų: {len(overdue)}")
            st.dataframe(pd.DataFrame(overdue), width='stretch', hide_index=True)
        else:
            st.success("Vėlavimų nėra!")