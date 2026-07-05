@echo off
chcp 65001 >nul
title Création tables Comptabilité - GESTROZ
echo ================================================
echo   Création des tables de comptabilité (Produits/Charges)
echo ================================================
echo.

:: 1. Sauvegarde
echo [1] Sauvegarde de la base en cours...
if exist "data\zaer.db" (
    copy "data\zaer.db" "data\zaer_backup_avant_compta.db" >nul
    echo ✅ Sauvegarde effectuée : data\zaer_backup_avant_compta.db
) else (
    echo ⚠️  Aucune base trouvée. On continue quand même.
)
echo.

:: 2. Création des tables
echo [2] Création des tables...
python -c "import sqlite3; conn=sqlite3.connect('data/zaer.db'); cur=conn.cursor(); cur.execute('CREATE TABLE IF NOT EXISTS compta_produits (id INTEGER PRIMARY KEY AUTOINCREMENT, code_elevage TEXT, annee INTEGER, categorie TEXT, description TEXT, montant REAL)'); cur.execute('CREATE TABLE IF NOT EXISTS compta_charges (id INTEGER PRIMARY KEY AUTOINCREMENT, code_elevage TEXT, annee INTEGER, categorie TEXT, description TEXT, montant REAL)'); conn.commit(); conn.close(); print('✅ Tables créées avec succès.')"
if errorlevel 1 (
    echo ❌ Erreur lors de la création des tables.
    pause
    exit /b 1
)
echo.

:: 3. Vérification
echo [3] Vérification de la présence des tables...
python -c "import sqlite3; conn=sqlite3.connect('data/zaer.db'); cur=conn.cursor(); cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'compta_%'\"); rows=cur.fetchall(); print('Tables trouvées :'); [print(' - ' + row[0]) for row in rows]; conn.close()"
echo.

:: 4. Petit résumé
echo ================================================
echo ✅ Les tables sont prêtes.
echo.
echo Vous pouvez maintenant :
echo   - Ouvrir le menu Économie -> Coûts et marges
echo   - Ou utiliser une nouvelle fenêtre dédiée si vous le souhaitez.
echo.
echo Pour lancer l'application : python main.py
echo ================================================
pause