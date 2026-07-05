import os
import sqlite3
import json
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI(title="Gestroz API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "api", "static")
DB_PATH = os.path.join(BASE_DIR, "data", "zaer.db")

# ---------- SERVEUR HTML ----------
@app.get("/")
@app.get("/interface.html")
async def serve_interface():
    html_path = os.path.join(STATIC_DIR, "interface.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return JSONResponse(status_code=404, content={"error": "interface.html not found"})

# ---------- LOGIN (GET pour afficher, POST pour authentifier) ----------
@app.get("/login")
async def login_get():
    # Affiche un message pour les requêtes GET
    return JSONResponse(content={"message": "Utilise POST avec username et password"})

@app.post("/login")
async def login_post(request: Request):
    try:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    except:
        return JSONResponse(status_code=400, content={"error": "JSON invalide"})
    
    # Exemple de validation (remplace par ta logique réelle)
    if username == "admin" and password == "admin":
        return {"token": "fake_jwt_token_12345", "message": "Connexion réussie"}
    else:
        return JSONResponse(status_code=401, content={"error": "Identifiants incorrects"})

# ---------- AUTRES ROUTES ----------
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# ---------- BASE DE DONNÉES ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- POUR VERCEL ----------
handler = Mangum(app)