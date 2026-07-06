import os
import sqlite3
import libsql_experimental as libsql

# ==========================================
# CONFIGURATION (à remplacer par tes valeurs)
# ==========================================

TURSO_URL = "libsql://gestroz-db-mers303030.turso.io"
TURSO_TOKEN = "TON_TOKEN_TURSO"  # À récupérer depuis Settings → Tokens

# Chemin vers ta base SQLite locale
LOCAL_DB_PATH = "data/zaer.db"

# ==========================================
# MIGRATION
# ==========================================

def migrate_to_turso():
    """Migre les données de la base locale vers Turso"""
    try:
        # 1. Lire les données locales
        print(f"📂 Lecture de {LOCAL_DB_PATH}...")
        conn_local = sqlite3.connect(LOCAL_DB_PATH)
        cursor_local = conn_local.cursor()
        
        # Vérifie que la table existe
        cursor_local.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eleveurs'")
        if not cursor_local.fetchone():
            print("❌ Table 'eleveurs' non trouvée dans la base locale.")
            conn_local.close()
            return
        
        cursor_local.execute("SELECT code_elevage, mot_de_passe FROM eleveurs")
        data = cursor_local.fetchall()
        conn_local.close()
        
        if not data:
            print("⚠️ Aucune donnée à migrer.")
            return
        
        print(f"📊 {len(data)} éleveurs trouvés dans la base locale.")
        
        # 2. Connexion à Turso
        print("🔌 Connexion à Turso...")
        conn_turso = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        cursor_turso = conn_turso.cursor()
        
        # 3. Migration
        print("📤 Migration vers Turso...")
        for code, mdp in data:
            cursor_turso.execute(
                "INSERT OR REPLACE INTO eleveurs (code_elevage, mot_de_passe) VALUES (?, ?)",
                (code, mdp)
            )
            print(f"   ✅ {code} migré")
        
        conn_turso.commit()
        conn_turso.close()
        
        print(f"✅ Migration terminée : {len(data)} éleveurs transférés vers Turso.")
        
        # 4. Vérification
        print("🔍 Vérification...")
        conn_turso = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        cursor_turso = conn_turso.cursor()
        cursor_turso.execute("SELECT COUNT(*) FROM eleveurs")
        count = cursor_turso.fetchone()[0]
        conn_turso.close()
        
        print(f"📊 Turso contient maintenant {count} éleveurs.")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    migrate_to_turso()