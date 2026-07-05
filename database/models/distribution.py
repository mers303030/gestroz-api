from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Distribution(Base):
    __tablename__ = 'distributions'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    date_distribution = Column(String, nullable=False)  # YYYY-MM-DD
    aliment_id = Column(Integer, nullable=False)       # référence vers aliments.id
    quantite_kg = Column(Float, nullable=False)        # quantité distribuée (kg brut)
    categorie_animale = Column(String)                # Vache, Génisse, etc.
    observations = Column(String)
    # Calculés automatiquement (à partir de l'aliment)
    ufl_apport = Column(Float, default=0)
    ufv_apport = Column(Float, default=0)
    pdi_apport = Column(Float, default=0)