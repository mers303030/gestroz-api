from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database.db_session import Base

class VaccinationCollective(Base):
    __tablename__ = 'vaccinations_collectives'

    id = Column(Integer, primary_key=True, index=True)
    code_elevage = Column(String(20), ForeignKey('eleveurs.code_elevage'), nullable=False)
    type_action = Column(String(50), nullable=False)          # Vaccination, Antiparasitaire, Autre collectif
    cible = Column(String(100), nullable=False)              # maladie ou parasite ciblé
    date_action = Column(String(10), nullable=False)         # format YYYY-MM-DD
    administrateur = Column(String(20), nullable=False)      # 'État' ou 'Privé'
    nom_administrateur = Column(String(100), nullable=True)
    cout_total = Column(Float, nullable=True)                # en DH
    observations = Column(String(255), nullable=True)

