@echo off
chcp 65001 >nul
title Sauvegarde GESTROZ

:: Vérifier que Git est installé
where git >nul 2>nul
if errorlevel 1 (
    echo ❌ Git introuvable. Installe Git depuis https://git-scm.com/
    pause
    exit /b 1
)

:: Définir l'identité Git si elle n'existe pas
git config user.name >nul 2>nul
if errorlevel 1 (
    echo ⚙️  Configuration automatique de l'identité Git...
    git config user.name "MOUMEN"
    git config user.email "moumen@exemple.com"
)

echo 📸 Sauvegarde en cours...
git add .
git commit -m "Sauvegarde - %date% %time%"

if errorlevel 0 (
    echo ✅ Sauvegarde réussie.
) else (
    echo ⚠️  Aucune modification à sauvegarder.
)

pause