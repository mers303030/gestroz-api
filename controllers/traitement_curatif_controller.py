from database.db_session import SessionLocal
from database.models import TraitementCuratif

class TraitementCuratifController:
    @staticmethod
    def get_traitements_par_eleveur(code_elevage):
        db = SessionLocal()
        result = db.query(TraitementCuratif).filter(TraitementCuratif.code_elevage == code_elevage).all()
        db.close()
        return result

    @staticmethod
    def ajouter_traitement(data):
        db = SessionLocal()
        try:
            t = TraitementCuratif(**data)
            db.add(t)
            db.commit()
            return True, t.id, "Traitement ajouté"
        except Exception as e:
            db.rollback()
            return False, None, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_traitement(traitement_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            t = db.query(TraitementCuratif).filter(TraitementCuratif.id == traitement_id).first()
            if not t:
                return False, "Traitement introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(t, key) and value is not None:
                    setattr(t, key, value)
            db.commit()
            return True, "Traitement modifié"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_traitement(traitement_id):
        db = SessionLocal()
        try:
            t = db.query(TraitementCuratif).filter(TraitementCuratif.id == traitement_id).first()
            if t:
                db.delete(t)
                db.commit()
                return True, "Traitement supprimé"
            return False, "Traitement introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()