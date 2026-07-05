from database.db_session import SessionLocal
from database.models import PrixVenteProduit

class PrixVenteProduitController:
    @staticmethod
    def get_prix_par_eleveur(code_elevage, annee=None):
        db = SessionLocal()
        query = db.query(PrixVenteProduit).filter(PrixVenteProduit.code_elevage == code_elevage)
        if annee:
            query = query.filter(PrixVenteProduit.annee == annee)
        result = query.all()
        db.close()
        return result

    @staticmethod
    def ajouter_prix(data):
        db = SessionLocal()
        try:
            p = PrixVenteProduit(**data)
            db.add(p)
            db.commit()
            return True, p.id, "Prix ajouté"
        except Exception as e:
            db.rollback()
            return False, None, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_prix(prix_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            p = db.query(PrixVenteProduit).filter(PrixVenteProduit.id == prix_id).first()
            if not p:
                return False, "Prix introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(p, key) and value is not None:
                    setattr(p, key, value)
            db.commit()
            return True, "Prix modifié"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_prix(prix_id):
        db = SessionLocal()
        try:
            p = db.query(PrixVenteProduit).filter(PrixVenteProduit.id == prix_id).first()
            if p:
                db.delete(p)
                db.commit()
                return True, "Prix supprimé"
            return False, "Prix introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()