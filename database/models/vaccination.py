from sqlalchemy import Column, Integer, String, Float
from database.db_session import Base

class Vaccination(Base):
    __tablename__ = 'vaccinations'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String, nullable=False)
    numero_boucle = Column(String, nullable=False)  # animal concerné
    maladie = Column(String, nullable=False)       # maladie ciblée
    date_vaccination = Column(String, nullable=False)
    administrateur = Column(String, nullable=False)  # Docteur, Technicien
    nom_administrateur = Column(String, nullable=True)
    statut = Column(String, nullable=False)          # Etat, Privé
    cout_par_dose = Column(Float, nullable=True)    # si privé
    observations = Column(String, nullable=True)