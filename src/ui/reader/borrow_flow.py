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
    Atlieka knygos pasiėmimo veiksmus.
    """
    if not book:
        return

    # --- 1 PATAISYMAS: Vartotojo užtikrinimas ---
    # Jei user nepaduotas, naudojame tą, kuris dabar prisijungęs
    if not user and hasattr(library, 'current_user'):
        user = library.current_user

    if not user:
        print("\nKLAIDA: Nepavyko nustatyti vartotojo. Prašome prisijungti iš naujo.")
        pause()
        return
    # ---------------------------------------------

    print(f"\n--- Knygos Pasiėmimas: '{book.title}' ---")
    
    if book.available_copies <= 0:
        print("Dėmesio: Šios knygos šiuo metu nėra (visos kopijos išduotos).")
        pause()
        return

    confirm = input(f"Ar tikrai norite pasiskolinti '{book.title}'? (t/n): ")
    
    if confirm.lower() == 't':
        # --- 2 PATAISYMAS: ID naudojimas ---
        # Servisui dažniausiai geriau duoti ID, o ne objektus.
        # Taip išvengiame klaidų, kai servisas bando ieškoti "objekto" duomenų bazėje.
        user_id = user.id if hasattr(user, 'id') else user
        book_id = book.id if hasattr(book, 'id') else book
        
        success, message = library.loan_service.borrow_book(user_id, book_id)
        
        if success:
            print(f"\n✅ SĖKMINGA! {message}")
        else:
            print(f"\n❌ KLAIDA: {message}")
    else:
        print("Veiksmas atšauktas.")
    
    pause()