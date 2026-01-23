from src.ui.ascii_styler import draw_ascii_table

def show_user_fines(library, user):
    """
    Parodo vėluojančias knygas ir baudas.
    """
    # Kviečiame serviso funkciją
    total_fine, overdue_details = library.loan_service.calculate_fine(user)
    
    print("\n--- SKOLŲ ATASKAITA ---")
    
    if total_fine == 0:
        print("✅ Jūs neturite jokių pradelstų skolų.")
        return

    print(f"⚠️ DĖMESIO: Jūsų bendra bauda yra: {total_fine:.2f} €")
    print("Skolinimas yra užblokuotas, kol negrąžinsite šių knygų:\n")

    # Ruošiame duomenis lentelei
    table_data = []
    for item in overdue_details:
        # Bandome gauti knygos pavadinimą iš ID
        book = library.book_repository.get_by_id(item['book_id'])
        title = book.title if book else item['book_id']
        
        table_data.append([
            title,
            item['due_date'],
            str(item['days']),      # Vėluoja dienų
            f"{item['fine']:.2f} €" # Bauda
        ])

    draw_ascii_table(
        ["Knyga", "Terminas", "Vėluoja (dienos)", "Bauda"],
        table_data
    )
    
    print(f"\nBendra mokėtina suma: {total_fine:.2f} €")