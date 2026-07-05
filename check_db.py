import sqlite3
import os

db_path = "data/zaer.db"

if not os.path.exists(db_path):
    print("❌ data/zaer.db introuvable")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📋 Tables existantes :", [t[0] for t in tables])

if "elevages" in [t[0] for t in tables]:
    cursor.execute("SELECT * FROM elevages;")
    rows = cursor.fetchall()
    if rows:
        print("✅ Table elevages :")
        for row in rows:
            print(row)
    else:
        print("⚠️ Table elevages est vide")
else:
    print("❌ Table elevages n'existe pas encore")

conn.close()