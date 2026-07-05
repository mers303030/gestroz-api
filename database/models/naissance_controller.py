from database.db_session import SessionLocal
from database.models.animal import Animal
from database.models.naissance import Naissance
from database.models.sevrage import Sevrage
from database.models.suivi_animal import SuiviAnimal
from datetime import datetime, date

class NaissanceController:
    @staticmethod
    def enregistrer_naissance(data):
        """
        data = {
            'code_elevage': str,
            'mere_boucle': str,
            'date_naissance': str (YYYY-MM-DD),
            'sexe': str,
            'race': str,
            'poids_naissance': float,
            'pere_boucle': str or None,
            'numero_boucle': str,
            'type_velage': str,
            'observations': str or None
        }
        """
        db = SessionLocal()
        try:
            # Récupérer la mère (obligatoire)
            mere = db.query(Animal).filter(
                Animal.code_elevage == data['code_elevage'],
                Animal.numero_boucle == data['mere_boucle']
            ).first()
            if not mere:
                return False, "Mère introuvable dans la base"

            # Récupérer le père (optionnel)
            pere = None
            if data.get('pere_boucle'):
                pere = db.query(Animal).filter(
                    Animal.code_elevage == data['code_elevage'],
                    Animal.numero_boucle == data['pere_boucle']
                ).first()
                # Note : on pourrait aussi étendre la recherche à la commune comme dans l'original

            # Création de l'enregistrement Naissance avec les champs redondants
            naissance = Naissance(
                code_elevage=data['code_elevage'],
                mere_boucle=data['mere_boucle'],
                date_naissance=data['date_naissance'],
                sexe=data['sexe'],
                race=data['race'],
                poids_naissance=data['poids_naissance'],
                pere_boucle=data.get('pere_boucle'),
                numero_boucle=data['numero_boucle'],
                type_velage=data['type_velage'],
                observations=data.get('observations'),
                # Copie des informations de la mère
                mere_categorie=mere.categorie,
                mere_date_naissance=mere.date_naissance,
                mere_race=mere.race,
                # Copie des informations du père
                pere_categorie=pere.categorie if pere else None,
                pere_date_naissance=pere.date_naissance if pere else None,
                pere_race=pere.race if pere else None
            )
            db.add(naissance)
            db.commit()
            return True, "Naissance enregistrée avec les informations parentales"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_naissance(naissance_id, nouvelles_donnees):
        """Met à jour une naissance et synchronise Animal, Sevrage et SuiviAnimal"""
        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == naissance_id).first()
            if not naissance:
                return False, "Naissance introuvable"

            ancien_code = naissance.code_elevage
            ancien_numero = naissance.numero_boucle

            # Mise à jour de la naissance
            for key, value in nouvelles_donnees.items():
                if hasattr(naissance, key) and value is not None:
                    setattr(naissance, key, value)

            # Mise à jour de l'animal associé
            animal = db.query(Animal).filter(
                Animal.code_elevage == ancien_code,
                Animal.numero_boucle == ancien_numero
            ).first()
            if animal:
                if 'numero_boucle' in nouvelles_donnees:
                    animal.numero_boucle = nouvelles_donnees['numero_boucle']
                if 'date_naissance' in nouvelles_donnees:
                    animal.date_naissance = nouvelles_donnees['date_naissance']
                if 'sexe' in nouvelles_donnees:
                    animal.sexe = nouvelles_donnees['sexe']
                if 'race' in nouvelles_donnees:
                    animal.race = nouvelles_donnees['race']
                if 'poids_naissance' in nouvelles_donnees:
                    animal.poids_naissance = nouvelles_donnees['poids_naissance']
                if 'pere_boucle' in nouvelles_donnees:
                    animal.pere_boucle = nouvelles_donnees['pere_boucle']
                if 'type_velage' in nouvelles_donnees:
                    animal.type_velage = nouvelles_donnees['type_velage']

            # Mise à jour du sevrage si changement de clé
            if 'code_elevage' in nouvelles_donnees or 'numero_boucle' in nouvelles_donnees:
                nouveau_code = nouvelles_donnees.get('code_elevage', ancien_code)
                nouveau_numero = nouvelles_donnees.get('numero_boucle', ancien_numero)
                sevrage = db.query(Sevrage).filter(
                    Sevrage.code_elevage == ancien_code,
                    Sevrage.numero_boucle == ancien_numero
                ).first()
                if sevrage:
                    sevrage.code_elevage = nouveau_code
                    sevrage.numero_boucle = nouveau_numero

                # Mise à jour du suivi
                suivi = db.query(SuiviAnimal).filter(
                    SuiviAnimal.code_elevage == ancien_code,
                    SuiviAnimal.numero_boucle == ancien_numero
                ).first()
                if suivi:
                    suivi.code_elevage = nouveau_code
                    suivi.numero_boucle = nouveau_numero
                    if 'date_naissance' in nouvelles_donnees:
                        suivi.date_naissance = nouvelles_donnees['date_naissance']
                    if 'poids_naissance' in nouvelles_donnees:
                        suivi.poids_naissance = nouvelles_donnees['poids_naissance']
                    if 'sexe' in nouvelles_donnees:
                        suivi.sexe = nouvelles_donnees['sexe']
                    if 'race' in nouvelles_donnees:
                        suivi.race = nouvelles_donnees['race']
            else:
                # Pas de changement de clé, mise à jour des champs du suivi
                suivi = db.query(SuiviAnimal).filter(
                    SuiviAnimal.code_elevage == ancien_code,
                    SuiviAnimal.numero_boucle == ancien_numero
                ).first()
                if suivi:
                    if 'date_naissance' in nouvelles_donnees:
                        suivi.date_naissance = nouvelles_donnees['date_naissance']
                    if 'poids_naissance' in nouvelles_donnees:
                        suivi.poids_naissance = nouvelles_donnees['poids_naissance']
                    if 'sexe' in nouvelles_donnees:
                        suivi.sexe = nouvelles_donnees['sexe']
                    if 'race' in nouvelles_donnees:
                        suivi.race = nouvelles_donnees['race']

            db.commit()
            return True, "Naissance modifiée, sevrage et suivi synchronisés"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_naissance(naissance_id):
        """Supprime la naissance, l'animal, le sevrage et le suivi associés"""
        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == naissance_id).first()
            if not naissance:
                return False, "Naissance introuvable"

            code = naissance.code_elevage
            numero = naissance.numero_boucle

            # Supprimer l'animal
            db.query(Animal).filter(
                Animal.code_elevage == code,
                Animal.numero_boucle == numero
            ).delete()

            # Supprimer le sevrage
            db.query(Sevrage).filter(
                Sevrage.code_elevage == code,
                Sevrage.numero_boucle == numero
            ).delete()

            # Supprimer le suivi animal
            db.query(SuiviAnimal).filter(
                SuiviAnimal.code_elevage == code,
                SuiviAnimal.numero_boucle == numero
            ).delete()

            # Supprimer la naissance elle-même
            db.delete(naissance)

            db.commit()
            return True, "Naissance et toutes ses dépendances supprimées"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()