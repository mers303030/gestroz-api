from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database.db_session import Base

class Arbre(Base):
    __tablename__ = 'arbres'

    id = Column(Integer, primary_key=True, index=True)
    code_elevage = Column(String, nullable=False)
    parcelle_id = Column(Integer, ForeignKey('parcelles.id'), nullable=True)
    espece = Column(String, nullable=False)
    nombre_arbres = Column(Integer, nullable=False)
    destination = Column(String)
    rendement_kg_arbre = Column(Float)
    quantite_vendue_kg = Column(Float)
    prix_vente_kg = Column(Float)
    observations = Column(String)

    # === RELATION ===
