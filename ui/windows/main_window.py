# ui/windows/main_window.py
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar,
    QMessageBox, QFileDialog, QInputDialog, QDialog, QPushButton
)
from PySide6.QtGui import (
    QShortcut, QKeySequence, QPixmap, QPainter, QFont,
    QColor, QPen
)
from PySide6.QtCore import Qt, QRect, QTimer

# === IMPORTS DES FENÊTRES EXISTANTES (protégés) ===
try:
    from ui.windows.saisie_consultation_eleveurs import SaisieConsultationEleveursWindow
except ImportError:
    SaisieConsultationEleveursWindow = None

try:
    from ui.windows.saisie_consultation_animaux import SaisieConsultationAnimauxWindow
except ImportError:
    SaisieConsultationAnimauxWindow = None

try:
    from ui.windows.saisie_consultation_naissances import SaisieConsultationNaissancesWindow
except ImportError:
    SaisieConsultationNaissancesWindow = None

try:
    from ui.windows.saisie_consultation_sevrages import SaisieConsultationSevragesWindow
except ImportError:
    SaisieConsultationSevragesWindow = None

try:
    from ui.windows.saisie_consultation_croissance import SaisieConsultationCroissanceWindow
except ImportError:
    SaisieConsultationCroissanceWindow = None

try:
    from ui.windows.saisie_consultation_ventes import SaisieConsultationVentesWindow
except ImportError:
    SaisieConsultationVentesWindow = None

try:
    from ui.windows.saisie_consultation_mortalites import SaisieConsultationMortalitesWindow
except ImportError:
    SaisieConsultationMortalitesWindow = None

try:
    from ui.windows.gestion_reproduction import GestionReproductionWindow
except ImportError:
    GestionReproductionWindow = None

# === NOUVEAUX MODULES AGRONOMIE ===
try:
    from ui.windows.saisie_consultation_foncier import SaisieConsultationFoncierWindow
except ImportError:
    SaisieConsultationFoncierWindow = None

try:
    from ui.windows.saisie_consultation_culturales import SaisieConsultationCulturalesWindow
except ImportError:
    SaisieConsultationCulturalesWindow = None

try:
    from ui.windows.saisie_consultation_arboriculture import SaisieConsultationArboricultureWindow
except ImportError:
    SaisieConsultationArboricultureWindow = None

# === MODULES ALIMENTATION ===
try:
    from ui.windows.saisie_consultation_stock import SaisieConsultationStockWindow
except ImportError:
    SaisieConsultationStockWindow = None

try:
    from ui.windows.rationnement import RationnementWindow
except ImportError:
    RationnementWindow = None

# === BIBLIOTHÈQUES ===
try:
    from ui.windows.gestion_bibliotheque_aliments import GestionBibliothequeAlimentsWindow
except ImportError:
    GestionBibliothequeAlimentsWindow = None

try:
    from ui.windows.saisie_consultation_besoins import SaisieConsultationBesoinWindow
except ImportError:
    SaisieConsultationBesoinWindow = None

# === NOUVEAU MODULE FAMILLE ===
try:
    from ui.windows.saisie_consultation_famille import SaisieConsultationFamilleWindow
except ImportError:
    SaisieConsultationFamilleWindow = None

# === AUTRES FENÊTRES (OPTIONNELLES) ===
try:
    from ui.windows.gestion_parcelles import GestionParcellesWindow
except ImportError:
    GestionParcellesWindow = None

try:
    from ui.windows.gestion_famille import GestionFamilleWindow
except ImportError:
    GestionFamilleWindow = None

try:
    from ui.windows.gestion_ressources import GestionRessourcesWindow
except ImportError:
    GestionRessourcesWindow = None

try:
    from ui.windows.gestion_economique import GestionEconomiqueWindow
except ImportError:
    GestionEconomiqueWindow = None

try:
    from ui.windows.gestion_vaccinations import GestionVaccinationsWindow
except ImportError:
    GestionVaccinationsWindow = None

try:
    from ui.windows.gestion_traitements import GestionTraitementsWindow
except ImportError:
    GestionTraitementsWindow = None

try:
    from ui.windows.gestion_arboriculture import GestionArboricultureWindow
except ImportError:
    GestionArboricultureWindow = None

try:
    from ui.windows.ajout_stock import AjoutStockWindow
except ImportError:
    AjoutStockWindow = None

try:
    from ui.windows.gestion_stocks import GestionStocksWindow
except ImportError:
    GestionStocksWindow = None

