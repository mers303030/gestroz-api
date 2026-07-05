from database.db_session import SessionLocal
from database.models import Soin, Animal

class SoinController:
    @staticmethod
    def get_soins_par_animal(code_elevage, numero_boucle):
        db = SessionLocal()
        result = db.query(Soin).filter(
            Soin.code_elevage == code_elevage,
            Soin.numero_boucle == numero_boucle
        ).order_by(Soin.date_soin.desc()).all()
        db.close()
        return result

    @staticmethod
    def get_soins_par_eleveur(code_elevage=None):
        db = SessionLocal()
        query = db.query(Soin)
        if code_elevage:
            query = query.filter(Soin.code_elevage == code_elevage)
        result = query.order_by(Soin.date_soin.desc()).all()
        db.close()
        return result

    @staticmethod
    def get_animaux_actifs(code_elevage):
        db = SessionLocal()
        animaux = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.actif == True
        ).all()
        db.close()
        return animaux

    @staticmethod
    def ajouter_soin(data):
        db = SessionLocal()
        try:
            soin = Soin(
                code_elevage=data['code_elevage'],
                numero_boucle=data['numero_boucle'],
                date_soin=data['date_soin'],
                type_soin=data['type_soin'],
                produit=data.get('produit'),
                dose=data.get('dose'),
                voie=data.get('voie'),
                veterinaire=data.get('veterinaire'),
                date_rappel=data.get('date_rappel'),
                observations=data.get('observations')
            )
            db.add(soin)
            db.commit()
            return True, "Soin ajouté"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def modifier_soin(soin_id, nouvelles_donnees):
        db = SessionLocal()
        try:
            soin = db.query(Soin).filter(Soin.id == soin_id).first()
            if not soin:
                return False, "Soin introuvable"
            for key, value in nouvelles_donnees.items():
                if hasattr(soin, key) and value is not None:
                    setattr(soin, key, value)
            db.commit()
            return True, "Soin modifié"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def supprimer_soin(soin_id):
        db = SessionLocal()
        try:
            soin = db.query(Soin).filter(Soin.id == soin_id).first()
            if soin:
                db.delete(soin)
                db.commit()
                return True, "Soin supprimé"
            return False, "Soin introuvable"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()