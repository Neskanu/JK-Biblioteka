"""
FILE: src/ui/reader/borrow_flow.py
PURPOSE: Valdo knygos pasiėmimo transakciją.
RELATIONSHIPS:
  - Bendrauja su Library kontroleriu (borrow_book metodas).
CONTEXT:
  - Užtikrina, kad vartotojas patvirtintų veiksmą ir gautų aiškų atsakymą.
"""

from src.ui.common import pause

def process_borrowing(library, user, book):
    """
    Atlieka knygos pasiėmimo veiksmus: patikrinimą ir vykdymą.
    
    Args:
        library: Pagrindinis bibliotekos objektas.
        user: Prisijungęs skaitytojas.
        book: Knygos objektas, kurį norima pasiimti.
    """
    if not book:
        return

    print(f"\n--- Knygos Pasiėmimas: '{book.title}' ---")
    
    # Papildomas patikrinimas UI lygmenyje (nors Library tą irgi tikrina)
    if book.available_copies <= 0:
        print("Dėmesio: Šios knygos šiuo metu nėra (visos kopijos išduotos).")
        # Galime leisti rezervuoti ateityje, bet dabar tiesiog sustojame
        pause()
        return

    confirm = input(f"Ar tikrai norite pasiskolinti '{book.title}'? (t/n): ")
    
    if confirm.lower() == 't':
        success, message = library.lending_service.borrow_book(user, book)
        
        if success:
            print(f"\nSĖKMINGA! {message}")
        else:
            print(f"\nKLAIDA: {message}")
    else:
        print("Veiksmas atšauktas.")
    
    pause()