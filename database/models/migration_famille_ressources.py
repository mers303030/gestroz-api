from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class CoutOperation(Base):
    __tablename__ = 'couts_operations'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    annee = Column(String, nullable=False)          # année de l'opération
    type_operation = Column(String, nullable=False) # labour, semis, engrais, désherbage, récolte, aliment, soin, etc.
    montant = Column(Float, nullable=False)         # DH (ou autre monnaie)
    quantite = Column(Float, nullable=True)         # ha, kg, dose, etc. (optionnel)
    observations = Column(String, nullable=True)