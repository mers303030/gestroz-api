from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class TraitementCuratif(Base):
    __tablename__ = 'traitements_curatifs'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    numero_boucle = Column(String, nullable=False)
    symptome = Column(String, nullable=False)
    cause = Column(String, nullable=True)
    maladie = Column(String, nullable=True)
    traitement = Column(String, nullable=False)       # traitement utilisé
    nom_traiteur = Column(String, nullable=True)      # vétérinaire ou technicien
    date_traitement = Column(String, nullable=False)
    produit = Column(String, nullable=True)
    dose = Column(String, nullable=True)
    observations = Column(String, nullable=True)