# init_bibliotheque.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import SessionLocal
from database.models import BibliothequeAliment

ALIMENTS = [
    # === Pailles ===
    {"nom": "Paille d'orge", "type": "Fourrage", "ms": 88, "ufl": 0.30, "ufv": 0.30, "pdi": 35, "ca": 0.20, "p": 0.08},
    {"nom": "Paille de blé dur", "type": "Fourrage", "ms": 88, "ufl": 0.28, "ufv": 0.28, "pdi": 30, "ca": 0.25, "p": 0.07},
    {"nom": "Paille de blé tendre", "type": "Fourrage", "ms": 88, "ufl": 0.32, "ufv": 0.32, "pdi": 32, "ca": 0.22, "p": 0.09},
    # === Foins ===
    {"nom": "Foin de prairie naturelle", "type": "Fourrage", "ms": 85, "ufl": 0.45, "ufv": 0.45, "pdi": 55, "ca": 0.60, "p": 0.15},
    {"nom": "Foin de luzerne", "type": "Fourrage", "ms": 85, "ufl": 0.50, "ufv": 0.50, "pdi": 80, "ca": 1.00, "p": 0.20},
    {"nom": "Foin de graminées", "type": "Fourrage", "ms": 85, "ufl": 0.48, "ufv": 0.48, "pdi": 50, "ca": 0.40, "p": 0.18},
    # === Sous-produits ===
    {"nom": "Déchets de dattes", "type": "Sous-produit", "ms": 85, "ufl": 0.65, "ufv": 0.65, "pdi": 45, "ca": 0.15, "p": 0.10},
    {"nom": "Pulpe de tomate séchée", "type": "Sous-produit", "ms": 88, "ufl": 0.55, "ufv": 0.55, "pdi": 50, "ca": 0.40, "p": 0.25},
    {"nom": "Grignons d'olive", "type": "Sous-produit", "ms": 90, "ufl": 0.50, "ufv": 0.50, "pdi": 35, "ca": 0.30, "p": 0.15},
    {"nom": "Marc de raisin", "type": "Sous-produit", "ms": 85, "ufl": 0.40, "ufv": 0.40, "pdi": 30, "ca": 0.25, "p": 0.10},
    {"nom": "Son de blé", "type": "Sous-produit", "ms": 86, "ufl": 0.70, "ufv": 0.70, "pdi": 70, "ca": 0.10, "p": 0.70},
    {"nom": "Son d'orge", "type": "Sous-produit", "ms": 86, "ufl": 0.75, "ufv": 0.75, "pdi": 65, "ca": 0.12, "p": 0.60},
    # === Concentrés ===
    {"nom": "Orge", "type": "Concentré", "ms": 86, "ufl": 0.95, "ufv": 0.95, "pdi": 60, "ca": 0.08, "p": 0.30},
    {"nom": "Maïs grain", "type": "Concentré", "ms": 86, "ufl": 1.10, "ufv": 1.10, "pdi": 55, "ca": 0.03, "p": 0.25},
    {"nom": "Avoine", "type": "Concentré", "ms": 86, "ufl": 0.85, "ufv": 0.85, "pdi": 55, "ca": 0.10, "p": 0.30},
    {"nom": "Tourteau de soja", "type": "Concentré", "ms": 88, "ufl": 0.90, "ufv": 0.90, "pdi": 130, "ca": 0.30, "p": 0.60},
    {"nom": "Tourteau de colza", "type": "Concentré", "ms": 88, "ufl": 0.80, "ufv": 0.80, "pdi": 110, "ca": 0.70, "p": 0.90},
    {"nom": "Tourteau de tournesol", "type": "Concentré", "ms": 88, "ufl": 0.70, "ufv": 0.70, "pdi": 90, "ca": 0.40, "p": 0.80},
    {"nom": "Fève (grain)", "type": "Concentré", "ms": 86, "ufl": 0.85, "ufv": 0.85, "pdi": 100, "ca": 0.10, "p": 0.40},
    {"nom": "Pois protéagineux", "type": "Concentré", "ms": 86, "ufl": 0.80, "ufv": 0.80, "pdi": 105, "ca": 0.10, "p": 0.35},
    {"nom": "Mélasse", "type": "Concentré", "ms": 75, "ufl": 0.60, "ufv": 0.60, "pdi": 30, "ca": 0.10, "p": 0.05},
    {"nom": "Minéraux (CMV)", "type": "Minéral", "ms": 100, "ufl": 0, "ufv": 0, "pdi": 0, "ca": 15.0, "p": 5.0},
]

def init_bibliotheque():
    db = SessionLocal()
    try:
        for data in ALIMENTS:
            existing = db.query(BibliothequeAliment).filter(BibliothequeAliment.nom == data["nom"]).first()
            if not existing:
                aliment = BibliothequeAliment(
                    nom=data["nom"],
                    type_aliment=data["type"],
                    matiere_seche=data["ms"],
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