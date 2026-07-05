from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Croissance(Base):
    __tablename__ = 'croissance'
    id = Column(Integer, primary_key=True)

    # Infos de l'animal (copiées depuis Naissance)
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

    # Données de pesée
    date_pesee = Column(String, nullable=False)
    poids = Column(Float, nullable=False)
    gmq_post_sevrage = Column(Float, nullable=True)   # calculé automatiquement