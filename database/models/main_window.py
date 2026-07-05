# ui/windows/main_window.py
import sys
from PySide6.QtWidgets import (QMainWindow, QMenuBar, QMenu, QStatusBar,
                               QMessageBox, QApplication)
from PySide6.QtCore import Qt

# Import des fenêtres existantes
from ui.windows.saisie_consultation_eleveurs import SaisieConsultationEleveursWindow
from ui.windows.saisie_consultation_animaux import SaisieConsultationAnimauxWindow
from ui.windows.saisie_consultation_naissances import SaisieConsultationNaissancesWindow
from ui.windows.saisie_consultation_sevrages import SaisieConsultationSevragesWindow
from ui.windows.saisie_consultation_croissance import SaisieConsultationCroissanceWindow
from ui.windows.gestion_reproduction import GestionReproductionWindow
from ui.windows.saisie_consultation_mortalites import SaisieConsultationMortalitesWindow
from ui.windows.saisie_consultation_ventes import SaisieConsultationVentesWindow


class MainWindow(QMainWindow):
    def __init__(self, user_role=None, user_code=None, parent=None):
        super().__init__(parent)
        self.user_role = user_role
        self.user_code = user_code
        self.setWindowTitle(f"GESTROZ - Zaer ({self.user_code})" if self.user_code else "GESTROZ - Zaer")
        self.resize(1200, 800)
        self.statusBar().showMessage("Prêt")
        self.create_menu()
        self.windows = {}

    def create_menu(self):
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        exit_action = file_menu.addAction("Quitter")
        exit_action.triggered.connect(self.close)

        # Menu Élevage
        eleveur_menu = menubar.addMenu("Élevage")
        eleveur_menu.addAction("Éleveurs").triggered.connect(self.open_eleveurs)
        eleveur_menu.addAction("Animaux").triggered.connect(self.open_animaux)

        # Menu Naissances
        naissance_menu = menubar.addMenu("Naissances")
        naissance_menu.addAction("Saisie et consultation des naissances").triggered.connect(self.open_naissances)

        # Menu Croissance
        croissance_menu = menubar.addMenu("Croissance")
        croissance_menu.addAction("Sevrages").triggered.connect(self.open_sevrages)
        croissance_menu.addAction("Pesées de croissance").triggered.connect(self.open_croissance)

        # Menu Reproduction
        reproduction_menu = menubar.addMenu("Reproduction")
        reproduction_menu.addAction("Gestion de la reproduction").triggered.connect(self.open_reproduction)

        # Menu Gestion du troupeau
        gestion_menu = menubar.addMenu("Gestion du troupeau")
        gestion_menu.addAction("Mortalités").triggered.connect(self.open_mortalites)
        gestion_menu.addAction("Ventes").triggered.connect(self.open_ventes)

        # Menu Aide
        aide_menu = menubar.addMenu("Aide")
        aide_menu.addAction("À propos").triggered.connect(self.show_about)

    # ========== MÉTHODES D'OUVERTURE ==========
    def open_eleveurs(self):
        self.windows['eleveurs'] = SaisieConsultationEleveursWindow(self)
        self.windows['eleveurs'].show()

    def open_animaux(self):
        self.windows['animaux'] = SaisieConsultationAnimauxWindow(self)
        self.windows['animaux'].show()

    def open_naissances(self):
        self.windows['naissances'] = SaisieConsultationNaissancesWindow(self)
        self.windows['naissances'].show()

    def open_sevrages(self):
        self.windows['sevrages'] = SaisieConsultationSevragesWindow(self)
        self.windows['sevrages'].show()

    def open_croissance(self):
        self.windows['croissance'] = SaisieConsultationCroissanceWindow(self)
        self.windows['croissance'].show()

    def open_reproduction(self):
        self.windows['reproduction'] = GestionReproductionWindow(self)
        self.windows['reproduction'].show()

    def open_mortalites(self):
        self.windows['mortalites'] = SaisieConsultationMortalitesWindow(self)
        self.windows['mortalites'].show()

    def open_ventes(self):
        self.windows['ventes'] = SaisieConsultationVentesWindow(self)
        self.windows['ventes'].show()

    def show_about(self):
        QMessageBox.about(self, "À propos", "GESTROZ - Zaer\nApplication de gestion d'élevage bovin.\nVersion 1.0")

    def closeEvent(self, event):
        for win in self.windows.values():
            if win is not None:
                try:
                    win.close()
                except:
                    pass
        event.accept()