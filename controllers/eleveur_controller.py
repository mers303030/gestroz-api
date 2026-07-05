from database.db_session import SessionLocal
from database.models.eleveur import Eleveur

class EleveurController:
    @staticmethod
    def generer_code_elevage(commune: str) -> str:
        prefix = {'Oulmès': 'OLM', 'Aït Ichou': 'AIT', 'Boukchmir': 'BOK'}[commune]
        db = SessionLocal()
        count = db.query(Eleveur).filter(Eleveur.code_elevage.like(f'{prefix}%')).count()
        db.close()
        return f"{prefix}{count+1:03d}"

    @staticmethod
    def ajouter_eleveur(data: dict) -> (bool, str):
        db = SessionLocal()
        if db.query(Eleveur).filter(Eleveur.cnie == data.get('cnie')).first():
            db.close()
            return False, "CNIE déjà existant"
        if db.query(Eleveur).filter(Eleveur.telephone == data.get('telephone')).first():
            db.close()
            return False, "Téléphone déjà existant"
        if not data.get('code_elevage'):
            data['code_elevage'] = EleveurController.generer_code_elevage(data['commune'])
        eleveur = Eleveur(**data)
        db.add(eleveur)
        db.commit()
        db.close()
        return True, "Éleveur ajouté"

    @staticmethod
    def modifier_eleveur(code: str, data: dict) -> (bool, str):
        db = SessionLocal()
        eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
        if not eleveur:
            db.close()
            return False, "Éleveur introuvable"
        if 'cnie' in data and data['cnie'] != eleveur.cnie:
            if db.query(Eleveur).filter(Eleveur.cnie == data['cnie']).first():
                db.close()
                return False, "CNIE déjà utilisé par un autre éleveur"
        if 'telephone' in data and data['telephone'] != eleveur.telephone:
            if db.query(Eleveur).filter(Eleveur.telephone == data['telephone']).first():
                db.close()
                return False, "Téléphone déjà utilisé par un autre éleveur"
        for key, value in data.items():
            setattr(eleveur, key, value)
        db.commit()
        db.close()
        return True, "Éleveur modifié"

    @staticmethod
    def supprimer_eleveur(code: str) -> (bool, str):
        db = SessionLocal()
        eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
        if not eleveur:
            db.close()
            return False, "Éleveur introuvable"
        db.delete(eleveur)
        db.commit()
        db.close()
        return True, "Éleveur supprimé"

    @staticmethod
    def get_all_eleveurs():
        db = SessionLocal()
        eleveurs = db.query(Eleveur).all()
        db.close()
        return eleveurs