from sqlalchemy import Column, Integer, String
from database.db_session import Base

class Reproduction(Base):
    __tablename__ = 'reproductions'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    numero_boucle = Column(String, nullable=False)
    date_evenement = Column(String, nullable=False)
    type_evenement = Column(String, nullable=False)
    taureau_boucle = Column(String, nullable=True)
    gestatif = Column(String, nullable=True)
    date_velage_prevu = Column(String, nullable=True)
    observations = Column(String, nullable=True)