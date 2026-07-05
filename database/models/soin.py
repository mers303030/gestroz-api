from sqlalchemy import Column, Integer, String, Float, Boolean
from database.db_session import Base

class Soin(Base):
    __tablename__ = 'soins'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    numero_boucle = Column(String, nullable=False)
    date_soin = Column(String, nullable=False)          # YYYY-MM-DD
    type_soin = Column(String, nullable=False)         # Vaccination, Traitement, Antiparasitaire, etc.
    produit = Column(String, nullable=True)
    dose = Column(String, nullable=True)
    voie = Column(String, nullable=True)               # IM, IV, SC, Orale, etc.
    veterinaire = Column(String, nullable=True)
    observations = Column(String, nullable=True)
    date_rappel = Column(String, nullable=True)        # YYYY-MM-DD
    rappel_envoye = Column(Boolean, default=False)    # pour savoir si l'alerte a été affichée