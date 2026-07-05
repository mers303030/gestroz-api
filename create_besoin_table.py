# create_besoin_table.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import engine
from database.models.besoin_nutritionnel import BesoinNutritionnel

def create_table():
    try:
        BesoinNutritionnel.__table__.create(engine, checkfirst=True)
        print("✅ Table 'besoins_nutritionnels' créée avec succès.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    create_table()