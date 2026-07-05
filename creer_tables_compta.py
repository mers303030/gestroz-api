# creer_tables_compta.py
import sqlite3
import os
import shutil

DB_PATH = 'data/zaer.db'

# Sauvegarde
if os.path.exists(DB_PATH):
    shutil.copy(DB_PATH, 'data/zaer_backup_avant_compta.db')
    print("✅ Sauvegarde effectuée : data/zaer_backup_avant_compta.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS compta_produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_elevage TEXT,
    annee INTEGER,
    categorie TEXT,
    description TEXT,
    montant REAL
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS compta_charges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_elevage TEXT,
    annee INTEGER,
    categorie TEXT,
    description TEXT,
    montant REAL
)
''')

conn.commit()
conn.close()

print("✅ Tables 'compta_produits' et 'compta_charges' créées avec succès.")