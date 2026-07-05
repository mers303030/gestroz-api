from datetime import datetime
from database.db_session import SessionLocal
from database.models.animal import Animal
from database.models.eleveur import Eleveur

class AnimalController:
    @staticmethod
    def calculer_categorie(sexe: str, date_naissance_str: str) -> str:
        if not date_naissance_str:
            return ""
        try:
            naissance = datetime.strptime(date_naissance_str, "%Y-%m-%d")
            aujourdhui = datetime.now()
            age_jours = (aujourdhui - naissance).days
            age_mois = age_jours / 30.44
            if sexe == 'F':
                if age_mois >= 24:
                    return "Vache"
                elif 12 <= age_mois < 24:
                    return "Génisse"
                else:
                    return "Velle"
            else:
                if age_mois >= 24:
                    return "Géniteur"
                elif 12 <= age_mois < 24:
                    return "Taurillon"
                else:
                    return "Veau"
        except:
            return ""

    @staticmethod
    def ajouter_animal(data: dict) -> (bool, str):
        if not data.get('numero_boucle') or not data['numero_boucle'].strip():
            return False, "Le numéro de boucle est obligatoire"
        db = SessionLocal()
        if not db.query(Eleveur).filter(Eleveur.code_elevage == data['code_elevage']).first():
            db.close()
            return False, "Éleveur introuvable"
        existant = db.query(Animal).filter(
            Animal.code_elevage == data['code_elevage'],
            Animal.numero_boucle == data['numero_boucle']
        ).first()
        if existant:
            db.close()
            return False, "Ce numéro de boucle existe déjà pour cet éleveur"
        data['categorie'] = AnimalController.calculer_categorie(data['sexe'], data['date_naissance'])
        data['actif'] = True  # nouveau né actif
        animal = Animal(**data)
        db.add(animal)
        db.commit()
        db.close()
        return True, "Animal ajouté"

    @staticmethod
    def modifier_animal(animal_id: int, data: dict) -> (bool, str):
        if 'numero_boucle' in data and (not data['numero_boucle'] or not data['numero_boucle'].strip()):
            return False, "Le numéro de boucle ne peut pas être vide"
        db = SessionLocal()
        animal = db.query(Animal).filter(Animal.id == animal_id).first()
        if not animal:
            db.close()
            return False, "Animal introuvable"
        if 'numero_boucle' in data and data['numero_boucle'] != animal.numero_boucle:
            existant = db.query(Animal).filter(
                Animal.code_elevage == animal.code_elevage,
                Animal.numero_boucle == data['numero_boucle']
            ).first()
            if existant:
                db.close()
                return False, "Ce numéro de boucle existe déjà pour cet éleveur"
        if 'sexe' in data or 'date_naissance' in data:
            new_sexe = data.get('sexe', animal.sexe)
            new_date = data.get('date_naissance', animal.date_naissance)
            data['categorie'] = AnimalController.calculer_categorie(new_sexe, new_date)
        for key, value in data.items():
            setattr(animal, key, value)
        db.commit()
        db.close()
        return True, "Animal modifié"

    @staticmethod
    def supprimer_animal(animal_id: int) -> (bool, str):
        db = SessionLocal()
        animal = db.query(Animal).filter(Animal.id == animal_id).first()
        if not animal:
            db.close()
            return False, "Animal introuvable"
        db.delete(animal)
        db.commit()
        db.close()
        return True, "Animal supprimé"

    @staticmethod
    def get_animaux_actifs_par_eleveur(code_elevage: str):
        """Retourne les animaux actifs (non vendus, non décédés)."""
        db = SessionLocal()
        animaux = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.actif == True
        ).all()
        db.close()
        return animaux

    @staticmethod
    def desactiver_animal(code_elevage: str, numero_boucle: str) -> bool:
        """Marque l'animal comme inactif (vendu ou mort)."""
        db = SessionLocal()
        animal = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.numero_boucle == numero_boucle
        ).first()
        if animal:
            animal.actif = False
            db.commit()
            db.close()
            return True
        db.close()
        return False