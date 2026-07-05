# create_agro_tables.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import Base, engine
from database.models import Parcelle, FicheCulturale, Arbre

def create_agro_tables():
    try:
        # Crée uniquement les tables qui n'existent pas encore
        Base.metadata.create_all(engine, tables=[Parcelle.__table__, FicheCulturale.__table__, Arbre.__table__])
        print("✅ Tables agronomiques créées avec succès.")
        print("   - parcelles")
        print("   - fiches_culturales")
        print("   - arbres")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    create_agro_tables()