from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Ration(Base):
    __tablename__ = 'rations'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    nom = Column(String, nullable=False)
    date_creation = Column(String, nullable=False)
    poids_vif = Column(Float)            # kg
    production_lait = Column(Float)      # kg/j
    stade = Column(String)               # croissance, gestation, lactation, tarissement
    observations = Column(String)