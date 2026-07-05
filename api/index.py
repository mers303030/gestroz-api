import os
import hashlib
import jwt
import datetime
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum
from libsql_client import create_client

# ---------- CONFIG ----------
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

TURSO_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

if not TURSO_URL or not TURSO_TOKEN:
    raise Exception("Variables d'environnement TURSO manquantes")

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

# ---------- BASE TURSO ----------
async def get_db():
    return create_client(TURSO_URL, auth_token=TURSO_TOKEN)

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
    db = await get_db()
    
    # Créer la table eleveurs si elle n'existe pas
    await db.execute('''
        CREATE TABLE IF NOT EXISTS eleveurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_elevage TEXT UNIQUE NOT NULL,
            mot_de_passe_hash TEXT NOT NULL
        )
    ''')
    
    # Ajouter admin/admin par défaut
    admin_hash = hash_password("admin")
    result = await db.execute(
        "SELECT COUNT(*) FROM eleveurs WHERE code_elevage = 'admin'"
    )
    row = result.fetchone()
    if row[0] == 0:
        await db.execute(
            "INSERT INTO eleveurs (code_elevage, mot_de_passe_hash) VALUES (?, ?)",
            ("admin", admin_hash)
        )
    
    # Ajouter un exemple d'éleveur si la table est vide
    result = await db.execute("SELECT COUNT(*) FROM eleveurs")
    if result.fetchone()[0] == 1:  # seulement admin
        await db.execute(
            "INSERT INTO eleveurs (code_elevage, mot_de_passe_hash) VALUES (?, ?)",
            ("OLM001", hash_password("OLM001"))
        )
        await db.execute(
            "INSERT INTO eleveurs (code_elevage, mot_de_passe_hash) VALUES (?, ?)",
            ("OLM002", hash_password("OLM002"))
        )
    
    await db.close()
    print("✅ Base Turso prête")

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
    
    db = await get_db()
    result = await db.execute(
        "SELECT mot_de_passe_hash FROM eleveurs WHERE code_elevage = ?",
        (username,)
    )
    row = result.fetchone()
    await db.close()
    
    if row and row[0] == hash_password(password):
        token = create_token(username)
        return {"token": token, "message": "Connexion réussie"}
    else:
        return JSONResponse(status_code=401, content={"error": "Identifiants incorrects"})

@app.post("/change-password")
async def change_password(request: Request, username: str = Depends(verify_token)):
    try:
        body = await request.json()
        old_password = body.get("old_password")
        new_password = body.get("new_password")
    except:
        return JSONResponse(status_code=400, content={"error": "JSON invalide"})
    
    db = await get_db()
    
    # Vérifier l'ancien mot de passe
    result = await db.execute(
        "SELECT mot_de_passe_hash FROM eleveurs WHERE code_elevage = ?",
        (username,)
    )
    row = result.fetchone()
    
    if not row or row[0] != hash_password(old_password):
        await db.close()
        return JSONResponse(status_code=401, content={"error": "Ancien mot de passe incorrect"})
    
    # Mettre à jour le mot de passe
    new_hash = hash_password(new_password)
    await db.execute(
        "UPDATE eleveurs SET mot_de_passe_hash = ? WHERE code_elevage = ?",
        (new_hash, username)
    )
    await db.close()
    
    return {"message": "Mot de passe mis à jour avec succès"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ---------- VERCEL ----------
handler = Mangum(app)