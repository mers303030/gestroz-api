# recreate_ressource_table.py
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Supprimer l'ancienne table
cursor.execute("DROP TABLE IF EXISTS ressources")

# Recréer avec la bonne structure
cursor.execute("""
    CREATE TABLE ressources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code_elevage TEXT NOT NULL,
        type_ressource TEXT NOT NULL,
        espece TEXT,
        effectif INTEGER,
        production TEXT,
        quantite_annuelle REAL,
        destination TEXT,
        type_revenu TEXT,
        description TEXT,
        montant_annuel REAL,
        periodicite TEXT,
        saisonnalite TEXT,
        observations TEXT
    )
""")

conn.commit()
conn.close()
print("✅ Table 'ressources' recréée.")