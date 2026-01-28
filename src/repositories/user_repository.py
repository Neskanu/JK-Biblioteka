"""
FILE: src/repositories/user_repository.py
PURPOSE: Atlieka CRUD operacijas su Vartotojais naudojant SQLAlchemy.
RELATIONSHIPS:
  - Naudoja src/database.py.
  - Manipuliuoja src/models.py User ir Loan objektais.
CONTEXT:
  - Užtikrina 'eager loading' (joinedload) paskoloms, kad jos būtų pasiekiamos po sesijos uždarymo.
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
        session = SessionLocal()
        try:
            # options(joinedload(User.loans)) užtikrina, kad paskolos bus užkrautos kartu su vartotoju
            return session.query(User).options(joinedload(User.loans)).all()
        finally:
            session.close()

    def get_by_id(self, user_id):
        session = SessionLocal()
        try:
            return session.query(User).options(joinedload(User.loans)).filter(User.id == str(user_id)).first()
        finally:
            session.close()
    
    def get_by_username(self, username):
        session = SessionLocal()
        try:
            return session.query(User).options(joinedload(User.loans)).filter(User.username == username).first()
        finally:
            session.close()

    def add(self, user):
        session = SessionLocal()
        try:
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save(self):
        """
        Suderinamumas. SQLAlchemy reikalauja explicityvaus commit.
        Idealiu atveju, servisas turėtų kviesti 'update' metodą.
        Bet jei modifikuojame objektą tiesiogiai, reikia sesijos.
        
        Laikinas sprendimas (Hack):
        Kadangi senas kodas daro: user.something = x; repo.save()
        Mums reikia 'merge' strategijos visiems vartotojams. Tai neefektyvu.
        Geriau perrašyti Services, kad jie kviestų update(user).
        """
        pass
        
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

    def remove(self, user):
        session = SessionLocal()
        try:
            # Reikia gauti objektą prijungtą prie šios sesijos
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
            
    # Alias
    delete_user_from_db = remove