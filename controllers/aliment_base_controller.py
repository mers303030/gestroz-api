from database.db_session import SessionLocal
from database.models.aliment_base import AlimentBase

class AlimentBaseController:
    @staticmethod
    def get_all():
        db = SessionLocal()
        aliments = db.query(AlimentBase).order_by(AlimentBase.categorie, AlimentBase.nom).all()
        db.close()
        return aliments

    @staticmethod
    def get_by_categorie():
        db = SessionLocal()
        categories = db.query(AlimentBase.categorie).distinct().all()
        result = {}
        for cat in categories:
            if cat[0]:
                result[cat[0]] = db.query(AlimentBase).filter(AlimentBase.categorie == cat[0]).order_by(AlimentBase.nom).all()
        db.close()
        return result

    @staticmethod
    def initialiser_bibliotheque():
        db = SessionLocal()
        if db.query(AlimentBase).count() == 0:
            aliments = [
                ("Paille d'orge", "Pailles", 0.35, 20, 0.35),
                ("Paille de blé tendre", "Pailles", 0.30, 15, 0.30),
                ("Paille de blé dur", "Pailles", 0.30, 15, 0.30),
                ("Paille de féverole", "Pailles", 0.40, 25, 0.40),
                ("Paille de vesce", "Pailles", 0.38, 22, 0.38),
                ("Paille de triticale", "Pailles", 0.33, 18, 0.33),
                ("Paille de pois chiche", "Pailles", 0.32, 16, 0.32),
                ("Paille de lentille", "Pailles", 0.32, 16, 0.32),
                ("Grain d'orge", "Grains", 1.10, 110, 1.10),
                ("Grain de triticale", "Grains", 1.05, 105, 1.05),
                ("Féverole", "Grains", 1.20, 180, 1.20),
                ("Ensilage vesce-avoine", "Ensilage", 0.75, 60, 0.75),
                ("Ensilage orge-vesce", "Ensilage", 0.70, 55, 0.70),
                ("Pulpe de betterave", "Pulpes", 0.85, 80, 0.85),
                ("Pulpe de luzerne", "Pulpes", 0.80, 70, 0.80),
                ("Mélasse", "Autres", 1.00, 90, 1.00),
            ]
            for nom, cat, ufl, pdi, ufv in aliments:
                db.add(AlimentBase(nom=nom, categorie=cat, ufl=ufl, pdi=pdi, ufv=ufv))
            db.commit()
        db.close()