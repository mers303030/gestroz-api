# recreate_agro_tables.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import engine, SessionLocal
from sqlalchemy import text
from database.models import Parcelle, FicheCulturale, Arbre

def drop_and_create():
    db = SessionLocal()
    try:
        # Supprimer les tables si elles existent
        db.execute(text("DROP TABLE IF EXISTS arbres;"))
        db.execute(text("DROP TABLE IF EXISTS fiches_culturales;"))
        db.execute(text("DROP TABLE IF EXISTS parcelles;"))
        db.commit()
        print("✅ Anciennes tables agronomiques supprimées.")
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
    finally:
        db.close()

    # Recréer les tables avec le bon schéma
    try:
        Parcelle.__table__.create(engine, checkfirst=True)
        print("✅ Table 'parcelles' recréée.")
        FicheCulturale.__table__.create(engine, checkfirst=True)
        print("✅ Table 'fiches_culturales' recréée.")
        Arbre.__table__.create(engine, checkfirst=True)
        print("✅ Table 'arbres' recréée.")
        print("\n✅ Toutes les tables agronomiques sont maintenant à jour.")
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")

if __name__ == "__main__":
    drop_and_create()