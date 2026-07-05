# ui/widgets/dashboard_tables.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGridLayout, QFrame, QComboBox, QTableWidget,
                               QTableWidgetItem, QHeaderView, QTabWidget,
                               QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import sqlite3
from datetime import date

class DashboardTables(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tableau de bord régional - GESTROZ")
        self.setMinimumSize(900, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # Titre
        title = QLabel("📊 Tableau de bord GESTROZ")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Filtre commune
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("📍 Commune :"))
        self.commune_combo = QComboBox()
        self.commune_combo.addItem("🌍 Toutes les communes")
        self.commune_combo.currentTextChanged.connect(self.refresh_dashboard)
        filter_layout.addWidget(self.commune_combo)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # Onglets
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Onglet 1 : Indicateurs généraux (cartes) ---
        self.tab_general = QWidget()
        general_layout = QVBoxLayout(self.tab_general)
        self.card_grid = QGridLayout()
        self.card_grid.setSpacing(10)
        general_layout.addLayout(self.card_grid)
        general_layout.addStretch()
        self.tabs.addTab(self.tab_general, "📊 Général")

        # --- Onglet 2 : Tableaux détaillés (avec scroll) ---
        self.tab_details = QWidget()
        details_layout = QVBoxLayout(self.tab_details)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(2)
        self.detail_table.setHorizontalHeaderLabels(["Indicateur", "Valeur"])
        self.detail_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.detail_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.detail_table.setAlternatingRowColors(True)
        scroll_layout.addWidget(self.detail_table)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        details_layout.addWidget(scroll)
        self.tabs.addTab(self.tab_details, "📋 Détails")

        self.load_communes()
        self.refresh_dashboard()

    # ------------------------------------------------------------
    # 1. Chargement des communes
    # ------------------------------------------------------------
    def load_communes(self):
        conn = sqlite3.connect("data/zaer.db")
        cur = conn.cursor()
        communes = [row[0] for row in cur.execute(
            "SELECT DISTINCT commune FROM eleveurs WHERE commune IS NOT NULL AND commune != '' ORDER BY commune"
        ).fetchall()]
        conn.close()
        for c in communes:
            self.commune_combo.addItem(c)

    # ------------------------------------------------------------
    # 2. Rafraîchissement
    # ------------------------------------------------------------
    def refresh_dashboard(self):
        commune = self.commune_combo.currentText()
        if commune == "🌍 Toutes les communes" or not commune:
            commune_filter = None
        else:
            commune_filter = commune

        conn = sqlite3.connect("data/zaer.db")
        cur = conn.cursor()

        if commune_filter:
            codes = [row[0] for row in cur.execute(
                "SELECT code_elevage FROM eleveurs WHERE commune = ?", (commune_filter,)
            ).fetchall()]
            if not codes:
                self._clear_cards()
                self._show_empty_message()
                conn.close()
                return
            code_tuple = tuple(codes)
            code_condition = f"code_elevage IN {code_tuple}"
        else:
            code_condition = "1=1"

        # --- Indicateurs ---
        if commune_filter:
            nb_eleveurs = cur.execute(
                "SELECT COUNT(*) FROM eleveurs WHERE commune = ?", (commune_filter,)
            ).fetchone()[0]
        else:
            nb_eleveurs = cur.execute("SELECT COUNT(*) FROM eleveurs").fetchone()[0]

        nb_animaux = cur.execute(f"SELECT COUNT(*) FROM animaux WHERE {code_condition}").fetchone()[0]

        res = cur.execute(
            f"SELECT COUNT(*), SUM(surface_ha) FROM parcelles WHERE {code_condition}"
        ).fetchone()
        nb_parcelles = res[0] or 0
        surface_totale = res[1] or 0.0

        nb_naissances = cur.execute(
            f"SELECT COUNT(*) FROM naissances WHERE {code_condition} AND date_naissance >= date('now', '-30 days')"
        ).fetchone()[0]

        nb_ventes = cur.execute(
            f"SELECT COUNT(*) FROM ventes WHERE {code_condition} AND date_vente >= date('now', '-30 days')"
        ).fetchone()[0]

        nb_mortalites = cur.execute(
            f"SELECT COUNT(*) FROM mortalites WHERE {code_condition} AND date_deces >= date('now', '-30 days')"
        ).fetchone()[0]

        # Âge
        if commune_filter:
            ages = cur.execute(
                "SELECT date_naissance FROM eleveurs WHERE commune = ? AND date_naissance IS NOT NULL",
                (commune_filter,)
            ).fetchall()
        else:
            ages = cur.execute(
                "SELECT date_naissance FROM eleveurs WHERE date_naissance IS NOT NULL"
            ).fetchall()
        ages_val = []
        for (dnaiss,) in ages:
            try:
                an_naiss = int(dnaiss.split('-')[0])
                age = date.today().year - an_naiss
                if 0 < age < 100:
                    ages_val.append(age)
            except:
                pass
        age_moy = sum(ages_val) / len(ages_val) if ages_val else 0
        age_min = min(ages_val) if ages_val else 0
        age_max = max(ages_val) if ages_val else 0

        taux_mortalite = (nb_mortalites / nb_animaux * 100) if nb_animaux > 0 else 0

        poids_naiss = cur.execute(
            f"SELECT AVG(poids_naissance) FROM naissances WHERE {code_condition} AND poids_naissance IS NOT NULL"
        ).fetchone()[0]

        ca_total = cur.execute(
            f"SELECT SUM(prix_vente) FROM ventes WHERE {code_condition} AND prix_vente IS NOT NULL"
        ).fetchone()[0]

        if commune_filter:
            produits = cur.execute(
                f"SELECT SUM(montant) FROM compta_produits WHERE code_elevage IN {code_tuple}"
            ).fetchone()[0] or 0
            charges = cur.execute(
                f"SELECT SUM(montant) FROM compta_charges WHERE code_elevage IN {code_tuple}"
            ).fetchone()[0] or 0
        else:
            produits = cur.execute("SELECT SUM(montant) FROM compta_produits").fetchone()[0] or 0
            charges = cur.execute("SELECT SUM(montant) FROM compta_charges").fetchone()[0] or 0
        marge = produits - charges

        nb_mouvements = cur.execute(
            f"SELECT COUNT(*) FROM mouvements_stock WHERE {code_condition}"
        ).fetchone()[0]

        conn.close()

        # --- Mise à jour des cartes ---
        self._clear_cards()
        self._add_card("🐄 Éleveurs", str(nb_eleveurs), 0, 0)
        self._add_card("🐮 Animaux", str(nb_animaux), 0, 1)
        self._add_card("🌾 Parcelles", f"{nb_parcelles}\n{surface_totale:.1f} ha", 0, 2)
        self._add_card("🐣 Naissances (30j)", str(nb_naissances), 0, 3)
        self._add_card("💰 Ventes (30j)", str(nb_ventes), 1, 0)
        self._add_card("💔 Mortalités (30j)", str(nb_mortalites), 1, 1)
        self._add_card("📊 Âge moyen", f"{age_moy:.1f} ans\n(min {age_min}, max {age_max})", 1, 2)
        self._add_card("📉 Taux mortalité", f"{taux_mortalite:.1f}%", 1, 3)
        self._add_card("⚖️ Poids naiss.", f"{poids_naiss:.1f} kg" if poids_naiss else "N/D", 2, 0)
        self._add_card("💰 CA total", f"{ca_total:,.0f} DH" if ca_total else "0 DH", 2, 1)
        self._add_card("📊 Marge nette", f"{marge:,.0f} DH" if marge else "0 DH", 2, 2)
        self._add_card("📦 Mouvements stock", str(nb_mouvements), 2, 3)

        # --- Détails ---
        self._fill_detail_table(commune_filter)

    # ------------------------------------------------------------
    # 3. Gestion des cartes
    # ------------------------------------------------------------
    def _clear_cards(self):
        for i in reversed(range(self.card_grid.count())):
            widget = self.card_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def _add_card(self, label, value, row, col):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 10px;
                padding: 8px;
                min-height: 50px;
                min-width: 120px;
            }
        """)
        vbox = QVBoxLayout(frame)
        vbox.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #d4af37; font-size: 12px; font-weight: bold;")
        val = QLabel(value)
        val.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        val.setAlignment(Qt.AlignCenter)
        val.setWordWrap(True)
        vbox.addWidget(lbl)
        vbox.addWidget(val)
        self.card_grid.addWidget(frame, row, col)

    def _show_empty_message(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("background-color: #3a3a3a; border-radius: 12px; padding: 20px;")
        vbox = QVBoxLayout(frame)
        msg = QLabel("Aucun éleveur trouvé dans cette commune.")
        msg.setStyleSheet("color: white; font-size: 16px;")
        msg.setAlignment(Qt.AlignCenter)
        vbox.addWidget(msg)
        self.card_grid.addWidget(frame, 0, 0, 1, 4)

    # ------------------------------------------------------------
    # 4. Tableau détaillé (avec titres de sections)
    # ------------------------------------------------------------
    def _fill_detail_table(self, commune_filter):
        conn = sqlite3.connect("data/zaer.db")
        cur = conn.cursor()

        if commune_filter:
            codes = [row[0] for row in cur.execute(
                "SELECT code_elevage FROM eleveurs WHERE commune = ?", (commune_filter,)
            ).fetchall()]
            if not codes:
                conn.close()
                return
            code_tuple = tuple(codes)
            code_condition = f"code_elevage IN {code_tuple}"
        else:
            code_condition = "1=1"

        data = []

        # --- SECTION 1 : SCOLAIRITÉ ---
        data.append(("--- SCOLAIRITÉ ---", ""))
        niveaux = cur.execute(f"""
            SELECT niveau_scolaire, COUNT(*)
            FROM eleveurs
            WHERE {code_condition}
            GROUP BY niveau_scolaire
            ORDER BY COUNT(*) DESC
        """).fetchall()
        for n, nb in niveaux:
            data.append((f"  {n or 'Non renseigné'}", nb))

        # --- SECTION 2 : ANIMAUX ---
        data.append(("--- ANIMAUX (sexe / catégorie) ---", ""))
        sexes = cur.execute(f"""
            SELECT sexe, COUNT(*)
            FROM animaux
            WHERE {code_condition}
            GROUP BY sexe
        """).fetchall()
        for s, nb in sexes:
            data.append((f"  Sexe {s or 'ND'}", nb))

        categories = cur.execute(f"""
            SELECT categorie, COUNT(*)
            FROM animaux
            WHERE {code_condition}
            GROUP BY categorie
            ORDER BY COUNT(*) DESC
        """).fetchall()
        for cat, nb in categories:
            data.append((f"  Catégorie {cat or 'ND'}", nb))

        # --- SECTION 3 : FONCIER ---
        data.append(("--- FONCIER (statuts / occupations) ---", ""))
        statuts = cur.execute(f"""
            SELECT statut_foncier, COUNT(*), SUM(surface_ha)
            FROM parcelles
            WHERE {code_condition}
            GROUP BY statut_foncier
            ORDER BY COUNT(*) DESC
        """).fetchall()
        for statut, nb, surf in statuts:
            surf_str = f"{surf:.1f} ha" if surf else "0 ha"
            data.append((f"  {statut or 'ND'}", f"{nb} parcelle(s) ({surf_str})"))

        occupations = cur.execute(f"""
            SELECT occupation_actuelle, COUNT(*)
            FROM parcelles
            WHERE {code_condition}
            GROUP BY occupation_actuelle
            ORDER BY COUNT(*) DESC
        """).fetchall()
        for occ, nb in occupations:
            data.append((f"  {occ or 'ND'}", nb))

        # --- SECTION 4 : COMPTABILITÉ ---
        data.append(("--- COMPTABILITÉ (produits / charges) ---", ""))
        produits_cat = cur.execute(f"""
            SELECT categorie, SUM(montant)
            FROM compta_produits
            WHERE {code_condition}
            GROUP BY categorie
            ORDER BY SUM(montant) DESC
        """).fetchall()
        for cat, mont in produits_cat:
            data.append((f"  {cat}", f"{mont:,.0f} DH"))

        charges_cat = cur.execute(f"""
            SELECT categorie, SUM(montant)
            FROM compta_charges
            WHERE {code_condition}
            GROUP BY categorie
            ORDER BY SUM(montant) DESC
        """).fetchall()
        for cat, mont in charges_cat:
            data.append((f"  {cat}", f"{mont:,.0f} DH"))

        conn.close()

        # Remplir le tableau avec styles
        self.detail_table.setRowCount(len(data))
        for i, (key, val) in enumerate(data):
            item_key = QTableWidgetItem(str(key))
            item_val = QTableWidgetItem(str(val))
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Style pour les titres de section (--- ---)
            if key.startswith("---") and key.endswith("---"):
                font = QFont()
                font.setBold(True)
                item_key.setFont(font)
                item_key.setForeground(Qt.white)
                # Fond gris foncé
                item_key.setBackground(Qt.darkGray)
                item_val.setBackground(Qt.darkGray)
                # Aligner le titre à gauche
                item_key.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            self.detail_table.setItem(i, 0, item_key)
            self.detail_table.setItem(i, 1, item_val)

        self.detail_table.resizeRowsToContents()