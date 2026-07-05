import os
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "zaer.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    from database.models.eleveur import Eleveur
    from database.models.animal import Animal
    from database.models.user import User
    from database.models.naissance import Naissance
    from database.models.sevrage import Sevrage
    from database.models.croissance import Croissance
    from database.models.mortalite import Mortalite
    from database.models.vente import Vente
    from database.models.aliment_base import AlimentBase
    from database.models.stock import Stock
    from database.models.visite import Visite
    Base.metadata.create_all(bind=engine)
    
    # Création d'un administrateur par défaut si aucun utilisateur
    db = SessionLocal()
    if db.query(User).count() == 0:
        admin = User(username="admin", password=hashlib.md5("admin123".encode()).hexdigest(), role="admin", code_elevage=None)
        db.add(admin)
        db.commit()
    db.close()