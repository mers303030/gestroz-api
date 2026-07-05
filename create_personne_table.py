# create_personne_table.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import engine
from database.models.personne import Personne  # <-- Import direct du fichier

def create_table():
    try:
        Personne.__table__.create(engine, checkfirst=True)
        print("✅ Table 'personnes' créée avec succès.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    create_table()