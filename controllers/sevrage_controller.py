from datetime import datetime
from database.db_session import SessionLocal
from database.models.animal import Animal
from database.models.naissance import Naissance
from database.models.sevrage import Sevrage

class SevrageController:
    @staticmethod
    def get_animaux_a_sevrer(code_elevage: str):
        db = SessionLocal()
        # Récupérer les naissances dont l'animal est actif et non sevré
        naissances = db.query(Naissance).filter(Naissance.code_elevage == code_elevage).all()
        sevrages = db.query(Sevrage.numero_boucle).filter(Sevrage.code_elevage == code_elevage).all()
        sevred = {s[0] for s in sevrages}
        a_sevrer = []
        for n in naissances:
            if n.numero_boucle in sevred:
                continue
            animal = db.query(Animal).filter(
                Animal.code_elevage == code_elevage,
                Animal.numero_boucle == n.numero_boucle,
                Animal.actif == True
            ).first()
            if animal:
                a_sevrer.append(animal)
        db.close()
        return a_sevrer

    @staticmethod
    def ajouter_sevrage(data: dict) -> (bool, str):
        db = SessionLocal()
        animal = db.query(Animal).filter(
            Animal.code_elevage == data['code_elevage'],
            Animal.numero_boucle == data['numero_boucle'],
            Animal.actif == True
        ).first()
        if not animal:
            db.close()
            return False, "Animal introuvable ou inactif"
        if db.query(Sevrage).filter(
            Sevrage.code_elevage == data['code_elevage'],
            Sevrage.numero_boucle == data['numero_boucle']
        ).first():
            db.close()
            return False, "Cet animal a déjà été sevré"
        poids = data['poids_sevrage']
        if poids <= 0:
            db.close()
            return False, "Le poids au sevrage doit être supérieur à 0"
        if data['date_sevrage'] <= animal.date_naissance:
            db.close()
            return False, "La date de sevrage doit être postérieure à la date de naissance"
        naissance = db.query(Naissance).filter(
            Naissance.code_elevage == data['code_elevage'],
            Naissance.numero_boucle == data['numero_boucle']
        ).first()
        poids_naissance = naissance.poids_naissance if naissance else (animal.poids_naissance or 0)
        gmq = SevrageController.calculer_gmq(animal.date_naissance, poids_naissance, data['date_sevrage'], poids)
        sevrage = Sevrage(
            code_elevage=data['code_elevage'],
            numero_boucle=data['numero_boucle'],
            date_sevrage=data['date_sevrage'],
            poids_sevrage=poids,
            gmq_naissance_sevrage=gmq
        )
        db.add(sevrage)
        db.commit()
        db.close()
        return True, f"Sevrage enregistré, GMQ = {gmq:.1f} g/j"

    @staticmethod
    def calculer_gmq(date_naissance_str, poids_naissance, date_sevrage_str, poids_sevrage):
        naiss = datetime.strptime(date_naissance_str, "%Y-%m-%d")
        sev = datetime.strptime(date_sevrage_str, "%Y-%m-%d")
        jours = (sev - naiss).days
        if jours <= 0:
            return 0
        gain_kg = poids_sevrage - poids_naissance
        return (gain_kg / jours) * 1000