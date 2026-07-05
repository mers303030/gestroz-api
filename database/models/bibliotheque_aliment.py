from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class BibliothequeAliment(Base):
    __tablename__ = 'bibliotheque_aliments'

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, nullable=False)
    type_aliment = Column(String)
    matiere_seche = Column(Float)      # %
    ufl = Column(Float, default=0)
    ufv = Column(Float, default=0)
    pdi = Column(Float, default=0)     # g/kg MS
    calcium = Column(Float, default=0) # %
    phosphore = Column(Float, default=0) # %