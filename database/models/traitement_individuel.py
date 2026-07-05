from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database.db_session import Base

class TraitementIndividuel(Base):
    __tablename__ = 'traitements_individuels'

    id = Column(Integer, primary_key=True, index=True)
    code_elevage = Column(String(20), ForeignKey('eleveurs.code_elevage'), nullable=False)
    numero_boucle = Column(String(20), nullable=False)
    symptome = Column(String(100), nullable=False)
    cause = Column(String(100), nullable=True)
    maladie = Column(String(100), nullable=True)
    traitement = Column(String(100), nullable=False)
    nom_traiteur = Column(String(100), nullable=True)
    date_traitement = Column(String(10), nullable=False)
    produit = Column(String(100), nullable=True)
    dose = Column(String(50), nullable=True)
    observations = Column(String(255), nullable=True)

