from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Sevrage(Base):
    __tablename__ = 'sevrages'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String)
    numero_boucle = Column(String)
    date_sevrage = Column(String)
    poids_sevrage = Column(Float)
    gmq_naissance_sevrage = Column(Float)  # calculé automatiquement