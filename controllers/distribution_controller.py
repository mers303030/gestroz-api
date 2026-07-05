from database.db_session import SessionLocal
from database.models.distribution import Distribution
from database.models.aliment import Aliment

class DistributionController:
    @staticmethod
    def ajouter_distribution(data: dict) -> (bool, str):
        db = SessionLocal()
        try:
            aliment = db.query(Aliment).filter(Aliment.id == data['aliment_id']).first()
            if not aliment:
                db.close()
                return False, "Aliment introuvable"
            quantite = data['quantite_kg']
            data['ufl_apport'] = (aliment.ufl or 0) * quantite
            data['ufv_apport'] = (aliment.ufv or 0) * quantite
            data['pdi_apport'] = (aliment.pdi or 0) * quantite
            distribution = Distribution(**data)
            db.add(distribution)
            db.commit()
            db.close()
            return True, "Distribution enregistrée"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def modifier_distribution(dist_id: int, data: dict) -> (bool, str):
        db = SessionLocal()
        try:
            dist = db.query(Distribution).filter(Distribution.id == dist_id).first()
            if not dist:
                db.close()
                return False, "Distribution introuvable"
            if 'aliment_id' in data or 'quantite_kg' in data:
                aliment_id = data.get('aliment_id', dist.aliment_id)
                quantite = data.get('quantite_kg', dist.quantite_kg)
                aliment = db.query(Aliment).filter(Aliment.id == aliment_id).first()
                if aliment:
                    data['ufl_apport'] = (aliment.ufl or 0) * quantite
                    data['ufv_apport'] = (aliment.ufv or 0) * quantite
                    data['pdi_apport'] = (aliment.pdi or 0) * quantite
            for key, value in data.items():
                setattr(dist, key, value)
            db.commit()
            db.close()
            return True, "Distribution modifiée"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def supprimer_distribution(dist_id: int) -> (bool, str):
        db = SessionLocal()
        try:
            dist = db.query(Distribution).filter(Distribution.id == dist_id).first()
            if not dist:
                db.close()
                return False, "Distribution introuvable"
            db.delete(dist)
            db.commit()
            db.close()
            return True, "Distribution supprimée"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def get_distributions_par_eleveur(code_elevage: str = None):
        db = SessionLocal()
        query = db.query(Distribution)
        if code_elevage:
            query = query.filter(Distribution.code_elevage == code_elevage)
        distributions = query.order_by(Distribution.date_distribution.desc()).all()
        db.close()
        return distributions