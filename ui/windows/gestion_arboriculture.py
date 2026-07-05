from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QTabWidget, QHeaderView, QSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur
from controllers.arboriculture_controller import ArboricultureController

class GestionArboricultureWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Arboriculture")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        # Filtre par éleveur
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Éleveur :"))
        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        filter_layout.addWidget(self.code_combo)
        layout.addLayout(filter_layout)

        # Onglets
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Onglet Arbres
        self.arbres_tab = QWidget()
        self.setup_arbres_tab()
        self.tabs.addTab(self.arbres_tab, "🌳 Arbres")

        # Onglet Traitements
        self.traitements_tab = QWidget()
        self.setup_traitements_tab()
        self.tabs.addTab(self.traitements_tab, "🧪 Traitements (engrais/phytos)")

        # Bouton Fermer
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        self.current_arbre_id = None
        self.current_traitement_id = None
        self.on_eleveur_changed()

    def get_all_codes(self):
        db = SessionLocal()
        codes = [e.code_elevage for e in db.query(Eleveur).all()]
        db.close()
        return codes

    def on_eleveur_changed(self):
        code = self.code_combo.currentText().strip()
        self.load_arbres(code)
        self.annuler_arbre()
        self.annuler_traitement()

    # ---------------------- Onglet Arbres ----------------------
    def setup_arbres_tab(self):
        layout = QVBoxLayout(self.arbres_tab)

        form = QFormLayout()
        self.nom_arbre = QLineEdit()
        form.addRow("Nom de l'arbre :", self.nom_arbre)
        self.nombre_arbres = QSpinBox()
        self.nombre_arbres.setRange(0, 100000)
        form.addRow("Nombre d'arbres :", self.nombre_arbres)
        self.destination = QComboBox()
        self.destination.addItems(["", "Autoconsommation", "Vente"])
        form.addRow("Destination :", self.destination)
        self.arbre_obs = QLineEdit()
        form.addRow("Observations :", self.arbre_obs)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.btn_add_arbre = QPushButton("Ajouter")
        self.btn_add_arbre.clicked.connect(self.ajouter_arbre)
        self.btn_modify_arbre = QPushButton("Modifier")
        self.btn_modify_arbre.clicked.connect(self.modifier_arbre)
        self.btn_delete_arbre = QPushButton("Supprimer")
        self.btn_delete_arbre.clicked.connect(self.supprimer_arbre)
        self.btn_cancel_arbre = QPushButton("Annuler")
        self.btn_cancel_arbre.clicked.connect(self.annuler_arbre)
        btn_layout.addWidget(self.btn_add_arbre)
        btn_layout.addWidget(self.btn_modify_arbre)
        btn_layout.addWidget(self.btn_delete_arbre)
        btn_layout.addWidget(self.btn_cancel_arbre)
        layout.addLayout(btn_layout)

        self.table_arbres = QTableWidget()
        self.table_arbres.setColumnCount(5)
        self.table_arbres.setHorizontalHeaderLabels(["ID", "Nom", "Nombre", "Destination", "Observations"])
        self.table_arbres.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_arbres.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_arbres.itemSelectionChanged.connect(self.on_arbre_selected)
        layout.addWidget(self.table_arbres)

    def load_arbres(self, code_elevage):
        if not code_elevage:
            self.table_arbres.setRowCount(0)
            return
        arbres = ArboricultureController.get_arbres_par_eleveur(code_elevage)
        self.table_arbres.setRowCount(len(arbres))
        for i, a in enumerate(arbres):
            self.table_arbres.setItem(i, 0, QTableWidgetItem(str(a.id)))
            self.table_arbres.setItem(i, 1, QTableWidgetItem(a.nom_arbre))
            self.table_arbres.setItem(i, 2, QTableWidgetItem(str(a.nombre_arbres)))
            self.table_arbres.setItem(i, 3, QTableWidgetItem(a.destination or ""))
            self.table_arbres.setItem(i, 4, QTableWidgetItem(a.observations or ""))
        self.table_arbres.resizeColumnsToContents()

    def on_arbre_selected(self):
        row = self.table_arbres.currentRow()
        if row < 0:
            self.current_arbre_id = None
            self.annuler_arbre()
            return
        self.current_arbre_id = int(self.table_arbres.item(row, 0).text())
        self.nom_arbre.setText(self.table_arbres.item(row, 1).text())
        self.nombre_arbres.setValue(int(self.table_arbres.item(row, 2).text()))
        self.destination.setCurrentText(self.table_arbres.item(row, 3).text())
        self.arbre_obs.setText(self.table_arbres.item(row, 4).text())
        self.load_traitements(self.current_arbre_id)

    def annuler_arbre(self):
        self.current_arbre_id = None
        self.nom_arbre.clear()
        self.nombre_arbres.setValue(0)
        self.destination.setCurrentIndex(0)
        self.arbre_obs.clear()
        self.load_arbres(self.code_combo.currentText().strip())

    def ajouter_arbre(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        if not self.nom_arbre.text().strip() or self.nombre_arbres.value() == 0:
            QMessageBox.warning(self, "Erreur", "Nom et nombre d'arbres obligatoires.")
            return
        data = {
            'code_elevage': code,
            'nom_arbre': self.nom_arbre.text().strip(),
            'nombre_arbres': self.nombre_arbres.value(),
            'destination': self.destination.currentText() or None,
            'observations': self.arbre_obs.text().strip() or None
        }
        ok, aid, msg = ArboricultureController.ajouter_arbre(data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.on_eleveur_changed()
            self.annuler_arbre()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def modifier_arbre(self):
        if self.current_arbre_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un arbre.")
            return
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Élevage non reconnu.")
            return
        data = {
            'nom_arbre': self.nom_arbre.text().strip(),
            'nombre_arbres': self.nombre_arbres.value(),
            'destination': self.destination.currentText() or None,
            'observations': self.arbre_obs.text().strip() or None
        }
        ok, msg = ArboricultureController.modifier_arbre(self.current_arbre_id, data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.on_eleveur_changed()
            self.annuler_arbre()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def supprimer_arbre(self):
        if self.current_arbre_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un arbre.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet arbre (tous ses traitements) ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = ArboricultureController.supprimer_arbre(self.current_arbre_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.on_eleveur_changed()
                self.annuler_arbre()
            else:
                QMessageBox.warning(self, "Erreur", msg)

    # ---------------------- Onglet Traitements ----------------------
    def setup_traitements_tab(self):
        layout = QVBoxLayout(self.traitements_tab)

        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Arbre :"))
        self.arbre_combo = QComboBox()
        self.arbre_combo.currentIndexChanged.connect(self.on_arbre_combo_changed)
        select_layout.addWidget(self.arbre_combo)
        select_layout.addStretch()
        layout.addLayout(select_layout)

        form = QFormLayout()
        self.type_traitement = QComboBox()
        self.type_traitement.addItems(["Engrais", "Phytosanitaire"])
        form.addRow("Type de traitement :", self.type_traitement)
        self.date_traitement = QDateEdit()
        self.date_traitement.setCalendarPopup(True)
        self.date_traitement.setDate(QDate.currentDate())
        self.date_traitement.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Date :", self.date_traitement)
        self.produit = QLineEdit()
        form.addRow("Produit :", self.produit)
        self.dose = QLineEdit()
        self.dose.setPlaceholderText("Ex: 2 L/ha, 500 g/arbre")
        form.addRow("Dose :", self.dose)
        self.traitement_obs = QLineEdit()
        form.addRow("Observations :", self.traitement_obs)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.btn_add_traitement = QPushButton("Ajouter")
        self.btn_add_traitement.clicked.connect(self.ajouter_traitement)
        self.btn_modify_traitement = QPushButton("Modifier")
        self.btn_modify_traitement.clicked.connect(self.modifier_traitement)
        self.btn_delete_traitement = QPushButton("Supprimer")
        self.btn_delete_traitement.clicked.connect(self.supprimer_traitement)
        self.btn_cancel_traitement = QPushButton("Annuler")
        self.btn_cancel_traitement.clicked.connect(self.annuler_traitement)
        btn_layout.addWidget(self.btn_add_traitement)
        btn_layout.addWidget(self.btn_modify_traitement)
        btn_layout.addWidget(self.btn_delete_traitement)
        btn_layout.addWidget(self.btn_cancel_traitement)
        layout.addLayout(btn_layout)

        self.table_traitements = QTableWidget()
        self.table_traitements.setColumnCount(5)
        self.table_traitements.setHorizontalHeaderLabels(["ID", "Type", "Date", "Produit", "Dose"])
        self.table_traitements.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_traitements.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_traitements.itemSelectionChanged.connect(self.on_traitement_selected)
        layout.addWidget(self.table_traitements)

    def load_arbre_combo(self):
        code = self.code_combo.currentText().strip()
        self.arbre_combo.clear()
        if not code:
            return
        arbres = ArboricultureController.get_arbres_par_eleveur(code)
        for a in arbres:
            self.arbre_combo.addItem(f"{a.nom_arbre} ({a.nombre_arbres} arbres)", a.id)
        if self.arbre_combo.count() > 0:
            self.arbre_combo.setCurrentIndex(0)
        else:
            self.table_traitements.setRowCount(0)

    def on_arbre_combo_changed(self):
        self.current_arbre_id = self.arbre_combo.currentData()
        self.load_traitements(self.current_arbre_id)
        self.annuler_traitement()

    def load_traitements(self, arbre_id):
        if not arbre_id:
            self.table_traitements.setRowCount(0)
            return
        traitements = ArboricultureController.get_traitements_par_arbre(arbre_id)
        self.table_traitements.setRowCount(len(traitements))
        for i, t in enumerate(traitements):
            self.table_traitements.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table_traitements.setItem(i, 1, QTableWidgetItem(t.type_traitement))
            self.table_traitements.setItem(i, 2, QTableWidgetItem(t.date_traitement))
            self.table_traitements.setItem(i, 3, QTableWidgetItem(t.produit or ""))
            self.table_traitements.setItem(i, 4, QTableWidgetItem(t.dose or ""))
        self.table_traitements.resizeColumnsToContents()

    def on_traitement_selected(self):
        row = self.table_traitements.currentRow()
        if row < 0:
            self.current_traitement_id = None
            return
        self.current_traitement_id = int(self.table_traitements.item(row, 0).text())
        self.type_traitement.setCurrentText(self.table_traitements.item(row, 1).text())
        self.date_traitement.setDate(QDate.fromString(self.table_traitements.item(row, 2).text(), "yyyy-MM-dd"))
        self.produit.setText(self.table_traitements.item(row, 3).text())
        self.dose.setText(self.table_traitements.item(row, 4).text())

    def annuler_traitement(self):
        self.current_traitement_id = None
        self.type_traitement.setCurrentIndex(0)
        self.date_traitement.setDate(QDate.currentDate())
        self.produit.clear()
        self.dose.clear()
        self.traitement_obs.clear()

    def ajouter_traitement(self):
        if self.current_arbre_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez d'abord un arbre.")
            return
        data = {
            'arbre_id': self.current_arbre_id,
            'type_traitement': self.type_traitement.currentText(),
            'date_traitement': self.date_traitement.date().toString("yyyy-MM-dd"),
            'produit': self.produit.text().strip() or None,
            'dose': self.dose.text().strip() or None,
            'observations': self.traitement_obs.text().strip() or None
        }
        ok, tid, msg = ArboricultureController.ajouter_traitement(data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_traitements(self.current_arbre_id)
            self.annuler_traitement()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def modifier_traitement(self):
        if self.current_traitement_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un traitement.")
            return
        data = {
            'type_traitement': self.type_traitement.currentText(),
            'date_traitement': self.date_traitement.date().toString("yyyy-MM-dd"),
            'produit': self.produit.text().strip() or None,
            'dose': self.dose.text().strip() or None,
            'observations': self.traitement_obs.text().strip() or None
        }
        ok, msg = ArboricultureController.modifier_traitement(self.current_traitement_id, data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_traitements(self.current_arbre_id)
            self.annuler_traitement()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def supprimer_traitement(self):
        if self.current_traitement_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un traitement.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer ce traitement ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = ArboricultureController.supprimer_traitement(self.current_traitement_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_traitements(self.current_arbre_id)
                self.annuler_traitement()
            else:
                QMessageBox.warning(self, "Erreur", msg)
