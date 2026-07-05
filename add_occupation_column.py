# add_occupation_column.py
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE parcelles ADD COLUMN occupation_actuelle TEXT;")
    conn.commit()
    print("✅ Colonne 'occupation_actuelle' ajoutée à la table 'parcelles'.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ La colonne 'occupation_actuelle' existe déjà.")
    else:
        print(f"❌ Erreur : {e}")
finally:
    conn.close()