import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar, QMessageBox, QFileDialog, QInputDialog)
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

# Import des fenêtres
from ui.windows.ajout_eleveur import AjoutEleveurWindow
from ui.windows.gestion_eleveurs import GestionEleveursWindow
from ui.windows.ajout_animal import AjoutAnimalWindow
from ui.windows.gestion_animaux import GestionAnimauxWindow
from ui.windows.ajout_naissance import AjoutNaissanceWindow
from ui.windows.gestion_naissances import GestionNaissancesWindow
from ui.windows.ajout_sevrage import AjoutSevrageWindow
from ui.windows.gestion_sevrages import GestionSevragesWindow
from ui.windows.ajout_croissance import AjoutCroissanceWindow
from ui.windows.gestion_croissance import GestionCroissanceWindow
from ui.windows.ajout_mortalite import AjoutMortaliteWindow
from ui.windows.gestion_mortalites import GestionMortalitesWindow
from ui.windows.ajout_vente import AjoutVenteWindow
from ui.windows.gestion_ventes import GestionVentesWindow
from ui.windows.ajout_stock import AjoutStockWindow
from ui.windows.gestion_stocks import GestionStocksWindow
from ui.windows.gestion_utilisateurs import GestionUtilisateursWindow
from ui.windows.help_window import HelpWindow

# Contrôleurs d'import
from controllers.import_eleveur_controller import importer_eleveurs_depuis_excel
from controllers.import_animal_controller import importer_animaux_depuis_excel

