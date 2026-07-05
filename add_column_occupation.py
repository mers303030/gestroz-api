# add_column_occupation.py
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE personnes ADD COLUMN occupation TEXT;")
    conn.commit()
    print("✅ Colonne 'occupation' ajoutée à 'personnes'.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ La colonne 'occupation' existe déjà.")
    else:
        print(f"❌ Erreur : {e}")
finally:
    conn.close()