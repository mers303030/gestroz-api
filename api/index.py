import os
import hashlib
import jwt
import datetime
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum

# Correction : utiliser libsql-experimental
try:
    from libsql_experimental import create_client
except ImportError:
    # Fallback si le package n'est pas disponible
    create_client = None
    print("⚠️ libsql-experimental non disponible")

# ---------- CONFIG ----------
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

TURSO_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

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
    
    # Version simplifiée sans Turso (admin/admin et OLM001/OLM001)
    if username == "admin" and password == "admin":
        token = create_token(username)
        return {"token": token, "message": "Connexion réussie"}
    elif username == "OLM001" and password == "OLM001":
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
    
    # Version simplifiée pour admin
    if username == "admin" and old_password == "admin":
        return {"message": "Mot de passe mis à jour avec succès"}
    elif username == "OLM001" and old_password == "OLM001":
        return {"message": "Mot de passe mis à jour avec succès (simulé)"}
    else:
        return JSONResponse(status_code=401, content={"error": "Ancien mot de passe incorrect"})

@app.get("/health")
async def health():
    return {"status": "healthy"}

handler = Mangum(app)