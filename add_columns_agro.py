# add_columns_agro.py
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Ajouter les colonnes manquantes dans parcelles
try:
    cursor.execute("ALTER TABLE parcelles ADD COLUMN occupation_actuelle TEXT;")
    print("✅ Colonne 'occupation_actuelle' ajoutée à la table parcelles.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Colonne 'occupation_actuelle' existe déjà.")
    else:
        print(f"❌ Erreur : {e}")

# Ajouter les colonnes manquantes dans fiches_culturales
columns_fiches = [
    "labour_profondeur", "moyen_labour", "date_engrais_fond", "type_engrais_fond",
    "dose_engrais_fond", "date_engrais_couverture", "type_engrais_couverture",
    "dose_engrais_couverture", "date_phytosanitaire", "type_phytosanitaire",
    "dose_phytosanitaire", "type_recolte", "rendement_ensilage",
    "paturage_debut", "paturage_fin"
]
for col in columns_fiches:
    try:
        cursor.execute(f"ALTER TABLE fiches_culturales ADD COLUMN {col} TEXT;")
        print(f"✅ Colonne '{col}' ajoutée à fiches_culturales.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"ℹ️ Colonne '{col}' existe déjà.")
        else:
            print(f"❌ Erreur sur {col} : {e}")

# Ajouter les colonnes manquantes dans arbres
columns_arbres = ["parcelle_id", "destination", "rendement_kg_arbre", "quantite_vendue_kg", "prix_vente_kg"]
for col in columns_arbres:
    try:
        cursor.execute(f"ALTER TABLE arbres ADD COLUMN {col};")
        print(f"✅ Colonne '{col}' ajoutée à arbres.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"ℹ️ Colonne '{col}' existe déjà.")
        else:
            print(f"❌ Erreur sur {col} : {e}")

conn.commit()
conn.close()
print("\n✅ Mise à jour terminée.")