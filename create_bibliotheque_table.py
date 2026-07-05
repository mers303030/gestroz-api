# create_bibliotheque_table.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import SessionLocal, engine
from database.models.bibliotheque_aliment import BibliothequeAliment

def create_table():
    try:
        BibliothequeAliment.__table__.create(engine, checkfirst=True)
        print("✅ Table 'bibliotheque_aliments' créée avec succès.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    create_table()