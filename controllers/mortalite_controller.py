from database.db_session import SessionLocal
from database.models import Naissance, Mortalite
from database.models.animal import Animal

class MortaliteController:
    @staticmethod
    def get_animaux_vivants(code_elevage):
        """Retourne la liste des animaux actifs (union de Naissance et Animal)."""
        db = SessionLocal()
        naissances = db.query(Naissance).filter(
            Naissance.code_elevage == code_elevage,
            Naissance.actif == True
        ).all()
        animaux = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.actif == True
        ).all()
        # Fusion sans doublon (code_elevage, numero_boucle)
        d = {}
        for a in naissances:
            key = (a.code_elevage, a.numero_boucle)
            d[key] = a
        for a in animaux:
            key = (a.code_elevage, a.numero_boucle)
            if key not in d:
                d[key] = a
        db.close()
        return list(d.values())

    @staticmethod
    def get_mortalites_par_eleveur(code_elevage=None):
        db = SessionLocal()
        query = db.query(Mortalite)
        if code_elevage:
            query = query.filter(Mortalite.code_elevage == code_elevage)
        result = query.all()
        db.close()
        return result

    @staticmethod
    def ajouter_mortalite(data):
        db = SessionLocal()
        try:
            naiss = db.query(Naissance).filter(
                Naissance.code_elevage == data['code_elevage'],
                Naissance.numero_boucle == data['numero_boucle']
            ).first()
            anim = db.query(Animal).filter(
                Animal.code_elevage == data['code_elevage'],
                Animal.numero_boucle == data['numero_boucle']
            ).first()
            if not naiss and not anim:
                return False, "Animal introuvable"
            if (naiss and not naiss.actif) or (anim and not anim.actif):
                return False, "Cet animal est déjà mort ou vendu"

            mort = Mortalite(
                code_elevage=data['code_elevage'],
                numero_boucle=data['numero_boucle'],
                date_deces=data['date_deces'],
                cause_deces=data['cause_deces'],
                remarque=data.get('remarque')
            )
            db.add(mort)
            if naiss:
                naiss.actif = False
            if anim:
                anim.actif = False
            db.commit()
            return True, "Mortalité enregistrée, animal désactivé"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_mortalite(mortalite_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            mort = db.query(Mortalite).filter(Mortalite.id == mortalite_id).first()
            if not mort:
                return False, "Mortalité introuvable"
            ancien_code = mort.code_elevage
            ancien_num = mort.numero_boucle
            mort.numero_boucle = nouvelles_donnees.get('numero_boucle', mort.numero_boucle)
            mort.date_deces = nouvelles_donnees.get('date_deces', mort.date_deces)
            mort.cause_deces = nouvelles_donnees.get('cause_deces', mort.cause_deces)
            mort.remarque = nouvelles_donnees.get('remarque', mort.remarque)
            if (mort.code_elevage, mort.numero_boucle) != (ancien_code, ancien_num):
                for table in (Naissance, Animal):
                    ancien = db.query(table).filter(
                        table.code_elevage == ancien_code,
                        table.numero_boucle == ancien_num
                    ).first()
                    if ancien:
                        ancien.actif = True
                for table in (Naissance, Animal):
                    nouveau = db.query(table).filter(
                        table.code_elevage == mort.code_elevage,
                        table.numero_boucle == mort.numero_boucle
                    ).first()
                    if nouveau:
                        nouveau.actif = False
            db.commit()
            return True, "Mortalité modifiée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_mortalite(mortalite_id):
        db = SessionLocal()
        try:
            mort = db.query(Mortalite).filter(Mortalite.id == mortalite_id).first()
            if not mort:
                return False, "Mortalité introuvable"
            for table in (Naissance, Animal):
                animal = db.query(table).filter(
                    table.code_elevage == mort.code_elevage,
                    table.numero_boucle == mort.numero_boucle
                ).first()
                if animal:
                    animal.actif = True
            db.delete(mort)
            db.commit()
            return True, "Mortalité supprimée, animal réactivé"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()