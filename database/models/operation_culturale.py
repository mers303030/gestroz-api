from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database.db_session import Base

class OperationCulturale(Base):
    __tablename__ = 'operations_culturales'
    id = Column(Integer, primary_key=True)
    parcelle_id = Column(Integer, ForeignKey('parcelles.id'), nullable=False)
    date_operation = Column(String, nullable=False)
    type_operation = Column(String, nullable=False)  # labour, semis, engrais_fond, etc.
    materiel = Column(String, nullable=True)
    dose = Column(String, nullable=True)            # ex: 200 kg/ha
    produit = Column(String, nullable=True)         # engrais ou semence
    observations = Column(String, nullable=True)