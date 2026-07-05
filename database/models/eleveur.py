from sqlalchemy import Column, String
from database.db_session import Base

class Eleveur(Base):
    __tablename__ = 'eleveurs'
    code_elevage = Column(String, primary_key=True)
    nom = Column(String)
    prenom = Column(String)
    date_naissance = Column(String)
    niveau_scolaire = Column(String)
    cnie = Column(String, unique=True)
    telephone = Column(String, unique=True)
    commune = Column(String)
