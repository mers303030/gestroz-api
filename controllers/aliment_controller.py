from database.db_session import SessionLocal
from database.models.aliment import Aliment

class AlimentController:
    @staticmethod
    def ajouter_aliment(data: dict) -> (bool, str):
        db = SessionLocal()
        try:
            aliment = Aliment(**data)
            db.add(aliment)
            db.commit()
            db.close()
            return True, "Aliment ajouté"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def modifier_aliment(aliment_id: int, data: dict) -> (bool, str):
        db = SessionLocal()
        try:
            aliment = db.query(Aliment).filter(Aliment.id == aliment_id).first()
            if not aliment:
                db.close()
                return False, "Aliment introuvable"
            for key, value in data.items():
                setattr(aliment, key, value)
            db.commit()
            db.close()
            return True, "Aliment modifié"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def supprimer_aliment(aliment_id: int) -> (bool, str):
        db = SessionLocal()
        try:
            aliment = db.query(Aliment).filter(Aliment.id == aliment_id).first()
            if not aliment:
                db.close()
                return False, "Aliment introuvable"
            db.delete(aliment)
            db.commit()
            db.close()
            return True, "Aliment supprimé"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def get_all_aliments():
        db = SessionLocal()
        aliments = db.query(Aliment).all()
        db.close()
        return aliments