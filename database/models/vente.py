from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Vente(Base):
    __tablename__ = 'ventes'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    numero_boucle = Column(String, nullable=False)
    date_vente = Column(String, nullable=False)   # YYYY-MM-DD
    prix_vente = Column(Float, nullable=False)    # DH
    lieu_vente = Column(String, nullable=False)
    poids_vente = Column(Float, nullable=True)    # kg (optionnel)
    remarque = Column(String, nullable=True)