try:
    from ui.windows.gestion_utilisateurs import GestionUtilisateursWindow
except ImportError:
    GestionUtilisateursWindow = None

try:
    from ui.windows.help_window import HelpWindow
except ImportError:
    HelpWindow = None

try:
    from ui.windows.export_onssa_window import ExportONSSAWindow
except ImportError:
    ExportONSSAWindow = None

try:
    from ui.windows.analyse_effectif import AnalyseEffectifWindow
except ImportError:
    AnalyseEffectifWindow = None

try:
    from ui.windows.analyse_croissance import AnalyseCroissanceWindow
except ImportError:
    AnalyseCroissanceWindow = None

try:
    from ui.windows.analyse_ventes import AnalyseVentesWindow
except ImportError:
    AnalyseVentesWindow = None

try:
    from ui.windows.analyse_deces import AnalyseDecesWindow
except ImportError:
    AnalyseDecesWindow = None

try:
    from ui.widgets.dashboard_tables import DashboardTables
except ImportError:
    DashboardTables = None

try:
    from controllers.import_eleveur_controller import importer_eleveurs_depuis_excel
except ImportError:
    importer_eleveurs_depuis_excel = None

try:
    from controllers.import_animal_controller import importer_animaux_depuis_excel
except ImportError:
    importer_animaux_depuis_excel = None


MESSAGE = (
    "La Fédération Marocaine des Éleveurs Bovins de la Race Oulmès-Zaër souhaite la bienvenue "
    "à tous les éleveurs, techniciens et responsables qui, par leur dévouement quotidien, veillent "
    "à préserver ce joyau de notre patrimoine national. Ensemble, gardons vivante cette race fière, "
    "attachée à nos terres et à notre histoire. GESTROZ a été conçu pour vous accompagner dans cette "
    "noble mission, avec rigueur et proximité. Merci pour votre confiance et votre engagement.\n\n"
    "Conçu et réalisé par MOUMEN Idriss."
)


class BackgroundWidget(QWidget):
    """Widget central : photo de fond en diaporama + message de bienvenue."""

    def __init__(self, parent=None):
        super().__init__(parent)
        here = os.path.dirname(os.path.abspath(__file__))

        # ---- Liste des images à afficher (diaporama) ----
        self.image_paths = [
            os.path.join(here, "vache01.png"),
            os.path.join(here, "vache02.png"),
            os.path.join(here, "vache03.png"),
            os.path.join(here, "vache04.png"),   # celle qui existe déjà
            os.path.join(here, "vache05.png"),
        ]
        # Ne garder que les fichiers qui existent vraiment
        self.image_paths = [p for p in self.image_paths if os.path.exists(p)]
        if not self.image_paths:
            # Fallback : on remonte d'un cran
            fallback = os.path.join(here, "..", "..", "vache04.png")
            if os.path.exists(fallback):
                self.image_paths = [fallback]
            else:
                self.image_paths = []   # pas d'image du tout

        self.current_index = 0
        self._pixmap = QPixmap()
        self._load_image()

        # ---- Timer pour changer d'image toutes les 10 secondes ----
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(10000)  # 10000 ms = 10 secondes

    def _load_image(self):
        """Charge l'image à l'index courant."""
        if self.image_paths:
            self._pixmap = QPixmap(self.image_paths[self.current_index])
        else:
            self._pixmap = QPixmap()
        self.update()  # force le redessin

    def next_image(self):
        """Passe à l'image suivante (boucle circulaire)."""
        if len(self.image_paths) > 1:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self._load_image()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w, h = self.width(), self.height()

        # Dessin de l'image (avec le même scaling que votre code original)
        if not self._pixmap.isNull():
            scaled = self._pixmap.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (scaled.width() - w) // 2
            y = (scaled.height() - h) // 2
            painter.drawPixmap(0, 0, scaled, x, y, w, h)
        else:
            painter.fillRect(0, 0, w, h, QColor("#2c2c2c"))

        # Filtre sombre
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 110))

        # Cadres dorés
        margin = 18
        pen_frame = QPen(QColor("#d4af37"), 3)
        painter.setPen(pen_frame)
        painter.drawRoundedRect(margin, margin, w - 2*margin, h - 2*margin, 12, 12)
        pen_inner = QPen(QColor("#d4af37"), 1)
        painter.setPen(pen_inner)
        m2 = margin + 7
        painter.drawRoundedRect(m2, m2, w - 2*m2, h - 2*m2, 8, 8)

        # Texte
        font = QFont("Parchment", 40, QFont.Bold)
        if not font.exactMatch():
            font = QFont("Parchment", 40)
        painter.setFont(font)

        padding = 50
        text_rect = QRect(padding, padding, w - 2 * padding, h - 2 * padding)

        painter.setPen(QColor(0, 0, 0, 180))
        shadow_rect = QRect(text_rect.x() + 2, text_rect.y() + 2,
                            text_rect.width(), text_rect.height())
        painter.drawText(shadow_rect, Qt.AlignCenter | Qt.TextWordWrap, MESSAGE)

        painter.setPen(QColor("#F5E6C8"))
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, MESSAGE)

        painter.end()


