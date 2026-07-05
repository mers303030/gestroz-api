from sqlalchemy import Column, Integer, String, Float, Boolean
from database.db_session import Base

class Naissance(Base):
    __tablename__ = 'naissances'
    id = Column(Integer, primary_key=True)
    code_elevage = Column(String)
    mere_boucle = Column(String)
    date_naissance = Column(String)
    sexe = Column(String)
    race = Column(String)
    poids_naissance = Column(Float, nullable=True)
    pere_boucle = Column(String, nullable=True)
    numero_boucle = Column(String)
    type_velage = Column(String, nullable=True)
    observations = Column(String, nullable=True)

    # Sevrage (stocké dans la même table)
    sevre = Column(Boolean, default=False)
    date_sevrage = Column(String, nullable=True)
    poids_sevrage = Column(Float, nullable=True)
    gmq_naissance_sevrage = Column(Float, nullable=True)

    # Statut vivant/vendu/mort
    actif = Column(Boolean, default=True)

    # (Optionnel) infos redondantes des parents
    mere_categorie = Column(String, nullable=True)
    mere_date_naissance = Column(String, nullable=True)
    mere_race = Column(String, nullable=True)
    pere_categorie = Column(String, nullable=True)
    pere_date_naissance = Column(String, nullable=True)
    pere_race = Column(String, nullable=True)