import os
import libsql_experimental as libsql

# ==========================================
# CONFIGURATION (à remplacer par tes valeurs)
# ==========================================

TURSO_URL = "libsql://gestroz-db-mers303030.turso.io"
TURSO_TOKEN = "TON_TOKEN_TURSO"  # À récupérer depuis Settings → Tokens

# ==========================================
# INITIALISATION
# ==========================================

def init_database():
    """Crée la table eleveurs et ajoute un utilisateur test"""
    try:
        print("🔌 Connexion à Turso...")
        conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        # Créer la table
        print("📋 Création de la table eleveurs...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eleveurs (
                code_elevage TEXT PRIMARY KEY,
                mot_de_passe TEXT NOT NULL
            )
        """)
        
        # Ajouter un utilisateur test
        print("👤 Ajout de l'utilisateur test...")
        cursor.execute(
            "INSERT OR IGNORE INTO eleveurs (code_elevage, mot_de_passe) VALUES (?, ?)",
            ("test123", "password")
        )
        
        conn.commit()
        conn.close()
        
        print("✅ Base de données initialisée avec succès !")
        
        # Vérification
        conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        cursor.execute("SELECT code_elevage, mot_de_passe FROM eleveurs")
        rows = cursor.fetchall()
        conn.close()
        
        print(f"📊 {len(rows)} éleveurs dans la base :")
        for row in rows:
            print(f"   - {row[0]} : {row[1]}")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("Vérifie que TURSO_URL et TURSO_TOKEN sont corrects.")

if __name__ == "__main__":
    init_database()