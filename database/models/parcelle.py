from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Parcelle(Base):
    __tablename__ = 'parcelles'

    id = Column(Integer, primary_key=True, index=True)
    code_elevage = Column(String, nullable=False)
    numero_parcelle = Column(String, nullable=False)
    surface_ha = Column(Float, nullable=False)
    statut_foncier = Column(String)
    occupation_actuelle = Column(String)
    observations = Column(String)

    # === RELATION ===
