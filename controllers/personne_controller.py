from database.db_session import SessionLocal
from database.models import Personne

class PersonneController:
    @staticmethod
    def get_personnes_par_eleveur(code_elevage):
        db = SessionLocal()
        result = db.query(Personne).filter(Personne.code_elevage == code_elevage).all()
        db.close()
        return result

    @staticmethod
    def ajouter_personne(data):
        db = SessionLocal()
        try:
            p = Personne(**data)
            db.add(p)
            db.commit()
            return True, p.id, "Personne ajoutée"
        except Exception as e:
            db.rollback()
            return False, None, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_personne(personne_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            p = db.query(Personne).filter(Personne.id == personne_id).first()
            if not p:
                return False, "Personne introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(p, key) and value is not None:
                    setattr(p, key, value)
            db.commit()
            return True, "Personne modifiée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_personne(personne_id):
        db = SessionLocal()
        try:
            p = db.query(Personne).filter(Personne.id == personne_id).first()
            if p:
                db.delete(p)
                db.commit()
                return True, "Personne supprimée"
            return False, "Personne introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()