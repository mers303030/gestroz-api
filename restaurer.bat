@echo off
chcp 65001 >nul
title Restauration GESTROZ

:: Vérifier que Git est installé
where git >nul 2>nul
if errorlevel 1 (
    echo ❌ Git introuvable. Installe Git depuis https://git-scm.com/
    pause
    exit /b 1
)

echo ⚠️  ATTENTION : Cette opération supprime TOUTES les modifications non sauvegardées.
echo    (fichiers créés, modifiés ou supprimés depuis la dernière sauvegarde)
echo.
choice /c ON /n /m "Confirmer la restauration (O/N) ? "

if errorlevel 2 (
    echo ❌ Annulation.
    pause
    exit /b 0
)

echo ⏪ Restauration en cours...
git restore .
git clean -fd

if errorlevel 0 (
    echo ✅ Restauration terminée. Projet revenu à l'état du dernier commit.
) else (
    echo ❌ Erreur lors de la restauration.
)

pause