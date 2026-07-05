@echo off
echo Installation des fichiers standardisés...
copy /Y ui\windows\saisie_consultation_ressources.py ui\windows\saisie_consultation_ressources.py
copy /Y ui\windows\saisie_consultation_vaccinations.py ui\windows\saisie_consultation_vaccinations.py
copy /Y ui\windows\saisie_consultation_traitements.py ui\windows\saisie_consultation_traitements.py
echo Suppression des anciens fichiers gestion_*...
del ui\windows\gestion_ressources.py 2>nul
del ui\windows\gestion_vaccinations.py 2>nul
del ui\windows\gestion_traitements.py 2>nul
echo Mise à jour des imports dans main_window.py...
powershell -Command "(Get-Content ui\main_window.py) -replace 'from ui\.windows\.gestion_ressources import GestionRessourcesWindow', 'from ui.windows.saisie_consultation_ressources import SaisieConsultationRessourcesWindow' | Set-Content ui\main_window.py"
powershell -Command "(Get-Content ui\main_window.py) -replace 'GestionRessourcesWindow', 'SaisieConsultationRessourcesWindow' | Set-Content ui\main_window.py"
powershell -Command "(Get-Content ui\main_window.py) -replace 'from ui\.windows\.gestion_vaccinations import GestionVaccinationsWindow', 'from ui.windows.saisie_consultation_vaccinations import SaisieConsultationVaccinationsWindow' | Set-Content ui\main_window.py"
powershell -Command "(Get-Content ui\main_window.py) -replace 'GestionVaccinationsWindow', 'SaisieConsultationVaccinationsWindow' | Set-Content ui\main_window.py"
powershell -Command "(Get-Content ui\main_window.py) -replace 'from ui\.windows\.gestion_traitements import GestionTraitementsWindow', 'from ui.windows.saisie_consultation_traitements import SaisieConsultationTraitementsWindow' | Set-Content ui\main_window.py"
powershell -Command "(Get-Content ui\main_window.py) -replace 'GestionTraitementsWindow', 'SaisieConsultationTraitementsWindow' | Set-Content ui\main_window.py"
echo Nettoyage des caches...
rmdir /s /q ui\__pycache__ 2>nul
rmdir /s /q ui\windows\__pycache__ 2>nul
rmdir /s /q __pycache__ 2>nul
echo Terminé. Lancez python main.py
pause