import random
import subprocess
import sys

# Vérifier si openpyxl est installé
try:
    from openpyxl import Workbook
except ImportError:
    print("📦 openpyxl manquant. Installation en cours...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    from openpyxl import Workbook

# Codes élevage (assurez-vous qu'ils existent dans votre base)
codes = ["OLM001", "OLM002", "OLM003", "AIT001", "AIT002", "BOK001", "BOK002"]
occupations = ["Orge", "Avoine", "Olivier", "Vesce", "Blé", "Jachère"]
statuts = ["Melk", "Location", "Offre provisoire", "Autre", ""]

wb = Workbook()
ws = wb.active
ws.title = "Parcelles"

# Entêtes
ws.append(["code_elevage", "numero_parcelle", "surface_ha", "statut_foncier", "occupation_actuelle", "observations"])

# Remplir
for code in codes:
    for i in range(1, 5):
        ws.append([
            code,
            f"Parcelle {chr(64+i)}",  # A, B, C, D
            round(random.uniform(1, 25), 1),
            random.choice(statuts),
            random.choice(occupations),
            ""
        ])

wb.save("parcelles_exemple.xlsx")
print("✅ Fichier 'parcelles_exemple.xlsx' généré avec 28 lignes.")