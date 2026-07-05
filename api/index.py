import os
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import libsql_experimental as libsql

app = FastAPI(title="Gestroz API", version="1.0.0")

# Configuration CORS pour l'interface statique
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration de la Base de Données Turso
TURSO_URL = os.environ.get("TURSO_DATABASE_URL")  # libsql://gestroz-db-...
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

def get_db_connection():
    """
    Crée une connexion hybride : Turso en production (Vercel) 
    ou SQLite local en fallback pour le développement.
    """
    if TURSO_URL and TURSO_TOKEN and not TURSO_URL.startswith("file:"):
        return libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
    else:
        os.makedirs("data", exist_ok=True)
        return libsql.connect(database="data/zaer.db")

# Schémas de données Pydantic
class LoginRequest(BaseModel):
    code_elevage: str
    mot_de_passe: str

class UpdatePasswordRequest(BaseModel):
    code_elevage: str
    current_password: str
    new_password: str

# ----------------------------------------------------------------
# MIDDLEWARE DE ROUTAGE (Anti-404 Vercel)
# ----------------------------------------------------------------
@app.middleware("http")
async def clean_vercel_routing_prefix(request: Request, call_next):
    """
    Vercel réécrit parfois les requêtes en ajoutant /api ou /api/index.py.
    Ce middleware nettoie le chemin à la volée pour que FastAPI s'y retrouve toujours.
    """
    path = request.url.path
    if path.startswith("/api/index.py"):
        request.scope["path"] = path.replace("/api/index.py", "")
    elif path.startswith("/api"):
        request.scope["path"] = path.replace("/api", "")
        
    # Sécurité supplémentaire : s'assurer qu'un chemin vide pointe bien sur la racine
    if not request.scope["path"]:
        request.scope["path"] = "/"
        
    return await call_next(request)

# ----------------------------------------------------------------
# ROUTES APPLICATIVES (Accessibles avec ou sans préfixe /api)
# ----------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Route de diagnostic pour valider la chaîne de connexion Turso"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM eleveurs;")
        count = cursor.fetchone()[0]
        conn.close()
        
        mode = "Turso Cloud" if (TURSO_URL and TURSO_TOKEN) else "Local SQLite"
        return {
            "status": "healthy",
            "database_mode": mode,
            "total_eleveurs": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Échec de connexion à la base de données : {str(e)}"
        )

@app.post("/login")
async def login(payload: LoginRequest):
    """Vérification des identifiants d'un éleveur"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT mot_de_passe FROM eleveurs WHERE code_elevage = ?;", 
            (payload.code_elevage,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] == payload.mot_de_passe:
            return {"success": True, "message": "Connexion approuvée"}
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Code élevage ou mot de passe incorrect"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-password")
async def update_password(payload: UpdatePasswordRequest):
    """Garantit la persistance des modifications de mots de passe sur Turso"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Validation de l'identité et du mot de passe actuel
        cursor.execute(
            "SELECT mot_de_passe FROM eleveurs WHERE code_elevage = ?;", 
            (payload.code_elevage,)
        )
        row = cursor.fetchone()
        
        if not row or row[0] != payload.current_password:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le mot de passe actuel est invalide"
            )
            
        # 2. Écriture persistante
        cursor.execute(
            "UPDATE eleveurs SET mot_de_passe = ? WHERE code_elevage = ?;",
            (payload.new_password, payload.code_elevage)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Mot de passe mis à jour avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))