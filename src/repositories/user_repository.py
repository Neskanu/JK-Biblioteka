"""
FILE: src/repositories/user_repository.py
PURPOSE: Atlieka CRUD operacijas su Vartotojais.
RELATIONSHIPS:
  - Naudoja src/database.py.
  - Manipuliuoja src/models.py User ir Loan objektais.
CONTEXT:
  - Refaktorizuota: Pridėtas 'nested eager loading' (joinedload(Loan.book)), 
    kad išvengtume 'DetachedInstanceError' kai UI bando pasiekti knygos duomenis.
"""

from sqlalchemy.orm import joinedload
from src.database import SessionLocal
from src.models import User, Loan

class UserRepository:
    def __init__(self):
        pass

    @property
    def users(self):
        """Suderinamumo sluoksnis."""
        return self.get_all()

    def get_all(self):
        """Grąžina visus vartotojus su užkrautomis paskolomis IR tų paskolų knygomis."""
        session = SessionLocal()
        try:
            # Grandininis užkrovimas: User -> Loans -> Book
            return session.query(User).options(
                joinedload(User.loans).joinedload(Loan.book)
            ).all()
        finally:
            session.close()

    def get_by_id(self, user_id):
        session = SessionLocal()
        try:
            return session.query(User).options(
                joinedload(User.loans).joinedload(Loan.book)
            ).filter(User.id == str(user_id)).first()
        finally:
            session.close()
    
    def get_by_username(self, username):
        session = SessionLocal()
        try:
            return session.query(User).options(
                joinedload(User.loans).joinedload(Loan.book)
            ).filter(User.username == username).first()
        finally:
            session.close()

    def add(self, user):
        session = SessionLocal()
        try:
            session.add(user)
            session.commit()
            session.refresh(user) # Atnaujina ID ir laukus
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update(self, user):
        """Atnaujina vartotojo duomenis."""
        session = SessionLocal()
        try:
            session.merge(user)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save(self):
        """
        Suderinamumo metodas.
        """
        pass

    def remove(self, user):
        session = SessionLocal()
        try:
            # Naudojame session.get, kad gautume objektą šioje sesijoje
            u = session.get(User, user.id)
            if u:
                session.delete(u)
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
            
    # Alias senam kodui
    delete_user_from_db = remove