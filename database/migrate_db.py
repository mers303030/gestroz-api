# migrate_db.py
import sqlite3
import os
from database.db_session import DB_PATH

def get_table_columns(conn, table_name):
    """Récupère la liste des colonnes d'une table"""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}

def migrate():
    # Connexion directe à SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Ajout des colonnes manquantes dans la table 'animaux'
    required_columns_animaux = {
        'numero_boucle': 'TEXT',
        'date_naissance': 'TEXT',
        'sexe': 'TEXT',
        'race': 'TEXT',
        'origine': 'TEXT',
        'date_entree': 'TEXT',
        'code_elevage': 'TEXT',
        'categorie': 'TEXT',
        'poids_naissance': 'REAL',
        'mere_boucle': 'TEXT',
        'pere_boucle': 'TEXT',
        'type_velage': 'TEXT'
    }
    
    existing = get_table_columns(conn, 'animaux')
    for col, col_type in required_columns_animaux.items():
        if col not in existing:
            print(f"Ajout de la colonne '{col}' à la table 'animaux'...")
            try:
                cursor.execute(f"ALTER TABLE animaux ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError as e:
                print(f"  -> Erreur : {e}")
    
    # 2. Ajout des colonnes manquantes dans la table 'eleveurs'
    required_columns_eleveurs = {
        'nom': 'TEXT',
        'prenom': 'TEXT',
        'date_naissance': 'TEXT',
        'niveau_scolaire': 'TEXT',
        'cnie': 'TEXT',
        'telephone': 'TEXT',
        'commune': 'TEXT'
    }
    
    existing = get_table_columns(conn, 'eleveurs')
    for col, col_type in required_columns_eleveurs.items():
        if col not in existing:
            print(f"Ajout de la colonne '{col}' à la table 'eleveurs'...")
            try:
                cursor.execute(f"ALTER TABLE eleveurs ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError as e:
                print(f"  -> Erreur : {e}")
    
    conn.commit()
    conn.close()
    print("Migration terminée avec succès.")

if __name__ == "__main__":
    migrate()