class MainWindow(QMainWindow):
    def __init__(self, role=None, code_elevage=None):
        super().__init__()
        self.role = "admin" if role is None else role
        self.code_elevage = code_elevage or "0000"

        self.setWindowTitle("GESTROZ - Race Oulmès-Zaer")
        self.setGeometry(100, 100, 850, 700)
        self.setMinimumSize(600, 400)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c2c2c;
            }
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3a3a3a, stop:1 #2c2c2c);
                color: #f0f0f0;
                font-family: "Segoe UI", "Microsoft Sans Serif", sans-serif;
                font-size: 13px;
                font-weight: bold;
                border-bottom: 2px solid #d4af37;
                padding: 4px 0px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 12px;
                margin: 0px 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #d4af37;
                color: #2c2c2c;
            }
            QMenuBar::item:pressed {
                background-color: #b08a2e;
            }
            QMenu {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 25px;
                margin: 2px 5px;
                border-radius: 3px;
                color: #f0f0f0;
            }
            QMenu::item:selected {
                background-color: #d4af37;
                color: #2c2c2c;
            }
            QMenu::separator {
                height: 1px;
                background-color: #d4af37;
                margin: 5px 10px;
            }
        """)

        central = BackgroundWidget(self)
        self.setCentralWidget(central)

        QShortcut(QKeySequence("F1"), self).activated.connect(self.show_help)

        self.menubar = self.menuBar()
        self.build_menus()
        self.windows = {}

    def build_menus(self):
        menubar = self.menubar

        # ----- MENU ÉLEVAGE -----
        menu_elevage = menubar.addMenu("🐄 Élevage")
        if SaisieConsultationEleveursWindow is not None:
            menu_elevage.addAction("Éleveurs", self.open_eleveurs)
        if SaisieConsultationAnimauxWindow is not None:
            menu_elevage.addAction("Animaux", self.open_animaux)
        menu_elevage.addSeparator()
        if SaisieConsultationNaissancesWindow is not None:
            menu_elevage.addAction("Naissances", self.open_naissance)
        if SaisieConsultationSevragesWindow is not None:
            menu_elevage.addAction("Sevrages", self.open_sevrage)
        if SaisieConsultationCroissanceWindow is not None:
            menu_elevage.addAction("Pesées (croissance)", self.open_croissance)
        if GestionReproductionWindow is not None:
            menu_elevage.addAction("Reproduction", self.open_reproduction)
        if SaisieConsultationVentesWindow is not None:
            menu_elevage.addAction("Ventes", self.open_vente)
        if SaisieConsultationMortalitesWindow is not None:
            menu_elevage.addAction("Mortalités", self.open_mortalite)

        # Prophylaxie
        if GestionVaccinationsWindow is not None or GestionTraitementsWindow is not None:
            menu_prophy = menu_elevage.addMenu("💊 Prophylaxie")
            if GestionVaccinationsWindow is not None:
                menu_prophy.addAction("Vaccinations", self.open_vaccinations)
            if GestionTraitementsWindow is not None:
                menu_prophy.addAction("Traitements curatifs", self.open_traitements)

        # Alimentation
        if (SaisieConsultationStockWindow is not None or RationnementWindow is not None):
            menu_alim = menu_elevage.addMenu("🥕 Alimentation")
            if SaisieConsultationStockWindow is not None:
                menu_alim.addAction("Saisie consultation stock", self.open_stock)
            if RationnementWindow is not None:
                menu_alim.addAction("Rationnement", self.open_rationnement)

        menu_elevage.addSeparator()
        menu_elevage.addAction("Quitter", self.close)

        # ----- MENU AGRONOMIE -----
        if (SaisieConsultationFoncierWindow is not None or
            SaisieConsultationCulturalesWindow is not None or
            SaisieConsultationArboricultureWindow is not None):
            menu_agro = menubar.addMenu("🌾 Agronomie")
            if self.role in ["admin", "technicien", "operateur"]:
                if SaisieConsultationFoncierWindow is not None:
                    menu_agro.addAction("Capital foncier", self.open_foncier)
                if SaisieConsultationCulturalesWindow is not None:
                    menu_agro.addAction("Pratiques culturales", self.open_culturales)
                if SaisieConsultationArboricultureWindow is not None:
                    menu_agro.addAction("Arboriculture", self.open_arboriculture)
        else:
            # Fallback
            menu_agro = menubar.addMenu("🌾 Agronomie")
            if self.role in ["admin", "technicien", "operateur"]:
                menu_agro.addAction("Capital foncier", self.open_foncier)
                menu_agro.addAction("Pratiques culturales", self.open_culturales)
                menu_agro.addAction("Arboriculture", self.open_arboriculture)

        # ----- MENU FAMILLE (NOUVEAU) -----
        if SaisieConsultationFamilleWindow is not None:
            menu_fam = menubar.addMenu("👨‍👩‍👧‍👦 Famille")
            if self.role in ["admin", "technicien", "operateur"]:
                menu_fam.addAction("Membres de la famille", self.open_famille)

        # ----- MENU AUTRES RESSOURCES -----
        if GestionRessourcesWindow is not None:
            menu_res = menubar.addMenu("🐑 Autres ressources")
            if self.role in ["admin", "technicien", "operateur"]:
                menu_res.addAction("Ovins, caprins, équidés, volailles", self.open_ressources)

        # ----- MENU ÉCONOMIE -----
        if GestionEconomiqueWindow is not None:
            menu_eco = menubar.addMenu("💰 Économie")
            if self.role in ["admin", "technicien", "operateur"]:
                menu_eco.addAction("Coûts et marges", self.open_economie)
                menu_eco.addAction("Comptabilité (Produits/Charges)", self.open_comptabilite)

        # ----- MENU ANALYSES -----
        menu_analyses = menubar.addMenu("📈 Analyses")
        if AnalyseEffectifWindow is not None:
            menu_analyses.addAction("Effectif par commune et catégorie", self.open_analyse_effectif)
        if AnalyseCroissanceWindow is not None:
            menu_analyses.addAction("Croissance (GMQ) par sexe et commune", self.open_analyse_croissance)
        if AnalyseVentesWindow is not None:
            menu_analyses.addAction("Ventes par commune", self.open_analyse_ventes)
        if AnalyseDecesWindow is not None:
            menu_analyses.addAction("Décès par commune", self.open_analyse_deces)

        # ----- MENU PILOTAGE -----
        menu_pilotage = menubar.addMenu("🎛️ Pilotage")
        menu_pilotage.addAction("Tableau de bord", self.open_dashboard)
        menu_pilotage.addAction("Visites", self.open_visites)

        # ----- MENU OUTILS -----
        menu_outils = menubar.addMenu("🛠️ Outils")
        if self.role == "admin" and GestionUtilisateursWindow is not None:
            menu_outils.addAction("Gestion des utilisateurs", self.open_gestion_utilisateurs)
        menu_outils.addAction("Import Excel", self.open_import)
        menu_outils.addAction("Export Excel", self.open_export)
        if ExportONSSAWindow is not None:
            menu_outils.addAction("Export ONSSA", self.open_export_onssa)
        menu_outils.addSeparator()

        # Bibliothèque
        if GestionBibliothequeAlimentsWindow is not None or SaisieConsultationBesoinWindow is not None:
            menu_biblio = menu_outils.addMenu("📚 Bibliothèque")
            if GestionBibliothequeAlimentsWindow is not None:
                menu_biblio.addAction("Aliments", self.open_bibliotheque)
            if SaisieConsultationBesoinWindow is not None:
                menu_biblio.addAction("Besoins nutritionnels", self.open_besoins)

        if self.role in ["admin", "technicien", "operateur"]:
            menu_outils.addAction("Sauvegarde", self.backup_db)
        menu_outils.addSeparator()
        menu_outils.addAction("Aide (F1)", self.show_help)
        menu_outils.addAction("À propos", self.show_about)

    # ========== MÉTHODES D'OUVERTURE ==========
    def open_eleveurs(self):
        if SaisieConsultationEleveursWindow is not None:
            self.windows['eleveurs'] = SaisieConsultationEleveursWindow()
            self.windows['eleveurs'].show()

    def open_animaux(self):
        if SaisieConsultationAnimauxWindow is not None:
            self.windows['animaux'] = SaisieConsultationAnimauxWindow()
            self.windows['animaux'].show()

    def open_naissance(self):
        if SaisieConsultationNaissancesWindow is not None:
            self.windows['naissance'] = SaisieConsultationNaissancesWindow()
            self.windows['naissance'].show()

    def open_sevrage(self):
        if SaisieConsultationSevragesWindow is not None:
            self.windows['sevrage'] = SaisieConsultationSevragesWindow()
            self.windows['sevrage'].show()

    def open_croissance(self):
        if SaisieConsultationCroissanceWindow is not None:
            self.windows['croissance'] = SaisieConsultationCroissanceWindow()
            self.windows['croissance'].show()

    def open_reproduction(self):
        if GestionReproductionWindow is not None:
            self.windows['reproduction'] = GestionReproductionWindow()
            self.windows['reproduction'].show()

    def open_vente(self):
        if SaisieConsultationVentesWindow is not None:
            self.windows['vente'] = SaisieConsultationVentesWindow()
            self.windows['vente'].show()

    def open_mortalite(self):
        if SaisieConsultationMortalitesWindow is not None:
            self.windows['mortalite'] = SaisieConsultationMortalitesWindow()
            self.windows['mortalite'].show()

    def open_vaccinations(self):
        if GestionVaccinationsWindow is not None:
            self.windows['vaccinations'] = GestionVaccinationsWindow()
            self.windows['vaccinations'].show()

    def open_traitements(self):
        if GestionTraitementsWindow is not None:
            self.windows['traitements'] = GestionTraitementsWindow()
            self.windows['traitements'].show()

    def open_parcelles(self):
        if GestionParcellesWindow is not None:
            self.windows['parcelles'] = GestionParcellesWindow()
            self.windows['parcelles'].show()

    def open_arboriculture(self):
        if GestionArboricultureWindow is not None:
            self.windows['arboriculture'] = GestionArboricultureWindow()
            self.windows['arboriculture'].show()

    # === AGRONOMIE ===
    def open_foncier(self):
        if SaisieConsultationFoncierWindow is not None:
            self.windows['foncier'] = SaisieConsultationFoncierWindow()
            self.windows['foncier'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Saisie consultation foncier non disponible.")

    def open_culturales(self):
        if SaisieConsultationCulturalesWindow is not None:
            self.windows['culturales'] = SaisieConsultationCulturalesWindow()
            self.windows['culturales'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Saisie consultation culturales non disponible.")

    def open_arboriculture(self):
        if SaisieConsultationArboricultureWindow is not None:
            self.windows['arboriculture'] = SaisieConsultationArboricultureWindow()
            self.windows['arboriculture'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Saisie consultation arboriculture non disponible.")

    # === ALIMENTATION ===
    def open_stock(self):
        if SaisieConsultationStockWindow is not None:
            self.windows['stock'] = SaisieConsultationStockWindow()
            self.windows['stock'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Saisie consultation stock non disponible.")

    def open_rationnement(self):
        if RationnementWindow is not None:
            self.windows['rationnement'] = RationnementWindow()
            self.windows['rationnement'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Rationnement non disponible.")

    # === BIBLIOTHÈQUES ===
    def open_bibliotheque(self):
        if GestionBibliothequeAlimentsWindow is not None:
            self.windows['bibliotheque'] = GestionBibliothequeAlimentsWindow()
            self.windows['bibliotheque'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Bibliothèque d'aliments non disponible.")

    def open_besoins(self):
        if SaisieConsultationBesoinWindow is not None:
            self.windows['besoins'] = SaisieConsultationBesoinWindow()
            self.windows['besoins'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Bibliothèque des besoins non disponible.")

    # === FAMILLE (NOUVEAU) ===
    def open_famille(self):
        if SaisieConsultationFamilleWindow is not None:
            self.windows['famille'] = SaisieConsultationFamilleWindow()
            self.windows['famille'].show()
        else:
            QMessageBox.warning(self, "Module manquant", "Saisie consultation famille non disponible.")

    def open_ajout_stock(self):
        if AjoutStockWindow is not None:
            self.windows['ajout_stock'] = AjoutStockWindow()
            self.windows['ajout_stock'].show()

    def open_gestion_stocks(self):
        if GestionStocksWindow is not None:
            self.windows['gestion_stocks'] = GestionStocksWindow()
            self.windows['gestion_stocks'].show()

    def open_gestion_utilisateurs(self):
        if GestionUtilisateursWindow is not None:
            self.windows['utilisateurs'] = GestionUtilisateursWindow()
            self.windows['utilisateurs'].show()

    def open_ressources(self):
        if GestionRessourcesWindow is not None:
            self.windows['ressources'] = GestionRessourcesWindow()
            self.windows['ressources'].show()

    def open_economie(self):
        if GestionEconomiqueWindow is not None:
            self.windows['economie'] = GestionEconomiqueWindow()
            self.windows['economie'].show()

    def open_comptabilite(self):
        from ui.windows.comptabilite_window import ComptabiliteWindow
        self.windows['comptabilite'] = ComptabiliteWindow()
        self.windows['comptabilite'].show()

    def open_dashboard(self):
        if DashboardTables is not None:
            dialog = QDialog(self)
            dialog.setWindowTitle("Tableau de bord - GESTROZ Zaer")
            dialog.setMinimumSize(900, 700)
            d_layout = QVBoxLayout(dialog)
            dashboard = DashboardTables(dialog)
            d_layout.addWidget(dashboard)
            btn_close = QPushButton("Fermer")
            btn_close.clicked.connect(dialog.accept)
            d_layout.addWidget(btn_close, alignment=Qt.AlignRight)
            dialog.exec()
        else:
            QMessageBox.information(self, "Info", "Tableau de bord non disponible.")

    def open_visites(self):
        QMessageBox.information(self, "Info", "Fonctionnalité 'Visites' à venir.")

    def open_analyse_effectif(self):
        if AnalyseEffectifWindow is not None:
            self.windows['analyse_effectif'] = AnalyseEffectifWindow()
            self.windows['analyse_effectif'].show()

    def open_analyse_croissance(self):
        if AnalyseCroissanceWindow is not None:
            self.windows['analyse_croissance'] = AnalyseCroissanceWindow()
            self.windows['analyse_croissance'].show()

    def open_analyse_ventes(self):
        if AnalyseVentesWindow is not None:
            self.windows['analyse_ventes'] = AnalyseVentesWindow()
            self.windows['analyse_ventes'].show()

    def open_analyse_deces(self):
        if AnalyseDecesWindow is not None:
            self.windows['analyse_deces'] = AnalyseDecesWindow()
            self.windows['analyse_deces'].show()

    def open_export_onssa(self):
        if ExportONSSAWindow is not None:
            self.windows['export_onssa'] = ExportONSSAWindow()
            self.windows['export_onssa'].show()

    def open_import(self):
        if importer_eleveurs_depuis_excel is None or importer_animaux_depuis_excel is None:
            QMessageBox.warning(self, "Erreur", "Contrôleurs d'import non disponibles.")
            return
        types = ["Éleveurs", "Animaux"]
        choix, ok = QInputDialog.getItem(self, "Import", "Type :", types, 0, False)
        if not ok or not choix:
            return
        path, _ = QFileDialog.getOpenFileName(self, f"Importer {choix}", "", "*.xlsx")
        if not path:
            return
        try:
            if choix == "Éleveurs":
                nb, err = importer_eleveurs_depuis_excel(path)
            else:
                nb, err = importer_animaux_depuis_excel(path)
            if err:
                QMessageBox.warning(self, "Avertissement", f"{nb} lignes importées.\nErreurs :\n" + "\n".join(err[:15]))
            else:
                QMessageBox.information(self, "Succès", f"{nb} {choix.lower()} importés.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def open_export(self):
        QMessageBox.information(self, "Export", "Utilisez le bouton 'Exporter Excel' dans chaque fenêtre.")

    def backup_db(self):
        try:
            from database.db_session import DB_PATH
            import shutil
            from datetime import datetime
            d = os.path.join(os.path.dirname(DB_PATH), "backups")
            os.makedirs(d, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = os.path.join(d, f"zaer_backup_{ts}.db")
            shutil.copy2(DB_PATH, dst)
            QMessageBox.information(self, "Succès", f"Sauvegarde : {dst}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la sauvegarde : {e}")

    def show_help(self):
        if HelpWindow is not None:
            HelpWindow(self).exec()
        else:
            QMessageBox.information(self, "Aide", "Aide non disponible.")

    def show_about(self):
        QMessageBox.about(self, "À propos", "GESTROZ - SmartÉlevage\nVersion 1.0\n© MOUMEN Idriss\nmoumen.idriss@gmail.com")