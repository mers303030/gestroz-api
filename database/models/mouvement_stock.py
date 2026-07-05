from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class MouvementStock(Base):
    __tablename__ = 'mouvements_stock'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    aliment_id = Column(Integer, nullable=False)
    date_mouvement = Column(String, nullable=False)  # format YYYY-MM-DD
    type = Column(String, nullable=False)            # 'entree' ou 'sortie'
    quantite = Column(Float, nullable=False)
    prix_unitaire = Column(Float)
    fournisseur = Column(String)
    remarque = Column(String)