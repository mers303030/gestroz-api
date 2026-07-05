from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class AlimentBase(Base):
    __tablename__ = 'aliments_base'
    id = Column(Integer, primary_key=True)
    nom = Column(String, unique=True, nullable=False)
    categorie = Column(String)  # Pailles, Grains, Pulpes, Ensilage, Autres
    ufl = Column(Float, default=0)
    pdi = Column(Float, default=0)
    ufv = Column(Float, default=0)