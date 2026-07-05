# check_imports.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

modules = [
    ("gestion_famille", "GestionFamilleWindow"),
    ("gestion_ressources", "GestionRessourcesWindow"),
    ("gestion_economique", "GestionEconomiqueWindow"),
]

for module_name, class_name in modules:
    try:
        import_name = f"ui.windows.{module_name}"
        mod = __import__(import_name, fromlist=[class_name])
        cls = getattr(mod, class_name)
        print(f"✅ {module_name} → {class_name} trouvé")
    except ImportError as e:
        print(f"❌ {module_name} → ImportError : {e}")
    except AttributeError as e:
        print(f"❌ {module_name} → AttributeError : la classe {class_name} n'existe pas dans le fichier")
    except Exception as e:
        print(f"❌ {module_name} → Erreur inattendue : {e}")