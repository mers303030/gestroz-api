from sqlalchemy import func
from database.db_session import SessionLocal
from database.models import CoutOperation

class CoutOperationController:
    @staticmethod
    def get_couts_par_eleveur(code_elevage, annee=None):
        db = SessionLocal()
        query = db.query(CoutOperation).filter(CoutOperation.code_elevage == code_elevage)
        if annee:
            query = query.filter(CoutOperation.annee == annee)
        result = query.all()
        db.close()
        return result

    @staticmethod
    def get_couts_par_type(code_elevage, annee):
        db = SessionLocal()
        result = db.query(CoutOperation.type_operation, func.sum(CoutOperation.montant)).filter(
            CoutOperation.code_elevage == code_elevage,
            CoutOperation.annee == annee
        ).group_by(CoutOperation.type_operation).all()
        db.close()
        return result

    @staticmethod
    def ajouter_cout(data):
        db = SessionLocal()
        try:
            c = CoutOperation(**data)
            db.add(c)
            db.commit()
            return True, c.id, "Coût ajouté"
        except Exception as e:
            db.rollback()
            return False, None, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_cout(cout_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            c = db.query(CoutOperation).filter(CoutOperation.id == cout_id).first()
            if not c:
                return False, "Coût introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(c, key) and value is not None:
                    setattr(c, key, value)
            db.commit()
            return True, "Coût modifié"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_cout(cout_id):
        db = SessionLocal()
        try:
            c = db.query(CoutOperation).filter(CoutOperation.id == cout_id).first()
            if c:
                db.delete(c)
                db.commit()
                return True, "Coût supprimé"
            return False, "Coût introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()
