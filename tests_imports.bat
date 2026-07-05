@echo off
chcp 65001 >nul
echo =================================================
echo TEST D'IMPORT DES MODULES GESTROZ
echo =================================================
echo.

set ERROR_COUNT=0

echo [1] Éleveurs...
python -c "from ui.windows.saisie_consultation_eleveurs import SaisieConsultationEleveursWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [2] Animaux...
python -c "from ui.windows.saisie_consultation_animaux import SaisieConsultationAnimauxWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [3] Stock...
python -c "from ui.windows.saisie_consultation_stock import SaisieConsultationStockWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [4] Rationnement...
python -c "from ui.windows.rationnement import RationnementWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [5] Naissances...
python -c "from ui.windows.saisie_consultation_naissances import SaisieConsultationNaissancesWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [6] Sevrages...
python -c "from ui.windows.saisie_consultation_sevrages import SaisieConsultationSevragesWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [7] Croissance (pesées)...
python -c "from ui.windows.saisie_consultation_croissance import SaisieConsultationCroissanceWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [8] Reproduction...
python -c "from ui.windows.gestion_reproduction import GestionReproductionWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [9] Ventes...
python -c "from ui.windows.saisie_consultation_ventes import SaisieConsultationVentesWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [10] Mortalités...
python -c "from ui.windows.saisie_consultation_mortalites import SaisieConsultationMortalitesWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [11] Vaccinations...
python -c "from ui.windows.saisie_consultation_vaccinations import SaisieConsultationVaccinationsWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [12] Traitements (curatifs)...
python -c "from ui.windows.saisie_consultation_traitements import SaisieConsultationTraitementsWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [13] Capital foncier...
python -c "from ui.windows.saisie_consultation_foncier import SaisieConsultationFoncierWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [14] Pratiques culturales...
python -c "from ui.windows.saisie_consultation_culturales import SaisieConsultationCulturalesWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [15] Arboriculture...
python -c "from ui.windows.saisie_consultation_arboriculture import SaisieConsultationArboricultureWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [16] Famille...
python -c "from ui.windows.saisie_consultation_famille import SaisieConsultationFamilleWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [17] Économie...
python -c "from ui.windows.gestion_economique import GestionEconomiqueWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [18] Analyses - Effectif...
python -c "from ui.windows.analyse_effectif import AnalyseEffectifWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [19] Analyses - Croissance...
python -c "from ui.windows.analyse_croissance import AnalyseCroissanceWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [20] Analyses - Ventes...
python -c "from ui.windows.analyse_ventes import AnalyseVentesWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [21] Analyses - Décès...
python -c "from ui.windows.analyse_deces import AnalyseDecesWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [22] Bibliothèque - Aliments...
python -c "from ui.windows.gestion_bibliotheque_aliments import GestionBibliothequeAlimentsWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [23] Bibliothèque - Besoins nutritionnels...
python -c "from ui.windows.saisie_consultation_besoins import SaisieConsultationBesoinWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [24] Gestion utilisateurs...
python -c "from ui.windows.gestion_utilisateurs import GestionUtilisateursWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [25] Export ONSSA...
python -c "from ui.windows.export_onssa_window import ExportONSSAWindow; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo [26] Dashboard...
python -c "from ui.widgets.dashboard_tables import DashboardTables; print('OK')" 2>nul
if %errorlevel% neq 0 ( echo ERREUR & set /a ERROR_COUNT+=1 ) else echo OK
echo.

echo.
echo =================================================
echo RÉSUMÉ : %ERROR_COUNT% module(s) en erreur.
echo =================================================
pause