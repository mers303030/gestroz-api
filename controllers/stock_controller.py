from database.db_session import SessionLocal
from database.models.stock import Stock
from database.models.aliment_base import AlimentBase

class StockController:
    @staticmethod
    def ajouter_stock(data: dict) -> (bool, str):
        db = SessionLocal()
        try:
            # Vérifier que l'aliment de base existe
            aliment = db.query(AlimentBase).filter(AlimentBase.id == data['aliment_base_id']).first()
            if not aliment:
                db.close()
                return False, "Aliment de base introuvable"
            stock = Stock(**data)
            db.add(stock)
            db.commit()
            db.close()
            return True, "Lot ajouté au stock"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def modifier_stock(stock_id: int, data: dict) -> (bool, str):
        db = SessionLocal()
        try:
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock:
                db.close()
                return False, "Lot introuvable"
            for key, value in data.items():
                setattr(stock, key, value)
            db.commit()
            db.close()
            return True, "Lot modifié"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def supprimer_stock(stock_id: int) -> (bool, str):
        db = SessionLocal()
        try:
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock:
                db.close()
                return False, "Lot introuvable"
            db.delete(stock)
            db.commit()
            db.close()
            return True, "Lot supprimé"
        except Exception as e:
            db.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def get_stocks_par_eleveur(code_elevage: str = None):
        db = SessionLocal()
        query = db.query(Stock)
        if code_elevage:
            query = query.filter(Stock.code_elevage == code_elevage)
        stocks = query.order_by(Stock.date_entree.desc()).all()
        db.close()
        return stocks