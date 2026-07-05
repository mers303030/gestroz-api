from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class SuiviAnimal(Base):
    __tablename__ = 'suivi_animaux'
    id = Column(Integer, primary_key=True)
    id_unique = Column(String, unique=True, nullable=False)   # même clé que dans Animal
    code_elevage = Column(String, nullable=False)
    numero_boucle = Column(String, nullable=False)
    date_naissance = Column(String, nullable=False)
    poids_naissance = Column(Float, nullable=True)
    mere_boucle = Column(String, nullable=True)
    pere_boucle = Column(String, nullable=True)
    sexe = Column(String, nullable=True)
    race = Column(String, nullable=True)
    date_sevrage = Column(String, nullable=True)
    poids_sevrage = Column(Float, nullable=True)
    gmq_naissance_sevrage = Column(Float, nullable=True)
    date_derniere_pesee = Column(String, nullable=True)
    poids_derniere_pesee = Column(Float, nullable=True)
    gmq_post_sevrage = Column(Float, nullable=True)