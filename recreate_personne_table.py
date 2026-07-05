# recreate_personne_table.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import engine, SessionLocal
from sqlalchemy import text
from database.models import Personne

def recreate_table():
    db = SessionLocal()
    try:
        # Supprimer la table si elle existe
        db.execute(text("DROP TABLE IF EXISTS personnes;"))
        db.commit()
        print("✅ Ancienne table 'personnes' supprimée (si existante).")
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
    finally:
        db.close()

    # Recréer la table avec le bon schéma
    try:
        Personne.__table__.create(engine, checkfirst=True)
        print("✅ Table 'personnes' recréée avec toutes les colonnes.")
        print("   - id, code_elevage, nom, prenom, date_naissance,")
        print("   - occupation, lien_parente, lieu_residence, observations")
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")

if __name__ == "__main__":
    recreate_table()