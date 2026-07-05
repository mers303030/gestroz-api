from sqlalchemy import Column, Integer, String
from database.db_session import Base

class Personne(Base):
    __tablename__ = 'personnes'

    id = Column(Integer, primary_key=True, index=True)
    code_elevage = Column(String, nullable=False)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_naissance = Column(String)       # format YYYY-MM-DD
    occupation = Column(String)
    lien_parente = Column(String)         # ex: époux, enfant, frère, etc.
    lieu_residence = Column(String)
    observations = Column(String)