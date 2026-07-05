from sqlalchemy import Column, Integer, String
from database.db_session import Base

class Mortalite(Base):
    __tablename__ = 'mortalites'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String)
    numero_boucle = Column(String)
    date_deces = Column(String)      # format YYYY-MM-DD
    cause_deces = Column(String)
    remarque = Column(String)