# ui/windows/comptabilite_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QComboBox, QLineEdit, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from database.db_session import SessionLocal
from database.models import Eleveur
import sqlite3

class ComptabiliteWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comptabilité - Produits et Charges")
        self.resize(1100, 650)

        layout = QVBoxLayout(self)

        # Sélecteur d'élevage (commun)
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Code élevage :"))
        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_code_changed)
        selector_layout.addWidget(self.code_combo)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # Onglets Produits / Charges
        self.tabs = QTabWidget()
        self.tab_produits = self.create_tab("compta_produits", [
            "Vente de bovins",
            "Vente d'ovins/caprins",
            "Vente de volailles",
            "Vente d'œufs",
            "Vente de lait",
            "Vente de laine",
            "Vente de miel",
            "Vente de fumier/compost",
            "Vente de paille",
            "Vente de fourrage",
            "Vente de grains",
            "Vente de fruits",
            "Vente de légumes",
            "Subventions/Aides",
            "Envois de fonds/Pension",
            "Autres revenus"
        ])
        self.tab_charges = self.create_tab("compta_charges", [
            "Alimentation du bétail",
            "Soins vétérinaires & médicaments",
            "Reproduction",
            "Main-d'œuvre",
            "Eau & électricité",
            "Entretien bâtiments & clôtures",
            "Transport & déplacements",
            "Achat d'animaux",
            "Impôts & taxes",
            "Divers / Imprévus"
        ])

        self.tabs.addTab(self.tab_produits, "📈 Produits")
        self.tabs.addTab(self.tab_charges, "📉 Charges")
        layout.addWidget(self.tabs)

        # Bouton Fermer en bas (aligné à droite)
        btn_close = QPushButton("❌ Fermer")
        btn_close.clicked.connect(self.close)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.current_code = None
        self.on_code_changed()

    def get_all_codes(self):
        db = SessionLocal()
        codes = [e.code_elevage for e in db.query(Eleveur).all()]
        db.close()
        return codes

    def on_code_changed(self):
        self.current_code = self.code_combo.currentText().strip()
        if hasattr(self, 'tab_produits'):
            self.load_table("compta_produits", self.tab_produits)
            self.load_table("compta_charges", self.tab_charges)

    def create_tab(self, table_name, categories):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Formulaire de saisie
        form_layout = QFormLayout()

        annee_edit = QSpinBox()
        annee_edit.setRange(2000, 2100)
        annee_edit.setValue(2025)
        form_layout.addRow(QLabel("Année :"), annee_edit)

        categorie_combo = QComboBox()
        categorie_combo.addItems([""] + categories)
        form_layout.addRow(QLabel("Catégorie :"), categorie_combo)

        description_edit = QLineEdit()
        description_edit.setPlaceholderText("Description libre (ex: vente de 3 agneaux)")
        form_layout.addRow(QLabel("Description :"), description_edit)

        montant_edit = QDoubleSpinBox()
        montant_edit.setRange(0, 10000000)
        montant_edit.setSuffix(" DH")
        form_layout.addRow(QLabel("Montant :"), montant_edit)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Ajouter")
        btn_update = QPushButton("✏️ Modifier")
        btn_delete = QPushButton("🗑️ Supprimer")
        btn_clear = QPushButton("🔄 Nouveau")
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_update)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_clear)
        btn_layout.addStretch()
        form_layout.addRow(btn_layout)

        layout.addLayout(form_layout)

        # Tableau
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Année", "Catégorie", "Description", "Montant (DH)"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.doubleClicked.connect(lambda: self.charger_selection(table_name, table))
        layout.addWidget(table)

        # Stocker les widgets dans le tab pour y accéder plus tard
        tab.table = table
        tab.annee_edit = annee_edit
        tab.categorie_combo = categorie_combo
        tab.description_edit = description_edit
        tab.montant_edit = montant_edit
        tab.btn_add = btn_add
        tab.btn_update = btn_update
        tab.btn_delete = btn_delete
        tab.btn_clear = btn_clear
        tab.current_id = None

        # Connecter les boutons
        btn_add.clicked.connect(lambda: self.ajouter(table_name, tab))
        btn_update.clicked.connect(lambda: self.modifier(table_name, tab))
        btn_delete.clicked.connect(lambda: self.supprimer(table_name, tab))
        btn_clear.clicked.connect(lambda: self.nouveau(tab))

        return tab

    def load_table(self, table_name, tab):
        code = self.current_code
        if not code:
            tab.table.setRowCount(0)
            return

        conn = sqlite3.connect('data/zaer.db')
        cur = conn.cursor()
        cur.execute(f"SELECT id, annee, categorie, description, montant FROM {table_name} WHERE code_elevage = ? ORDER BY annee DESC, id DESC", (code,))
        rows = cur.fetchall()
        conn.close()

        tab.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            tab.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            tab.table.setItem(i, 1, QTableWidgetItem(str(row[1])))
            tab.table.setItem(i, 2, QTableWidgetItem(row[2] or ""))
            tab.table.setItem(i, 3, QTableWidgetItem(row[3] or ""))
            tab.table.setItem(i, 4, QTableWidgetItem(f"{row[4]:.2f}" if row[4] else ""))
        tab.table.resizeColumnsToContents()

    def charger_selection(self, table_name, tab):
        row = tab.table.currentRow()
        if row < 0:
            return
        tab.current_id = int(tab.table.item(row, 0).text())
        tab.annee_edit.setValue(int(tab.table.item(row, 1).text()))
        tab.categorie_combo.setCurrentText(tab.table.item(row, 2).text())
        tab.description_edit.setText(tab.table.item(row, 3).text())
        montant_text = tab.table.item(row, 4).text().replace(" DH", "").strip()
        tab.montant_edit.setValue(float(montant_text) if montant_text else 0)

    def nouveau(self, tab):
        tab.current_id = None
        tab.annee_edit.setValue(2025)
        tab.categorie_combo.setCurrentIndex(0)
        tab.description_edit.clear()
        tab.montant_edit.setValue(0)

    def ajouter(self, table_name, tab):
        code = self.current_code
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        annee = tab.annee_edit.value()
        categorie = tab.categorie_combo.currentText()
        description = tab.description_edit.text().strip()
        montant = tab.montant_edit.value()

        if not categorie:
            QMessageBox.warning(self, "Erreur", "Choisissez une catégorie.")
            return
        if not description:
            QMessageBox.warning(self, "Erreur", "La description est obligatoire.")
            return
        if montant <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être positif.")
            return

        conn = sqlite3.connect('data/zaer.db')
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table_name} (code_elevage, annee, categorie, description, montant) VALUES (?, ?, ?, ?, ?)",
                    (code, annee, categorie, description, montant))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Succès", "Ligne ajoutée.")
        self.load_table(table_name, tab)
        self.nouveau(tab)

    def modifier(self, table_name, tab):
        if tab.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à modifier.")
            return

        code = self.current_code
        if not code:
            return

        annee = tab.annee_edit.value()
        categorie = tab.categorie_combo.currentText()
        description = tab.description_edit.text().strip()
        montant = tab.montant_edit.value()

        if not categorie or not description or montant <= 0:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être valides.")
            return

        conn = sqlite3.connect('data/zaer.db')
        cur = conn.cursor()
        cur.execute(f"UPDATE {table_name} SET annee=?, categorie=?, description=?, montant=? WHERE id=? AND code_elevage=?",
                    (annee, categorie, description, montant, tab.current_id, code))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Succès", "Ligne modifiée.")
        self.load_table(table_name, tab)
        self.nouveau(tab)

    def supprimer(self, table_name, tab):
        if tab.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à supprimer.")
            return

        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette ligne ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = sqlite3.connect('data/zaer.db')
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table_name} WHERE id=?", (tab.current_id,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Succès", "Ligne supprimée.")
        self.load_table(table_name, tab)
        self.nouveau(tab)