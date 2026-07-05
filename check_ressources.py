# check_ressources.py
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Vérifier si la table existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ressources'")
if cursor.fetchone() is None:
    print("❌ La table 'ressources' n'existe pas.")
else:
    # Compter les lignes
    cursor.execute("SELECT COUNT(*) FROM ressources")
    count = cursor.fetchone()[0]
    print(f"📊 La table 'ressources' contient {count} ligne(s).")
    
    # Afficher les données
    cursor.execute("SELECT * FROM ressources")
    rows = cursor.fetchall()
    for r in rows:
        print(r)

conn.close()