from database.db_session import SessionLocal
from database.models import Naissance, Vente
from database.models.animal import Animal

class VenteController:
    @staticmethod
    def get_animaux_vendables(code_elevage):
        """Union des animaux actifs dans Naissance et Animal."""
        db = SessionLocal()
        naissances = db.query(Naissance).filter(
            Naissance.code_elevage == code_elevage,
            Naissance.actif == True
        ).all()
        animaux = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.actif == True
        ).all()
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
    def get_ventes_par_eleveur(code_elevage=None):
        db = SessionLocal()
        query = db.query(Vente)
        if code_elevage:
            query = query.filter(Vente.code_elevage == code_elevage)
        result = query.all()
        db.close()
        return result

    @staticmethod
    def ajouter_vente(data):
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
                return False, "Cet animal n'est pas actif"
            vente = Vente(
                code_elevage=data['code_elevage'],
                numero_boucle=data['numero_boucle'],
                date_vente=data['date_vente'],
                prix_vente=data['prix_vente'],
                lieu_vente=data['lieu_vente'],
                poids_vente=data.get('poids_vente'),
                remarque=data.get('remarque')
            )
            db.add(vente)
            if naiss:
                naiss.actif = False
            if anim:
                anim.actif = False
            db.commit()
            return True, "Vente enregistrée, animal désactivé"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_vente(vente_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            vente = db.query(Vente).filter(Vente.id == vente_id).first()
            if not vente:
                return False, "Vente introuvable"
            ancien_code = vente.code_elevage
            ancien_num = vente.numero_boucle
            vente.numero_boucle = nouvelles_donnees.get('numero_boucle', vente.numero_boucle)
            vente.date_vente = nouvelles_donnees.get('date_vente', vente.date_vente)
            vente.prix_vente = nouvelles_donnees.get('prix_vente', vente.prix_vente)
            vente.lieu_vente = nouvelles_donnees.get('lieu_vente', vente.lieu_vente)
            vente.poids_vente = nouvelles_donnees.get('poids_vente', vente.poids_vente)
            vente.remarque = nouvelles_donnees.get('remarque', vente.remarque)
            if (vente.code_elevage, vente.numero_boucle) != (ancien_code, ancien_num):
                for table in (Naissance, Animal):
                    ancien = db.query(table).filter(
                        table.code_elevage == ancien_code,
                        table.numero_boucle == ancien_num
                    ).first()
                    if ancien:
                        ancien.actif = True
                for table in (Naissance, Animal):
                    nouveau = db.query(table).filter(
                        table.code_elevage == vente.code_elevage,
                        table.numero_boucle == vente.numero_boucle
                    ).first()
                    if nouveau:
                        nouveau.actif = False
            db.commit()
            return True, "Vente modifiée"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_vente(vente_id):
        db = SessionLocal()
        try:
            vente = db.query(Vente).filter(Vente.id == vente_id).first()
            if not vente:
                return False, "Vente introuvable"
            for table in (Naissance, Animal):
                animal = db.query(table).filter(
                    table.code_elevage == vente.code_elevage,
                    table.numero_boucle == vente.numero_boucle
                ).first()
                if animal:
                    animal.actif = True
            db.delete(vente)
            db.commit()
            return True, "Vente supprimée, animal réactivé"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()