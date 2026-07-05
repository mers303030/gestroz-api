from sqlalchemy import Column, Integer, Float
from database.db_session import Base

class CompositionRation(Base):
    __tablename__ = 'compositions_ration'
    id = Column(Integer, primary_key=True)
    ration_id = Column(Integer, nullable=False)
    aliment_id = Column(Integer, nullable=False)
    quantite = Column(Float, nullable=False)   # en kg (ou unité)
    proportion = Column(Float)                 # % de la ration (optionnel)