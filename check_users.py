import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "data", "zaer.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT username, password, code_elevage FROM users;")
rows = cursor.fetchall()
conn.close()

if rows:
    print("=== Utilisateurs existants ===")
    for username, password_hash, code in rows:
        print(f"Nom: {username}, Hash: {password_hash}, Code élevage: {code}")
else:
    print("Aucun utilisateur trouvé.")