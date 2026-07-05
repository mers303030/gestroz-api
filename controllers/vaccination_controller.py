from database.db_session import SessionLocal
from database.models import Vaccination

class VaccinationController:
    @staticmethod
    def get_vaccinations_par_eleveur(code_elevage):
        db = SessionLocal()
        result = db.query(Vaccination).filter(Vaccination.code_elevage == code_elevage).all()
        db.close()
        return result

    @staticmethod
    def ajouter_vaccination(data):
        db = SessionLocal()
        try:
            v = Vaccination(**data)
            db.add(v)
            db.commit()
            return True, v.id, "Vaccination ajoutée"
        except Exception as e:
            db.rollback()
            return False, None, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_vaccination(vaccination_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            v = db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
            if not v:
                return False, "Vaccination introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(v, key) and value is not None:
                    setattr(v, key, value)
            db.commit()
            return True, "Vaccination modifiée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_vaccination(vaccination_id):
        db = SessionLocal()
        try:
            v = db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
            if v:
                db.delete(v)
                db.commit()
                return True, "Vaccination supprimée"
            return False, "Vaccination introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()