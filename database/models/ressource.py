# database/models/ressource.py
from sqlalchemy import Column, Integer, String, Float, Text
from database.db_session import Base

class Ressource(Base):
    __tablename__ = "ressources"

    id = Column(Integer, primary_key=True, index=True)
    code_elevage = Column(String(50), index=True, nullable=False)
    type_ressource = Column(String(50))  # "Animaux" ou "Revenu extérieur"

    # Champs pour "Animaux"
    espece = Column(String(100))
    effectif = Column(Integer)
    production = Column(String(100))
    quantite_annuelle = Column(Float)
    destination = Column(String(50))

    # Champs pour "Revenu extérieur"
    type_revenu = Column(String(100))
    description = Column(String(200))
    montant_annuel = Column(Float)
    periodicite = Column(String(50))
    saisonnalite = Column(String(50))

    # Observations communes
    observations = Column(Text)