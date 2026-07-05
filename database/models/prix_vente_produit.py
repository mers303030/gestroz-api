from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class PrixVenteProduit(Base):
    __tablename__ = 'prix_vente_produits'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    annee = Column(String, nullable=False)
    produit = Column(String, nullable=False)        # grain, paille, foin, viande, lait, etc.
    prix_unitaire = Column(Float, nullable=False)   # DH / unité (kg, tonne, litre)
    observations = Column(String, nullable=True)