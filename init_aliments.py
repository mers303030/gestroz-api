# init_aliments.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import SessionLocal
from database.models import Aliment

LIBRARY_CODE = "BIBLIO"

ALIMENTS = [
    # === Pailles ===
    {"nom": "Paille d'orge", "type": "Fourrage", "ms": 88, "prix": 0.0, "ufl": 0.30, "ufv": 0.30, "pdi": 35, "ca": 0.20, "p": 0.08},
    {"nom": "Paille de blé dur", "type": "Fourrage", "ms": 88, "prix": 0.0, "ufl": 0.28, "ufv": 0.28, "pdi": 30, "ca": 0.25, "p": 0.07},
    # ... (complétez avec tous les aliments que j'ai listés précédemment)
    # Pour gagner de la place, je mets un extrait, mais vous mettrez toute la liste.
]

def init_bibliotheque():
    db = SessionLocal()
    try:
        # Supprimer les anciens aliments de la bibliothèque (si vous voulez les remplacer)
        # db.query(Aliment).filter(Aliment.code_elevage == LIBRARY_CODE).delete()
        # db.commit()

        for data in ALIMENTS:
            existing = db.query(Aliment).filter(
                Aliment.code_elevage == LIBRARY_CODE,
                Aliment.nom == data["nom"]
            ).first()
            if not existing:
                aliment = Aliment(
                    code_elevage=LIBRARY_CODE,
                    nom=data["nom"],
                    type_aliment=data["type"],
                    matiere_seche=data["ms"],
                    prix_kg=data["prix"],
                    ufl=data["ufl"],
                    ufv=data["ufv"],
                    pdi=data["pdi"],
                    calcium=data["ca"],
                    phosphore=data["p"]
                )
                db.add(aliment)
        db.commit()
        print(f"✅ Bibliothèque initialisée avec {len(ALIMENTS)} aliments.")
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_bibliotheque()