from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Aliment(Base):
    __tablename__ = 'aliments'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)   # lien avec l'éleveur
    nom = Column(String, nullable=False)
    type_aliment = Column(String)       # Concentré, Fourrage, Minéral
    matiere_seche = Column(Float)       # % matière sèche
    prix_kg = Column(Float)             # prix unitaire en DH/kg
    ufl = Column(Float, default=0)      # Unité Fourragère Lait
    ufv = Column(Float, default=0)      # Unité Fourragère Viande
    pdi = Column(Float, default=0)      # Protéines Digestibles Intestinales