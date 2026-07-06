import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# CONFIGURATION TURSO
# ==========================================

def get_turso_url():
    url = os.environ.get("TURSO_DATABASE_URL")
    if not url:
        return None
    return url.replace("libsql://", "https://")

def get_turso_token():
    return os.environ.get("TURSO_AUTH_TOKEN")

def execute_sql(sql, params=None):
    """Exécute une requête SQL sur Turso via HTTP API"""
    turso_url = get_turso_url()
    turso_token = get_turso_token()
    
    if not turso_url or not turso_token:
        raise Exception("Variables Turso non configurées")
    
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {"sql": sql}
            }
        ]
    }
    
    if params:
        args = []
        for p in params:
            if isinstance(p, int):
                args.append({"type": "integer", "value": str(p)})
            elif isinstance(p, float):
                args.append({"type": "float", "value": p})
            else:
                args.append({"type": "text", "value": str(p)})
        payload["requests"][0]["stmt"]["args"] = args
    
    headers = {
        "Authorization": f"Bearer {turso_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{turso_url}/v2/pipeline",
        headers=headers,
        json=payload,
        timeout=10
    )
    
    if response.status_code != 200:
        raise Exception(f"Erreur Turso: {response.status_code} - {response.text}")
    
    result = response.json()
    results = result.get("results", [])
    if not results:
        return None
    
    result_data = results[0].get("response", {}).get("result", {})
    rows = result_data.get("rows", [])
    
    # Conversion en tuples
    output_rows = []
    for row in rows:
        if isinstance(row, list) and len(row) > 0 and isinstance(row[0], dict):
            output_rows.append(tuple(col.get("value") for col in row))
        elif isinstance(row, list):
            output_rows.append(tuple(row))
        else:
            output_rows.append(tuple(row.values()))
    
    return {
        "rows": output_rows,
        "affected_count": result_data.get("affected_row_count", 0),
        "last_insert_id": result_data.get("last_insert_rowid")
    }

# ==========================================
# MODÈLES
# ==========================================

class LoginRequest(BaseModel):
    code_elevage: str
    mot_de_passe: str

class UpdatePasswordRequest(BaseModel):
    code_elevage: str
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str

class CreateUserRequest(BaseModel):
    code_elevage: str
    mot_de_passe: str

# ==========================================
# ROUTES
# ==========================================

@app.get("/")
async def serve_ui():
    """Sert l'interface HTML"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "interface.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return JSONResponse({"error": "interface.html not found"})

@app.get("/health")
async def health():
    """Vérifie la connexion à Turso"""
    try:
        result = execute_sql("SELECT COUNT(*) FROM eleveurs")
        count = result["rows"][0][0] if result and result["rows"] else 0
        return {
            "status": "healthy",
            "database": "Turso (HTTP API)",
            "total_eleveurs": count
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/api/login")
async def login(payload: LoginRequest):
    """Authentifie un éleveur"""
    try:
        result = execute_sql(
            "SELECT mot_de_passe FROM eleveurs WHERE code_elevage = ?",
            [payload.code_elevage]
        )
        
        if not result or not result["rows"]:
            raise HTTPException(401, "Code élevage inexistant")
        
        if result["rows"][0][0] != payload.mot_de_passe:
            raise HTTPException(401, "Mot de passe incorrect")
        
        return {"success": True, "message": "Bienvenue dans Gestroz"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/update-password")
async def update_password(payload: UpdatePasswordRequest):
    """Change le mot de passe"""
    try:
        # Vérifie l'ancien mot de passe
        result = execute_sql(
            "SELECT mot_de_passe FROM eleveurs WHERE code_elevage = ?",
            [payload.code_elevage]
        )
        
        if not result or not result["rows"]:
            raise HTTPException(404, "Éleveur non trouvé")
        
        if result["rows"][0][0] != payload.ancien_mot_de_passe:
            raise HTTPException(400, "Ancien mot de passe incorrect")
        
        # Met à jour
        execute_sql(
            "UPDATE eleveurs SET mot_de_passe = ? WHERE code_elevage = ?",
            [payload.nouveau_mot_de_passe, payload.code_elevage]
        )
        
        return {"success": True, "message": "Mot de passe modifié avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/admin/create-user")
async def create_user(payload: CreateUserRequest):
    """Crée un nouvel éleveur (admin)"""
    try:
        # Vérifie si l'utilisateur existe
        result = execute_sql(
            "SELECT code_elevage FROM eleveurs WHERE code_elevage = ?",
            [payload.code_elevage]
        )
        
        if result and result["rows"]:
            raise HTTPException(400, "Ce code existe déjà")
        
        execute_sql(
            "INSERT INTO eleveurs (code_elevage, mot_de_passe) VALUES (?, ?)",
            [payload.code_elevage, payload.mot_de_passe]
        )
        
        return {"success": True, "message": f"Éleveur {payload.code_elevage} créé"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/admin/users")
async def list_users():
    """Liste tous les éleveurs (admin)"""
    try:
        result = execute_sql("SELECT code_elevage FROM eleveurs ORDER BY code_elevage")
        users = [row[0] for row in result["rows"]] if result else []
        return {"users": users}
        
    except Exception as e:
        raise HTTPException(500, str(e))