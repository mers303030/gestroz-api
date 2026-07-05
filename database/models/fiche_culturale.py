from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database.db_session import Base

class FicheCulturale(Base):
    __tablename__ = 'fiches_culturales'

    id = Column(Integer, primary_key=True, index=True)
    parcelle_id = Column(Integer, ForeignKey('parcelles.id'), nullable=False)
    annee = Column(String, nullable=False)
    culture = Column(String)
    # Labour
    labour_profondeur = Column(String)
    moyen_labour = Column(String)
    # Engrais fond
    date_engrais_fond = Column(String)
    type_engrais_fond = Column(String)
    dose_engrais_fond = Column(String)
    # Engrais couverture
    date_engrais_couverture = Column(String)
    type_engrais_couverture = Column(String)
    dose_engrais_couverture = Column(String)
    # Phytosanitaire
    date_phytosanitaire = Column(String)
    type_phytosanitaire = Column(String)
    dose_phytosanitaire = Column(String)
    # Récolte
    type_recolte = Column(String)
    rendement_grain = Column(Float)
    rendement_paille = Column(Float)
    rendement_foin = Column(Float)
    rendement_ensilage = Column(Float)
    paturage_debut = Column(String)
    paturage_fin = Column(String)
    observations = Column(String)

    # === RELATION ===
