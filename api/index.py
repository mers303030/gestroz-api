import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "zaer.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def serve_ui():
    path = os.path.join(os.path.dirname(__file__), "static", "interface.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "interface.html not found"}

@app.get("/health")
async def health():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM eleveurs").fetchone()[0]
    conn.close()
    return {"status": "healthy", "total_eleveurs": count}

@app.post("/api/login")
async def login(payload: dict):
    code = payload.get("code_elevage")
    mdp = payload.get("mot_de_passe")
    conn = get_db()
    row = conn.execute("SELECT mot_de_passe FROM eleveurs WHERE code_elevage = ?", (code,)).fetchone()
    conn.close()
    if row and row[0] == mdp:
        return {"success": True}
    raise HTTPException(status_code=401, detail="Identifiants incorrects")