from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database.db_session import Base

class TraitementArbre(Base):
    __tablename__ = 'traitements_arbres'
    id = Column(Integer, primary_key=True)
    arbre_id = Column(Integer, ForeignKey('arbres.id'), nullable=False)
    type_traitement = Column(String, nullable=False)
    date_traitement = Column(String, nullable=False)
    produit = Column(String, nullable=True)
    dose = Column(String, nullable=True)
    observations = Column(String, nullable=True)
