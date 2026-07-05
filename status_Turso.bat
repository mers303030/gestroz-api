# diagnostic.ps1
# Script de diagnostic pour le projet Gestroz
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTIC DU PROJET GESTROZ" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Structure du projet
Write-Host "[1] STRUCTURE DU PROJET" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Gray

$folders = @("api", "api/static", "data")
foreach ($f in $folders) {
    if (Test-Path $f) {
        Write-Host "✅ Dossier '$f' existe" -ForegroundColor Green
    } else {
        Write-Host "❌ Dossier '$f' manquant" -ForegroundColor Red
    }
}

$files = @("api/index.py", "api/static/interface.html", "requirements.txt", "vercel.json", ".gitignore")
foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "✅ Fichier '$f' existe" -ForegroundColor Green
    } else {
        Write-Host "❌ Fichier '$f' manquant" -ForegroundColor Red
    }
}
Write-Host ""

# 2. Fichier requirements.txt
Write-Host "[2] DEPENDANCES (requirements.txt)" -ForegroundColor Yellow
Write-Host "---------------------------------" -ForegroundColor Gray
if (Test-Path "requirements.txt") {
    $content = Get-Content "requirements.txt" -Raw
    Write-Host "Contenu :" -ForegroundColor White
    Write-Host $content -ForegroundColor Gray
    
    # Vérifier les dépendances clés
    $deps = @("fastapi", "uvicorn", "pyjwt", "mangum", "httpx", "libsql")
    foreach ($d in $deps) {
        if ($content -match $d) {
            Write-Host "✅ $d trouvé" -ForegroundColor Green
        } else {
            Write-Host "❌ $d non trouvé" -ForegroundColor Red
        }
    }
} else {
    Write-Host "❌ requirements.txt introuvable" -ForegroundColor Red
}
Write-Host ""

# 3. Fichier vercel.json
Write-Host "[3] VERIFICATION VERCEL" -ForegroundColor Yellow
Write-Host "----------------------" -ForegroundColor Gray
if (Test-Path "vercel.json") {
    try {
        $config = Get-Content "vercel.json" | ConvertFrom-Json
        Write-Host "✅ vercel.json valide" -ForegroundColor Green
        Write-Host "   builds: $($config.builds | ConvertTo-Json)" -ForegroundColor Gray
        Write-Host "   routes: $($config.routes | ConvertTo-Json)" -ForegroundColor Gray
    } catch {
        Write-Host "❌ vercel.json invalide (erreur JSON)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ vercel.json introuvable" -ForegroundColor Red
}
Write-Host ""

# 4. Base de données
Write-Host "[4] BASE DE DONNEES" -ForegroundColor Yellow
Write-Host "-------------------" -ForegroundColor Gray
if (Test-Path "data/zaer.db") {
    $size = (Get-Item "data/zaer.db").Length / 1MB
    Write-Host "✅ data/zaer.db existe ($([math]::Round($size, 2)) Mo)" -ForegroundColor Green
    
    try {
        $conn = New-Object System.Data.SQLite.SQLiteConnection("Data Source=data/zaer.db")
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT name FROM sqlite_master WHERE type='table';"
        $reader = $cmd.ExecuteReader()
        $tables = @()
        while ($reader.Read()) {
            $tables += $reader.GetString(0)
        }
        $conn.Close()
        Write-Host "   Tables : $($tables -join ', ')" -ForegroundColor Gray
        if ($tables -contains "eleveurs") {
            Write-Host "✅ Table 'eleveurs' présente" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Table 'eleveurs' non trouvée" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Impossible de lire la base (SQLite non installé?)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ data/zaer.db introuvable" -ForegroundColor Red
}
Write-Host ""

# 5. Git
Write-Host "[5] GIT" -ForegroundColor Yellow
Write-Host "------" -ForegroundColor Gray
if (Test-Path ".git") {
    Write-Host "✅ Dossier .git existe" -ForegroundColor Green
    try {
        $branch = git rev-parse --abbrev-ref HEAD
        Write-Host "   Branche : $branch" -ForegroundColor Gray
        $status = git status --porcelain
        if ($status) {
            Write-Host "⚠️ Fichiers modifiés non commités :" -ForegroundColor Yellow
            Write-Host $status -ForegroundColor Gray
        } else {
            Write-Host "✅ Aucun fichier modifié non commité" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ Git non trouvé dans PATH" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Dossier .git introuvable (dépôt non initialisé)" -ForegroundColor Red
}
Write-Host ""

# 6. Variables d'environnement (locales)
Write-Host "[6] VARIABLES D'ENVIRONNEMENT LOCALES" -ForegroundColor Yellow
Write-Host "--------------------------------------" -ForegroundColor Gray
$env_vars = @("TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN", "SECRET_KEY")
foreach ($v in $env_vars) {
    if ([Environment]::GetEnvironmentVariable($v)) {
        Write-Host "✅ $v = $([Environment]::GetEnvironmentVariable($v))" -ForegroundColor Green
    } else {
        Write-Host "❌ $v non définie" -ForegroundColor Red
    }
}
if (Test-Path ".env") {
    Write-Host "✅ Fichier .env existe" -ForegroundColor Green
} else {
    Write-Host "⚠️ Fichier .env introuvable" -ForegroundColor Yellow
}
Write-Host ""

# 7. Derniers logs locaux (si uvicon a tourné)
Write-Host "[7] LOGS LOCAUX" -ForegroundColor Yellow
Write-Host "--------------" -ForegroundColor Gray
if (Test-Path "logs") {
    $logFiles = Get-ChildItem "logs" -Filter "*.log" | Sort-Object LastWriteTime -Descending
    if ($logFiles.Count -gt 0) {
        Write-Host "✅ Dernier log : $($logFiles[0].Name)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Aucun fichier log trouvé" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Dossier 'logs' introuvable" -ForegroundColor Yellow
}
Write-Host ""

# 8. Turso (si identifiés)
Write-Host "[8] TURSO" -ForegroundColor Yellow
Write-Host "------" -ForegroundColor Gray
$turso_url = [Environment]::GetEnvironmentVariable("TURSO_DATABASE_URL")
$turso_token = [Environment]::GetEnvironmentVariable("TURSO_AUTH_TOKEN")
if ($turso_url -and $turso_token) {
    Write-Host "✅ URL Turso : $($turso_url.Substring(0, [Math]::Min(30, $turso_url.Length)))..." -ForegroundColor Green
    Write-Host "✅ Token : $($turso_token.Substring(0, [Math]::Min(15, $turso_token.Length)))..." -ForegroundColor Green
} else {
    Write-Host "⚠️ Identifiants Turso non trouvés en local" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTIC TERMINE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📌 Resume :" -ForegroundColor White
Write-Host "- Fichiers : verifier que tout est present" -ForegroundColor Gray
Write-Host "- Base : verifier que la table 'eleveurs' existe" -ForegroundColor Gray
Write-Host "- Env : verifier que TURSO_* sont definies" -ForegroundColor Gray
Write-Host "- Vercel : verifier que le dernier deploiement est en 'Ready'" -ForegroundColor Gray