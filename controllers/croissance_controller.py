from datetime import datetime
from database.db_session import SessionLocal
from database.models.croissance import Croissance
from database.models.sevrage import Sevrage
from database.models.naissance import Naissance

class CroissanceController:
    @staticmethod
    def get_animaux_avec_sevrage(code_elevage: str):
        """Renvoie les animaux qui ont un sevrage enregistré (donc éligibles aux pesées)."""
        try:
            db = SessionLocal()
            sevrages = db.query(Sevrage.numero_boucle).filter(Sevrage.code_elevage == code_elevage).all()
            boucles = [s[0] for s in sevrages]
            animaux = []
            for b in boucles:
                naissance = db.query(Naissance).filter(
                    Naissance.code_elevage == code_elevage,
                    Naissance.numero_boucle == b
                ).first()
                if naissance:
                    animaux.append({
                        'numero_boucle': b,
                        'date_naissance': naissance.date_naissance,
                        'categorie': 'Sevré'
                    })
                else:
                    animaux.append({
                        'numero_boucle': b,
                        'date_naissance': 'inconnue',
                        'categorie': 'Sevré'
                    })
            db.close()
            return animaux
        except Exception:
            return []

    @staticmethod
    def get_nb_pesees_animal(code_elevage: str, numero_boucle: str) -> int:
        """Retourne le nombre de pesées déjà enregistrées pour un animal."""
        try:
            db = SessionLocal()
            count = db.query(Croissance).filter(
                Croissance.code_elevage == code_elevage,
                Croissance.numero_boucle == numero_boucle
            ).count()
            db.close()
            return count
        except Exception:
            return 0

    @staticmethod
    def get_derniere_pesee(code_elevage: str, numero_boucle: str):
        try:
            db = SessionLocal()
            pesee = db.query(Croissance).filter(
                Croissance.code_elevage == code_elevage,
                Croissance.numero_boucle == numero_boucle
            ).order_by(Croissance.date_pesee.desc()).first()
            db.close()
            return pesee
        except Exception:
            return None

    @staticmethod
    def get_poids_sevrage(code_elevage: str, numero_boucle: str):
        try:
            db = SessionLocal()
            sevrage = db.query(Sevrage).filter(
                Sevrage.code_elevage == code_elevage,
                Sevrage.numero_boucle == numero_boucle
            ).first()
            db.close()
            if sevrage:
                return sevrage.poids_sevrage, sevrage.date_sevrage
            return None, None
        except Exception:
            return None, None

    @staticmethod
    def calculer_gmq_post_sevrage(poids_actuel, poids_precedent, jours):
        if jours <= 0:
            return 0
        gain = poids_actuel - poids_precedent
        return (gain / jours) * 1000

    @staticmethod
    def ajouter_pesee(data: dict) -> (bool, str):
        try:
            db = SessionLocal()
            sevrage = db.query(Sevrage).filter(
                Sevrage.code_elevage == data['code_elevage'],
                Sevrage.numero_boucle == data['numero_boucle']
            ).first()
            if not sevrage:
                db.close()
                return False, "Cet animal n'a pas de sevrage enregistré."

            if data['date_pesee'] <= sevrage.date_sevrage:
                db.close()
                return False, "La date de pesée doit être postérieure à la date de sevrage."

            derniere = CroissanceController.get_derniere_pesee(data['code_elevage'], data['numero_boucle'])
            if derniere:
                if data['date_pesee'] <= derniere.date_pesee:
                    db.close()
                    return False, "La date doit être postérieure à la dernière pesée."
                if data['poids'] <= derniere.poids:
                    db.close()
                    return False, "Le poids doit être supérieur au dernier poids."
                jours = (datetime.strptime(data['date_pesee'], "%Y-%m-%d") - datetime.strptime(derniere.date_pesee, "%Y-%m-%d")).days
                gmq = CroissanceController.calculer_gmq_post_sevrage(data['poids'], derniere.poids, jours)
            else:
                poids_sevrage, date_sevrage = CroissanceController.get_poids_sevrage(data['code_elevage'], data['numero_boucle'])
                if poids_sevrage is None:
                    db.close()
                    return False, "Poids au sevrage introuvable."
                if data['poids'] <= poids_sevrage:
                    db.close()
                    return False, "Le poids doit être supérieur au poids au sevrage."
                jours = (datetime.strptime(data['date_pesee'], "%Y-%m-%d") - datetime.strptime(date_sevrage, "%Y-%m-%d")).days
                gmq = CroissanceController.calculer_gmq_post_sevrage(data['poids'], poids_sevrage, jours)

            pesee = Croissance(
                code_elevage=data['code_elevage'],
                numero_boucle=data['numero_boucle'],
                date_pesee=data['date_pesee'],
                poids=data['poids'],
                gmq_post_sevrage=gmq
            )
            db.add(pesee)
            db.commit()
            db.close()
            return True, f"Pesée ajoutée, GMQ = {gmq:.1f} g/j"
        except Exception as e:
            return False, f"Erreur technique : {str(e)}"

    @staticmethod
    def get_pesees_par_animal(code_elevage: str, numero_boucle: str = None):
        try:
            db = SessionLocal()
            query = db.query(Croissance).filter(Croissance.code_elevage == code_elevage)
            if numero_boucle:
                query = query.filter(Croissance.numero_boucle == numero_boucle)
            pesees = query.order_by(Croissance.date_pesee).all()
            db.close()
            return pesees
        except Exception:
            return []

    @staticmethod
    def modifier_pesee(pesee_id: int, data: dict) -> (bool, str):
        # À implémenter si nécessaire
        pass

    @staticmethod
    def supprimer_pesee(pesee_id: int) -> (bool, str):
        try:
            db = SessionLocal()
            pesee = db.query(Croissance).filter(Croissance.id == pesee_id).first()
            if not pesee:
                db.close()
                return False, "Pesée introuvable"
            db.delete(pesee)
            db.commit()
            db.close()
            return True, "Pesée supprimée"
        except Exception as e:
            return False, f"Erreur : {str(e)}"