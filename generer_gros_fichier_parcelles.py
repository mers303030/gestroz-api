import random
import sqlite3
from openpyxl import Workbook

# Se connecter à la base pour récupérer tous les codes élevage
conn = sqlite3.connect("data/zaer.db")
cursor = conn.cursor()

codes = [row[0] for row in cursor.execute("SELECT code_elevage FROM eleveurs").fetchall()]
conn.close()

if not codes:
    print("❌ Aucun code élevage trouvé dans la base.")
    exit()

print(f"📋 {len(codes)} codes élevage trouvés.")

# Paramètres de génération
occupations = ["Orge", "Avoine", "Olivier", "Vesce", "Blé", "Jachère", "Luzerne", "Pomme de terre"]
statuts = ["Melk", "Location", "Offre provisoire", "Autre", ""]

wb = Workbook()
ws = wb.active
ws.title = "Parcelles"

# Entêtes
ws.append(["code_elevage", "numero_parcelle", "surface_ha", "statut_foncier", "occupation_actuelle", "observations"])

total_lignes = 0
for code in codes:
    # Chaque élevage aura entre 5 et 20 parcelles
    nb_parcelles = random.randint(5, 20)
    for i in range(1, nb_parcelles + 1):
        ws.append([
            code,
            f"Parcelle {i:03d}",
            round(random.uniform(0.5, 50), 1),
            random.choice(statuts),
            random.choice(occupations),
            ""
        ])
    total_lignes += nb_parcelles

wb.save("gros_test_parcelles.xlsx")
print(f"✅ Fichier 'gros_test_parcelles.xlsx' généré avec {total_lignes} lignes.")