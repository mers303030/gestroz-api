import os
import hashlib
import jwt
import datetime
import httpx
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum

# ---------- CONFIG ----------
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

TURSO_HTTP_URL = os.environ.get("TURSO_HTTP_URL")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

if not TURSO_HTTP_URL:
    raise Exception("Variable TURSO_HTTP_URL manquante")
if not TURSO_TOKEN:
    raise Exception("Variable TURSO_AUTH_TOKEN manquante")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "api", "static")

# ---------- APP ----------
app = FastAPI(title="Gestroz API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ---------- TURSO VIA HTTPX ----------
async def turso_query(sql: str, params: list = []):
    """Exécute une requête SQL sur Turso via l'API HTTP."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TURSO_HTTP_URL}/v1/query",
            json={"statements": [{"sql": sql, "args": params}]},
            headers={"Authorization": f"Bearer {TURSO_TOKEN}"},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

# ---------- HASH ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- JWT ----------
def create_token(username: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

# ---------- INIT ----------
@app.on_event("startup")
async def startup():
    try:
        await turso_query("""
            CREATE TABLE IF NOT EXISTS eleveurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_elevage TEXT UNIQUE NOT NULL,
                mot_de_passe_hash TEXT NOT NULL
            )
        """)
        print("✅ Table 'eleveurs' vérifiée")
        
        result = await turso_query(
            "SELECT COUNT(*) FROM eleveurs WHERE code_elevage = ?",
            ["admin"]
        )
        count = result["results"][0]["rows"][0][0]
        if count == 0:
            admin_hash = hash_password("admin")
            await turso_query(
                "INSERT INTO eleveurs (code_elevage, mot_de_passe_hash) VALUES (?, ?)",
                ["admin", admin_hash]
            )
            print("✅ Compte 'admin' créé")
    except Exception as e:
        print(f"⚠️ Erreur startup : {e}")

# ---------- ROUTES ----------
@app.get("/")
@app.get("/interface.html")
async def serve_interface():
    html_path = os.path.join(STATIC_DIR, "interface.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return JSONResponse(status_code=404, content={"error": "interface.html not found"})

@app.post("/login")
async def login_post(request: Request):
    try:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    except:
        return JSONResponse(status_code=400, content={"error": "JSON invalide"})
    
    try:
        result = await turso_query(
            "SELECT mot_de_passe_hash FROM eleveurs WHERE code_elevage = ?",
            [username]
        )
        rows = result["results"][0]["rows"]
        
        if rows and rows[0][0] == hash_password(password):
            token = create_token(username)
            return {"token": token, "message": "Connexion réussie"}
        else:
            return JSONResponse(status_code=401, content={"error": "Identifiants incorrects"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur base de données: {str(e)}"})

@app.post("/change-password")
async def change_password(request: Request, username: str = Depends(verify_token)):
    try:
        body = await request.json()
        old_password = body.get("old_password")
        new_password = body.get("new_password")
    except:
        return JSONResponse(status_code=400, content={"error": "JSON invalide"})
    
    try:
        result = await turso_query(
            "SELECT mot_de_passe_hash FROM eleveurs WHERE code_elevage = ?",
            [username]
        )
        rows = result["results"][0]["rows"]
        
        if not rows or rows[0][0] != hash_password(old_password):
            return JSONResponse(status_code=401, content={"error": "Ancien mot de passe incorrect"})
        
        new_hash = hash_password(new_password)
        await turso_query(
            "UPDATE eleveurs SET mot_de_passe_hash = ? WHERE code_elevage = ?",
            [new_hash, username]
        )
        return {"message": "Mot de passe mis à jour avec succès"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur base de données: {str(e)}"})

@app.get("/health")
async def health():
    try:
        await turso_query("SELECT 1")
        return {"status": "healthy", "turso": "connected"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "unhealthy", "turso": "disconnected", "error": str(e)})

handler = Mangum(app)