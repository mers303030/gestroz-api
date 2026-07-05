from sqlalchemy import Column, Integer, String, Float, Boolean
from database.db_session import Base

class Animal(Base):
    __tablename__ = 'animaux'
    id = Column(Integer, primary_key=True)
    numero_boucle = Column(String)
    date_naissance = Column(String)
    sexe = Column(String)
    race = Column(String)
    origine = Column(String)
    date_entree = Column(String)
    code_elevage = Column(String)
    categorie = Column(String)
    poids_naissance = Column(Float, nullable=True)
    mere_boucle = Column(String, nullable=True)
    pere_boucle = Column(String, nullable=True)
    type_velage = Column(String, nullable=True)
    actif = Column(Boolean, default=True)   # True = en vie et non vendu