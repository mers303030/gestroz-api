import sqlite3
import os

db_path = r"S:\Python-Project\Zaer\data\zaer.db"

if not os.path.exists(db_path):
    print(f"❌ Base introuvable : {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Récupère toutes les tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("\n===== LISTE DES TABLES DANS ZAER.DB =====\n")
for table in tables:
    table_name = table[0]
    if table_name.startswith("sqlite_"):
        continue
    print(f"📁 TABLE : {table_name}")
    
    # Récupère le schéma
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        cid, name, ctype, notnull, dflt_value, pk = col
        pk_marker = "🔑" if pk else " "
        print(f"   {pk_marker} {name} ({ctype})")
    
    # Affiche un exemple des 3 premières lignes
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
    rows = cursor.fetchall()
    if rows:
        col_names = [description[0] for description in cursor.description]
        print(f"   → Exemple : {col_names}")
        for row in rows[:1]:
            print(f"     {row}")
    print("\n")

conn.close()
print("===== FIN DU DIAGNOSTIC =====")