"""
FILE: src/services/inventory_service.py
PURPOSE: Valdo knygų fondą (Inventorių).
RELATIONSHIPS:
  - Bendrauja su BookRepository duomenų keitimui.
CONTEXT:
  - Čia yra taisyklė: "Jei knyga jau yra, nekurk naujos, o padidink kiekį".
    Tai vadinama Verslo Logika (Business Logic).
"""
from datetime import datetime
from src.models import Book

class InventoryService:
    def __init__(self, book_repository):
        self.repo = book_repository

    def add_book(self, title, author, year, genre):
            """
            Prideda knygą su griežta validacija.
            """
            # 1. DEBUG: Atspausdiname į konsolę, ką tiksliai gauname (kad matytumėte terminale)
            print(f"DEBUG: Bandoma pridėti knygą. Metai: {year} (Tipas: {type(year)})")

            # 2. PRIVERSTINIS KONVERTAVIMAS (Defensive Programming)
            # Tai apsaugo nuo situacijų, jei iš UI netyčia atkeliauja tekstas "2029"
            try:
                year_int = int(year)
            except ValueError:
                raise ValueError(f"Klaida: Metai turi būti skaičius, o gauta: {year}")

            # 3. LAIKO PATIKRINIMAS
            current_year = datetime.now().year
            limit_future_year = current_year + 1
            limit_past_year = -1000

            # Patikriname ateitį
            if year_int > limit_future_year:
                raise ValueError(f"Klaida: Knygos metai ({year_int}) negali būti vėlesni nei {limit_future_year}.")

            # Patikriname praeitį (NAUJA DALIS)
            if year_int < limit_past_year:
                raise ValueError(f"Klaida: Knygos metai ({year_int}) negali būti ankstesni nei {limit_past_year}.")

            # 4. PATIKRINIMAS, AR KNYGA EGZISTUOJA
            existing_book = self.repo.find_by_details(title, author)
            
            if existing_book:
                existing_book.total_copies += 1
                existing_book.available_copies += 1
                self.repo.save()
                print("DEBUG: Atnaujinta esama knyga.")
                return existing_book
            
            # 5. NAUJOS KNYGOS KŪRIMAS
            # Svarbu: naudojame year_int, o ne pradinį year
            new_book = Book(title, author, year_int, genre, total_copies=1, available_copies=1)
            self.repo.add(new_book)
            print("DEBUG: Sukurta nauja knyga.")
            return new_book

    def batch_delete(self, book_ids):
        """
        Masinis knygų šalinimas su vienkartiniu išsaugojimu.
        """
        print(f"DEBUG: Pradedamas masinis trynimas. Kiekis: {len(book_ids)}")
        
        deleted_count = 0
        
        # 1. Triname tik iš atminties (RAM)
        for bid in book_ids:
            # Naudojame naują metodą, kuris nerašo į failą
            if self.repo.remove_without_save(bid):
                print(f"DEBUG: Iš atminties pašalinta knyga ID: {bid}")
                deleted_count += 1
            else:
                print(f"DEBUG: Knyga {bid} nerasta atmintyje.")
        
        # 2. Įrašome į failą TIK VIENĄ KARTĄ
        if deleted_count > 0:
            print(f"DEBUG: Baigta. Iš viso ištrinta: {deleted_count}. Saugoma į diską...")
            self.repo.save()
        else:
            print("DEBUG: Nieko neištrinta, failas neliečiamas.")
            
        return deleted_count