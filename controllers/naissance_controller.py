from datetime import datetime, timedelta
from database.db_session import SessionLocal
from database.models.animal import Animal
from database.models.naissance import Naissance
from controllers.animal_controller import AnimalController

class NaissanceController:
    @staticmethod
    def get_meres_potentielles(code_elevage: str):
        db = SessionLocal()
        femelles = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.sexe == 'F',
            Animal.categorie.in_(['Vache', 'Génisse']),
            Animal.actif == True
        ).all()
        dernier_velage = {}
        naissances = db.query(Naissance).filter(Naissance.code_elevage == code_elevage).all()
        for n in naissances:
            if n.mere_boucle not in dernier_velage or n.date_naissance > dernier_velage[n.mere_boucle]:
                dernier_velage[n.mere_boucle] = n.date_naissance
        aujourdhui = datetime.now().date()
        meres_disponibles = []
        for f in femelles:
            derniere = dernier_velage.get(f.numero_boucle)
            if derniere:
                derniere_date = datetime.strptime(derniere, "%Y-%m-%d").date()
                if (aujourdhui - derniere_date).days < 365:
                    continue
            meres_disponibles.append(f)
        db.close()
        return meres_disponibles

    @staticmethod
    def enregistrer_naissance(data: dict) -> (bool, str):
        poids = data.get('poids_naissance')
        if not poids or poids == "":
            return False, "Le poids à la naissance est obligatoire."
        try:
            poids = float(poids)
            if poids < 12 or poids > 26:
                return False, "Le poids à la naissance doit être compris entre 12 et 26 kg."
        except:
            return False, "Le poids doit être un nombre."
        if not data.get('type_velage'):
            return False, "Le type de vêlage est obligatoire."
        db = SessionLocal()
        # Vérifier que la mère existe et est active
        mere = db.query(Animal).filter(
            Animal.code_elevage == data['code_elevage'],
            Animal.numero_boucle == data['mere_boucle'],
            Animal.actif == True
        ).first()
        if not mere:
            db.close()
            return False, "Mère introuvable ou inactive"
        # Vérifier que le numéro de boucle du veau n'existe pas
        existant = db.query(Animal).filter(
            Animal.code_elevage == data['code_elevage'],
            Animal.numero_boucle == data['numero_boucle']
        ).first()
        if existant:
            db.close()
            return False, "Ce numéro de boucle existe déjà pour cet éleveur"
        # Créer l'animal (actif)
        animal_data = {
            'code_elevage': data['code_elevage'],
            'numero_boucle': data['numero_boucle'],
            'date_naissance': data['date_naissance'],
            'sexe': data['sexe'],
            'race': data['race'],
            'origine': 'Né à l\'élevage',
            'date_entree': '',
            'poids_naissance': poids,
            'mere_boucle': data['mere_boucle'],
            'pere_boucle': data.get('pere_boucle'),
            'type_velage': data['type_velage'],
            'actif': True
        }
        animal_data['categorie'] = AnimalController.calculer_categorie(data['sexe'], data['date_naissance'])
        animal = Animal(**animal_data)
        db.add(animal)
        naissance = Naissance(**data)
        db.add(naissance)
        db.commit()
        db.close()
        return True, "Naissance enregistrée et animal créé"