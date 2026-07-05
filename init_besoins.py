# init_besoins.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_session import SessionLocal
from database.models import BesoinNutritionnel

# ============================================================
# BESOINS NUTRITIONNELS POUR RACES RUSTIQUES (type Oulmès-Zaer)
# Poids vache adulte : 300-380 kg
# Production laitière max : 8-12 kg/j
# ============================================================

BESOINS = [
    # ==================== VACHES ====================
    {"race": "Oulmès-Zaer", "categorie": "Vache", "stade": "Tarissement",
     "poids_min": 300, "poids_max": 380, "prod_min": None, "prod_max": None,
     "ufl": 0.55, "ufv": 0.55, "pdi": 55, "calcium": 0.25, "phosphore": 0.18},

    {"race": "Oulmès-Zaer", "categorie": "Vache", "stade": "Lactation",
     "poids_min": 300, "poids_max": 350, "prod_min": 8, "prod_max": 10,
     "ufl": 0.75, "ufv": 0.75, "pdi": 85, "calcium": 0.40, "phosphore": 0.30},

    {"race": "Oulmès-Zaer", "categorie": "Vache", "stade": "Lactation",
     "poids_min": 320, "poids_max": 380, "prod_min": 6, "prod_max": 8,
     "ufl": 0.65, "ufv": 0.65, "pdi": 75, "calcium": 0.35, "phosphore": 0.25},

    {"race": "Oulmès-Zaer", "categorie": "Vache", "stade": "Lactation",
     "poids_min": 320, "poids_max": 380, "prod_min": 4, "prod_max": 6,
     "ufl": 0.55, "ufv": 0.55, "pdi": 65, "calcium": 0.30, "phosphore": 0.22},

    # ==================== GÉNISSES ====================
    {"race": "Oulmès-Zaer", "categorie": "Génisse", "stade": "Croissance",
     "poids_min": 150, "poids_max": 200, "prod_min": None, "prod_max": None,
     "ufl": 0.55, "ufv": 0.55, "pdi": 60, "calcium": 0.35, "phosphore": 0.25},

    {"race": "Oulmès-Zaer", "categorie": "Génisse", "stade": "Croissance",
     "poids_min": 200, "poids_max": 260, "prod_min": None, "prod_max": None,
     "ufl": 0.60, "ufv": 0.60, "pdi": 65, "calcium": 0.30, "phosphore": 0.22},

    {"race": "Oulmès-Zaer", "categorie": "Génisse", "stade": "Croissance",
     "poids_min": 260, "poids_max": 320, "prod_min": None, "prod_max": None,
     "ufl": 0.65, "ufv": 0.65, "pdi": 70, "calcium": 0.25, "phosphore": 0.20},

    {"race": "Oulmès-Zaer", "categorie": "Génisse", "stade": "Gestation",
     "poids_min": 280, "poids_max": 350, "prod_min": None, "prod_max": None,
     "ufl": 0.60, "ufv": 0.60, "pdi": 65, "calcium": 0.35, "phosphore": 0.25},

    # ==================== TAURILLONS ====================
    {"race": "Oulmès-Zaer", "categorie": "Taurillon", "stade": "Croissance",
     "poids_min": 150, "poids_max": 200, "prod_min": None, "prod_max": None,
     "ufl": 0.55, "ufv": 0.55, "pdi": 55, "calcium": 0.30, "phosphore": 0.20},

    {"race": "Oulmès-Zaer", "categorie": "Taurillon", "stade": "Croissance",
     "poids_min": 200, "poids_max": 280, "prod_min": None, "prod_max": None,
     "ufl": 0.60, "ufv": 0.60, "pdi": 60, "calcium": 0.25, "phosphore": 0.18},

    {"race": "Oulmès-Zaer", "categorie": "Taurillon", "stade": "Croissance",
     "poids_min": 280, "poids_max": 380, "prod_min": None, "prod_max": None,
     "ufl": 0.65, "ufv": 0.65, "pdi": 65, "calcium": 0.20, "phosphore": 0.15},

    # ==================== GÉNITEURS ====================
    {"race": "Oulmès-Zaer", "categorie": "Géniteur", "stade": "Indifférent",
     "poids_min": 350, "poids_max": 450, "prod_min": None, "prod_max": None,
     "ufl": 0.55, "ufv": 0.55, "pdi": 50, "calcium": 0.20, "phosphore": 0.15},

    # ==================== VEAUX / VELLES ====================
    {"race": "Oulmès-Zaer", "categorie": "Veau", "stade": "Croissance",
     "poids_min": 30, "poids_max": 100, "prod_min": None, "prod_max": None,
     "ufl": 0.50, "ufv": 0.50, "pdi": 50, "calcium": 0.40, "phosphore": 0.30},

    {"race": "Oulmès-Zaer", "categorie": "Veau", "stade": "Croissance",
     "poids_min": 100, "poids_max": 180, "prod_min": None, "prod_max": None,
     "ufl": 0.55, "ufv": 0.55, "pdi": 55, "calcium": 0.35, "phosphore": 0.25},

    {"race": "Oulmès-Zaer", "categorie": "Velle", "stade": "Croissance",
     "poids_min": 30, "poids_max": 100, "prod_min": None, "prod_max": None,
     "ufl": 0.50, "ufv": 0.50, "pdi": 50, "calcium": 0.40, "phosphore": 0.30},

    {"race": "Oulmès-Zaer", "categorie": "Velle", "stade": "Croissance",
     "poids_min": 100, "poids_max": 180, "prod_min": None, "prod_max": None,
     "ufl": 0.55, "ufv": 0.55, "pdi": 55, "calcium": 0.35, "phosphore": 0.25},
]

def init_besoins():
    db = SessionLocal()
    try:
        for data in BESOINS:
            existing = db.query(BesoinNutritionnel).filter(
                BesoinNutritionnel.race == data["race"],
                BesoinNutritionnel.categorie == data["categorie"],
                BesoinNutritionnel.stade == data["stade"],
                BesoinNutritionnel.poids_min == data["poids_min"],
                BesoinNutritionnel.poids_max == data["poids_max"]
            ).first()
            if not existing:
                besoin = BesoinNutritionnel(
                    race=data["race"],
                    categorie=data["categorie"],
                    stade=data["stade"],
                    poids_min=data["poids_min"],
                    poids_max=data["poids_max"],
                    production_min=data["prod_min"],
                    production_max=data["prod_max"],
                    ufl=data["ufl"],
                    ufv=data["ufv"],
                    pdi=data["pdi"],
                    calcium=data["calcium"],
                    phosphore=data["phosphore"],
                    observations="Initialisation bibliothèque besoins"
                )
                db.add(besoin)
        db.commit()
        print(f"✅ Bibliothèque des besoins initialisée avec {len(BESOINS)} enregistrements.")
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_besoins()