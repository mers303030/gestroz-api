# insert_test_ressources_final.py
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

test_data = [
    ("OLM001", "Animaux", "Ovins", 15, "Lait", 600, "Vente", None, None, None, None, None),
    ("OLM001", "Animaux", "Caprins", 8, "Viande", 200, "Mixte", None, None, None, None, None),
    ("OLM001", "Animaux", "Volailles", 50, "Œufs", 1500, "Autoconsommation", None, None, None, None, None),
    ("OLM001", "Revenu extérieur", None, None, None, None, None, "Activité non agricole", "Menuisier", 12000, "Mensuel", "Toute l'année"),
    ("OLM001", "Revenu extérieur", None, None, None, None, None, "Pension", "Pension militaire", 6000, "Annuel", "Toute l'année"),
]

cursor.executemany("""
    INSERT INTO ressources (code_elevage, type_ressource, espece, effectif, production, quantite_annuelle, destination, type_revenu, description, montant_annuel, periodicite, saisonnalite)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", test_data)

conn.commit()
conn.close()
print("✅ Données de test insérées.")