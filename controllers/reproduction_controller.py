from database.db_session import SessionLocal
from database.models import Reproduction, Naissance, Animal
from datetime import datetime, timedelta

class ReproductionController:
    @staticmethod
    def get_reproductions_par_eleveur(code_elevage=None):
        db = SessionLocal()
        query = db.query(Reproduction)
        if code_elevage:
            query = query.filter(Reproduction.code_elevage == code_elevage)
        result = query.order_by(Reproduction.date_evenement.desc()).all()
        db.close()
        return result

    @staticmethod
    def get_femelles_actives(code_elevage):
        db = SessionLocal()
        femelles = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.sexe == 'F',
            Animal.actif == True
        ).all()
        db.close()
        return femelles

    @staticmethod
    def get_taureaux_actifs(code_elevage):
        db = SessionLocal()
        taureaux = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.sexe == 'M',
            Animal.categorie.in_(['Géniteur', 'Taurillon']),
            Animal.actif == True
        ).all()
        db.close()
        return taureaux

    @staticmethod
    def ajouter_evenement(data):
        db = SessionLocal()
        try:
            evt = Reproduction(
                code_elevage=data['code_elevage'],
                numero_boucle=data['numero_boucle'],
                date_evenement=data['date_evenement'],
                type_evenement=data['type_evenement'],
                taureau_boucle=data.get('taureau_boucle'),
                gestatif=data.get('gestatif'),
                date_velage_prevu=data.get('date_velage_prevu'),
                observations=data.get('observations')
            )
            db.add(evt)
            db.commit()
            return True, "Événement ajouté"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_evenement(evenement_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            evt = db.query(Reproduction).filter(Reproduction.id == evenement_id).first()
            if not evt:
                return False, "Événement introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(evt, key) and value is not None:
                    setattr(evt, key, value)
            db.commit()
            return True, "Événement modifié"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_evenement(evenement_id):
        db = SessionLocal()
        try:
            evt = db.query(Reproduction).filter(Reproduction.id == evenement_id).first()
            if evt:
                db.delete(evt)
                db.commit()
                return True, "Événement supprimé"
            return False, "Événement introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def calculer_velage_prevu(date_ia):
        dt = datetime.strptime(date_ia, "%Y-%m-%d")
        velage = dt + timedelta(days=285)
        return velage.strftime("%Y-%m-%d")