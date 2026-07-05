# test_insert.py
import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO ressources (code_elevage, type_ressource, espece, effectif, production, quantite_annuelle, destination)
    VALUES ('OLM001', 'Animaux', 'Ovins', 10, 'Lait', 500, 'Vente')
""")
conn.commit()
conn.close()
print("✅ Ressource de test insérée.")