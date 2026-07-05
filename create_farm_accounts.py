import sqlite3
import os
import hashlib

# Chemin absolu correct
db_path = r"S:\python-project\zaer\data\zaer.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Récupérer tous les codes élevage existants
cursor.execute("SELECT code_elevage FROM eleveurs;")
eleveurs = cursor.fetchall()

created = 0
for (code,) in eleveurs:
    # Vérifier si l'utilisateur existe déjà
    cursor.execute("SELECT username FROM users WHERE username = ?", (code,))
    if cursor.fetchone():
        continue
    
    # Hash du mot de passe (identique au code)
    password_hash = hashlib.md5(code.encode()).hexdigest()
    
    cursor.execute(
        "INSERT INTO users (username, password, role, code_elevage) VALUES (?, ?, ?, ?)",
        (code, password_hash, "user", code)
    )
    created += 1

conn.commit()
conn.close()

print(f"✅ {created} comptes créés. Chaque login = mot de passe = code_elevage.")