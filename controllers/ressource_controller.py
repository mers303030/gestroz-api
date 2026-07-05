from database.db_session import SessionLocal
from database.models import Ressource

class RessourceController:
    @staticmethod
    def get_ressources_par_eleveur(code_elevage):
        db = SessionLocal()
        result = db.query(Ressource).filter(Ressource.code_elevage == code_elevage).all()
        db.close()
        return result

    @staticmethod
    def ajouter_ressource(data):
        db = SessionLocal()
        try:
            r = Ressource(**data)
            db.add(r)
            db.commit()
            return True, r.id, "Ressource ajoutée"
        except Exception as e:
            db.rollback()
            return False, None, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_ressource(ressource_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            r = db.query(Ressource).filter(Ressource.id == ressource_id).first()
            if not r:
                return False, "Ressource introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(r, key) and value is not None:
                    setattr(r, key, value)
            db.commit()
            return True, "Ressource modifiée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_ressource(ressource_id):
        db = SessionLocal()
        try:
            r = db.query(Ressource).filter(Ressource.id == ressource_id).first()
            if r:
                db.delete(r)
                db.commit()
                return True, "Ressource supprimée"
            return False, "Ressource introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()