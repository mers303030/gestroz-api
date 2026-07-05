import importlib
import sys

modules = [
    ("ui.windows.saisie_consultation_eleveurs", "SaisieConsultationEleveursWindow"),
    ("ui.windows.saisie_consultation_animaux", "SaisieConsultationAnimauxWindow"),
    ("ui.windows.saisie_consultation_stock", "SaisieConsultationStockWindow"),
    ("ui.windows.rationnement", "RationnementWindow"),
    ("ui.windows.saisie_consultation_naissances", "SaisieConsultationNaissancesWindow"),
    ("ui.windows.saisie_consultation_sevrages", "SaisieConsultationSevragesWindow"),
    ("ui.windows.saisie_consultation_croissance", "SaisieConsultationCroissanceWindow"),
    ("ui.windows.gestion_reproduction", "GestionReproductionWindow"),
    ("ui.windows.saisie_consultation_ventes", "SaisieConsultationVentesWindow"),
    ("ui.windows.saisie_consultation_mortalites", "SaisieConsultationMortalitesWindow"),
    ("ui.windows.saisie_consultation_vaccinations", "SaisieConsultationVaccinationsWindow"),
    ("ui.windows.saisie_consultation_traitements", "SaisieConsultationTraitementsWindow"),
    ("ui.windows.saisie_consultation_foncier", "SaisieConsultationFoncierWindow"),
    ("ui.windows.saisie_consultation_culturales", "SaisieConsultationCulturalesWindow"),
    ("ui.windows.saisie_consultation_arboriculture", "SaisieConsultationArboricultureWindow"),
    ("ui.windows.saisie_consultation_famille", "SaisieConsultationFamilleWindow"),
    ("ui.windows.gestion_economique", "GestionEconomiqueWindow"),
    ("ui.windows.analyse_effectif", "AnalyseEffectifWindow"),
    ("ui.windows.analyse_croissance", "AnalyseCroissanceWindow"),
    ("ui.windows.analyse_ventes", "AnalyseVentesWindow"),
    ("ui.windows.analyse_deces", "AnalyseDecesWindow"),
    ("ui.windows.gestion_bibliotheque_aliments", "GestionBibliothequeAlimentsWindow"),
    ("ui.windows.saisie_consultation_besoins", "SaisieConsultationBesoinWindow"),
    ("ui.windows.gestion_utilisateurs", "GestionUtilisateursWindow"),
    ("ui.windows.export_onssa_window", "ExportONSSAWindow"),
    ("ui.widgets.dashboard_tables", "DashboardTables"),
]

failed = []

for mod_name, class_name in modules:
    try:
        mod = importlib.import_module(mod_name)
        getattr(mod, class_name)
        print(f"✅ OK: {mod_name}.{class_name}")
    except Exception as e:
        print(f"❌ ERREUR: {mod_name}.{class_name} -> {e}")
        failed.append(f"{mod_name}.{class_name}: {e}")

print("\n" + "="*50)
if failed:
    print(f"⚠️  {len(failed)} module(s) en échec :")
    for f in failed:
        print(f"  - {f}")
else:
    print("🎉 Tous les modules sont importables !")