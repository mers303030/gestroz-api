import random
import sqlite3
from openpyxl import Workbook

# Récupérer tous les codes élevage de la base
conn = sqlite3.connect("data/zaer.db")
cursor = conn.cursor()
codes = [row[0] for row in cursor.execute("SELECT code_elevage FROM eleveurs").fetchall()]
conn.close()

if not codes:
    print("❌ Aucun code élevage trouvé.")
    exit()

print(f"📋 {len(codes)} codes élevage trouvés.")

# Données aléatoires
occupations = ["Orge", "Avoine", "Olivier", "Vesce", "Blé", "Jachère", "Luzerne", "Pomme de terre"]
statuts = ["Melk", "Location", "Offre provisoire", "Autre", ""]

# Création du fichier Excel
wb = Workbook()
ws = wb.active
ws.title = "Parcelles"

# Entêtes
ws.append(["code_elevage", "numero_parcelle", "surface_ha", "statut_foncier", "occupation_actuelle", "observations"])

total = 0
for code in codes:
    for i in range(1, 5):  # 4 parcelles par éleveur
        ws.append([
            code,
            f"{code}_P{i:02d}",
            round(random.uniform(0.5, 50), 1),
            random.choice(statuts),
            random.choice(occupations),
            ""
        ])
        total += 1

wb.save("test_1900_parcelles.xlsx")
print(f"✅ Fichier 'test_1900_parcelles.xlsx' généré avec {total} lignes.")