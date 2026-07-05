import sys
import importlib
import traceback
from sqlalchemy.exc import InvalidRequestError, NoForeignKeysError

print("=" * 60)
print("DIAGNOSTIC COMPLET - GESTROZ")
print("=" * 60)

errors = []

# --------------------- ÉTAPE 1 : IMPORTS DES MODÈLES ---------------------
print("\n[1] Test d'import de tous les modèles...")
import os
models_dir = 'database/models'
for f in os.listdir(models_dir):
    if f.endswith('.py') and f not in ['__init__.py', 'main_window.py', 'migration_famille_ressources.py']:
        module = f[:-3]
        try:
            importlib.import_module(f'database.models.{module}')
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module} -> {e}")
            errors.append(f"Import {module}: {e}")

# --------------------- ÉTAPE 2 : INITIALISATION DES MAPPERS SQLALCHEMY ---------------------
print("\n[2] Test d'initialisation des mappers (relations)...")
try:
    from database.db_session import Base
    from sqlalchemy.orm import configure_mappers
    configure_mappers()
    print("  ✅ Tous les mappers sont cohérents.")
except InvalidRequestError as e:
    print(f"  ❌ Erreur de relation SQLAlchemy : {e}")
    errors.append(f"Mapper : {e}")
except Exception as e:
    print(f"  ❌ Autre erreur : {e}")
    errors.append(f"Mapper : {e}")

# --------------------- ÉTAPE 3 : CONNEXION À LA BASE ---------------------
print("\n[3] Test de connexion à la base de données...")
try:
    from database.db_session import SessionLocal
    db = SessionLocal()
    from database.models import Eleveur
    eleveurs = db.query(Eleveur).limit(1).all()
    db.close()
    print("  ✅ Base de données accessible.")
except Exception as e:
    print(f"  ❌ Erreur base de données : {e}")
    errors.append(f"DB : {e}")

# --------------------- ÉTAPE 4 : IMPORT DES FENÊTRES UI ---------------------
print("\n[4] Test d'import des fenêtres critiques...")
windows_to_test = [
    'saisie_consultation_eleveurs',
    'saisie_consultation_animaux',
    'saisie_consultation_stock',
    'rationnement',
    'saisie_consultation_naissances',
    'saisie_consultation_foncier',
    'saisie_consultation_famille',
]
for w in windows_to_test:
    try:
        importlib.import_module(f'ui.windows.{w}')
        print(f"  ✅ {w}")
    except Exception as e:
        print(f"  ❌ {w} -> {e}")
        errors.append(f"UI {w}: {e}")

# --------------------- ÉTAPE 5 : INSTANTIATION DES FENÊTRES (sans les afficher) ---------------------
print("\n[5] Test d'instanciation des fenêtres (sans les afficher)...")
try:
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    from ui.windows.saisie_consultation_eleveurs import SaisieConsultationEleveursWindow
    win = SaisieConsultationEleveursWindow()
    win.close()
    print("  ✅ SaisieConsultationEleveursWindow instanciée.")
except Exception as e:
    print(f"  ❌ SaisieConsultationEleveursWindow -> {e}")
    errors.append(f"Instanciation Eleveurs: {e}")

# --------------------- RÉSUMÉ ---------------------
print("\n" + "=" * 60)
if errors:
    print(f"⚠️  {len(errors)} erreur(s) détectée(s) :")
    for err in errors:
        print(f"  - {err}")
    print("\n👉 Pour corriger proprement, ouvre les fichiers indiqués dans les ❌.")
else:
    print("✅ TOUT EST PARFAIT. Lance `python main.py`.")

print("=" * 60)
input("\nAppuie sur Entrée pour fermer...")