from database.db_session import SessionLocal
from database.models import Parcelle, FicheCulturale

class ParcelleController:
    # --- Parcelles ---
    @staticmethod
    def get_parcelles_par_eleveur(code_elevage):
        db = SessionLocal()
        result = db.query(Parcelle).filter(Parcelle.code_elevage == code_elevage).all()
        db.close()
        return result

    @staticmethod
    def ajouter_parcelle(data):
        db = SessionLocal()
        try:
            p = Parcelle(**data)
            db.add(p)
            db.commit()
            return True, p.id, "Parcelle ajoutée"
        except Exception as e:
            db.rollback()
            return False, None, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_parcelle(parcelle_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            p = db.query(Parcelle).filter(Parcelle.id == parcelle_id).first()
            if not p:
                return False, "Parcelle introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(p, key) and value is not None:
                    setattr(p, key, value)
            db.commit()
            return True, "Parcelle modifiée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_parcelle(parcelle_id):
        db = SessionLocal()
        try:
            p = db.query(Parcelle).filter(Parcelle.id == parcelle_id).first()
            if p:
                db.query(FicheCulturale).filter(FicheCulturale.parcelle_id == parcelle_id).delete()
                db.delete(p)
                db.commit()
                return True, "Parcelle supprimée"
            return False, "Parcelle introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    # --- Fiches culturales ---
    @staticmethod
    def get_fiche_par_parcelle_annee(parcelle_id, annee):
        db = SessionLocal()
        result = db.query(FicheCulturale).filter(
            FicheCulturale.parcelle_id == parcelle_id,
            FicheCulturale.annee == annee
        ).first()
        db.close()
        return result

    @staticmethod
    def get_all_fiches_par_parcelle(parcelle_id):
        db = SessionLocal()
        result = db.query(FicheCulturale).filter(FicheCulturale.parcelle_id == parcelle_id).order_by(FicheCulturale.annee.desc()).all()
        db.close()
        return result

    @staticmethod
    def ajouter_fiche(data):
        db = SessionLocal()
        try:
            f = FicheCulturale(**data)
            db.add(f)
            db.commit()
            return True, "Fiche enregistrée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_fiche(fiche_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            f = db.query(FicheCulturale).filter(FicheCulturale.id == fiche_id).first()
            if not f:
                return False, "Fiche introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(f, key) and value is not None:
                    setattr(f, key, value)
            db.commit()
            return True, "Fiche modifiée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_fiche(fiche_id):
        db = SessionLocal()
        try:
            f = db.query(FicheCulturale).filter(FicheCulturale.id == fiche_id).first()
            if f:
                db.delete(f)
                db.commit()
                return True, "Fiche supprimée"
            return False, "Fiche introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()