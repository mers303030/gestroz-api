from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    aliment_base_id = Column(Integer, nullable=False)  # référence à aliments_base.id
    quantite_kg = Column(Float, nullable=False)
    prix_kg = Column(Float, nullable=False)
    date_entree = Column(String, nullable=False)       # YYYY-MM-DD
    origine = Column(String, nullable=False)           # "Exploitation" ou "Achat"
    observations = Column(String, nullable=True)