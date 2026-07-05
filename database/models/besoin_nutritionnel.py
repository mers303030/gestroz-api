from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class BesoinNutritionnel(Base):
    __tablename__ = 'besoins_nutritionnels'

    id = Column(Integer, primary_key=True, index=True)
    race = Column(String, nullable=False)            # ex: Oulmès-Zaer, Holstein, etc.
    categorie = Column(String, nullable=False)      # Veau, Velle, Génisse, Taurillon, Vache, Géniteur
    stade = Column(String)                          # Croissance, Gestation, Lactation, Tarissement, Indifférent
    poids_min = Column(Float, nullable=False)       # kg
    poids_max = Column(Float, nullable=False)       # kg
    production_min = Column(Float, nullable=True)   # Lait (kg/j) ou Viande (g/j)
    production_max = Column(Float, nullable=True)
    ufl = Column(Float, nullable=False)
    ufv = Column(Float, nullable=False)
    pdi = Column(Float, nullable=False)             # g
    calcium = Column(Float, nullable=False)         # %
    phosphore = Column(Float, nullable=False)       # %
    observations = Column(String, nullable=True)