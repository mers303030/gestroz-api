from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class CoutOperation(Base):
    __tablename__ = 'couts_operations'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    annee = Column(String, nullable=False)
    type_operation = Column(String, nullable=False)
    montant = Column(Float, nullable=False)
    quantite = Column(String, nullable=True)
    observations = Column(String, nullable=True)