class MainWindow(QMainWindow):
    def __init__(self, role, code_elevage):
        super().__init__()
        self.role = role
        self.code_elevage = code_elevage
        self.setWindowTitle("GESTROZ - Zaer")
        self.setGeometry(100, 100, 800, 600)

        # Widget central simple (pour éviter les problèmes de dessin)
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Bienvenue dans GESTROZ", alignment=Qt.AlignCenter))
        self.setCentralWidget(central)

        # Raccourci F1 pour l'aide
        QShortcut(QKeySequence("F1"), self).activated.connect(self.show_help)

        # Barre de menu
        menubar = self.menuBar()

        # ========== Menu Exploitation ==========
        menu_exp = menubar.addMenu("Exploitation")
        if role in ["admin", "technicien", "operateur"]:
            menu_exp.addAction("Ajouter un éleveur", self.open_ajout_eleveur)
            menu_exp.addAction("Ajouter un animal", self.open_ajout_animal)
        menu_exp.addAction("Gérer les éleveurs", self.open_gestion_eleveurs)
        menu_exp.addAction("Gérer les animaux", self.open_gestion_animaux)

        # ========== Menu Suivi technique ==========
        menu_suivi = menubar.addMenu("Suivi technique et sanitaire")
        if role in ["admin", "technicien", "operateur"]:
            menu_suivi.addAction("Naissances", self.open_naissance)
            menu_suivi.addAction("Sevrages", self.open_ajout_sevrage)
            menu_suivi.addAction("Croissance", self.open_ajout_croissance)
            menu_suivi.addAction("Mortalité", self.open_ajout_mortalite)
            menu_suivi.addAction("Ventes", self.open_ajout_vente)
        menu_suivi.addAction("Gérer les naissances", self.open_gestion_naissances)
        menu_suivi.addAction("Gérer les sevrages", self.open_gestion_sevrages)
        menu_suivi.addAction("Gérer les pesées", self.open_gestion_croissance)
        menu_suivi.addAction("Gérer les mortalités", self.open_gestion_mortalites)
        menu_suivi.addAction("Gérer les ventes", self.open_gestion_ventes)

        # ========== Menu Alimentation ==========
        menu_alim = menubar.addMenu("Alimentation")
        if role in ["admin", "technicien", "operateur"]:
            menu_alim.addAction("Ajouter un lot", self.open_ajout_stock)
        menu_alim.addAction("Gérer les stocks", self.open_gestion_stocks)

        # ========== Menu Administration ==========
        if role in ["admin", "technicien", "chef_general"]:
            menu_admin = menubar.addMenu("Administration")
            menu_admin.addAction("Dashboard", self.open_dashboard)
            menu_admin.addAction("Visites", self.open_visites)

        # ========== Menu Tools ==========
        menu_tools = menubar.addMenu("Tools")
        if role == "admin":
            menu_tools.addAction("Gestion des utilisateurs", self.open_gestion_utilisateurs)
        menu_tools.addAction("Import Excel", self.open_import)
        menu_tools.addAction("Export Excel", self.open_export)
        menu_tools.addSeparator()
        if role in ["admin", "technicien", "operateur"]:
            menu_tools.addAction("Sauvegarde", self.backup_db)
        menu_tools.addSeparator()
        menu_tools.addAction("Aide (F1)", self.show_help)
        menu_tools.addAction("À propos", self.show_about)
        menu_tools.addAction("Quitter", self.close)

    # --- Toutes les méthodes d'ouverture (définies) ---
    def open_ajout_eleveur(self):
        self.w = AjoutEleveurWindow()
        self.w.show()

    def open_gestion_eleveurs(self):
        self.w = GestionEleveursWindow(self.role, self.code_elevage)
        self.w.show()

    def open_ajout_animal(self):
        self.w = AjoutAnimalWindow()
        self.w.show()

    def open_gestion_animaux(self):
        self.w = GestionAnimauxWindow(self.role, self.code_elevage)
        self.w.show()

    def open_naissance(self):
        self.w = AjoutNaissanceWindow()
        self.w.show()

    def open_gestion_naissances(self):
        self.w = GestionNaissancesWindow(self.role, self.code_elevage)
        self.w.show()

    def open_ajout_sevrage(self):
        self.w = AjoutSevrageWindow()
        self.w.show()

    def open_gestion_sevrages(self):
        self.w = GestionSevragesWindow(self.role, self.code_elevage)
        self.w.show()

    def open_ajout_croissance(self):
        self.w = AjoutCroissanceWindow()
        self.w.show()

    def open_gestion_croissance(self):
        self.w = GestionCroissanceWindow(self.role, self.code_elevage)
        self.w.show()

    def open_ajout_mortalite(self):
        self.w = AjoutMortaliteWindow()
        self.w.show()

    def open_gestion_mortalites(self):
        self.w = GestionMortalitesWindow(self.role, self.code_elevage)
        self.w.show()

    def open_ajout_vente(self):
        self.w = AjoutVenteWindow()
        self.w.show()

    def open_gestion_ventes(self):
        self.w = GestionVentesWindow(self.role, self.code_elevage)
        self.w.show()

    def open_ajout_stock(self):
        self.w = AjoutStockWindow()
        self.w.show()

    def open_gestion_stocks(self):
        self.w = GestionStocksWindow(self.role, self.code_elevage)
        self.w.show()

    def open_gestion_utilisateurs(self):
        self.w = GestionUtilisateursWindow()
        self.w.show()

    def open_dashboard(self):
        QMessageBox.information(self, "Information", "Dashboard à venir")

    def open_visites(self):
        QMessageBox.information(self, "Information", "Visites à venir")

    # --- Import Excel ---
    def open_import(self):
        types = ["Éleveurs", "Animaux"]
        choix, ok = QInputDialog.getItem(self, "Type d'import", "Choisissez le type de données à importer :", types, 0, False)
        if not ok or not choix:
            return
        file_path, _ = QFileDialog.getOpenFileName(self, f"Importer {choix}", "", "Fichiers Excel (*.xlsx)")
        if not file_path:
            return
        try:
            if choix == "Éleveurs":
                nb, erreurs = importer_eleveurs_depuis_excel(file_path)
            else:
                nb, erreurs = importer_animaux_depuis_excel(file_path)
            if erreurs:
                msg = f"{nb} lignes importées.\n\nErreurs :\n" + "\n".join(erreurs[:15])
                QMessageBox.warning(self, "Import terminé avec avertissements", msg)
            else:
                QMessageBox.information(self, "Succès", f"{nb} {choix.lower()} importés.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    # --- Export Excel (informatif) ---
    def open_export(self):
        QMessageBox.information(self, "Export", "Utilisez le bouton 'Exporter Excel' dans chaque fenêtre de gestion.")

    # --- Sauvegarde de la base ---
    def backup_db(self):
        from database.db_session import DB_PATH
        import shutil, os
        from datetime import datetime
        backup_dir = os.path.join(os.path.dirname(DB_PATH), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"zaer_backup_{ts}.db")
        try:
            shutil.copy2(DB_PATH, backup_file)
            QMessageBox.information(self, "Succès", f"Sauvegarde créée : {backup_file}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    # --- Aide et à propos ---
    def show_help(self):
        self.help_win = HelpWindow(self)
        self.help_win.show()

    def show_about(self):
        QMessageBox.about(self, "À propos de GESTROZ",
                          "SmartÉlevage - GESTROZ\nVersion 1.0\n"
                          "Gestion des races bovines Oulmès-Zaïr\n"
                          "© 2026 Idriss MOUMEN - PCM Consulting\n"
                          "Email : moumen.idriss@gmail.com")