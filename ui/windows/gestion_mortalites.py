from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox, QComboBox, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QDateEdit)
from PySide6.QtCore import QDate
from database.db_session import SessionLocal
from database.models.eleveur import Eleveur
from database.models.mortalite import Mortalite
from controllers.mortalite_controller import MortaliteController

class ModifierMortaliteDialog(QDialog):
    def __init__(self, mort, parent=None):
        super().__init__(parent)
        self.mort = mort
        self.setWindowTitle("Modifier mortalité")
        self.setModal(True)
        layout = QFormLayout(self)
        self.numero_boucle = QLineEdit(mort.numero_boucle)
        self.date_deces = QDateEdit()
        self.date_deces.setCalendarPopup(True)
        self.date_deces.setDate(QDate.fromString(mort.date_deces, "yyyy-MM-dd"))
        self.date_deces.setDisplayFormat("yyyy-MM-dd")
        self.cause_deces = QLineEdit(mort.cause_deces)
        self.remarque = QLineEdit(mort.remarque or "")
        layout.addRow("Numéro boucle:", self.numero_boucle)
        layout.addRow("Date décès:", self.date_deces)
        layout.addRow("Cause:", self.cause_deces)
        layout.addRow("Remarque:", self.remarque)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    def get_data(self):
        return {
            'numero_boucle': self.numero_boucle.text(),
            'date_deces': self.date_deces.date().toString("yyyy-MM-dd"),
            'cause_deces': self.cause_deces.text(),
            'remarque': self.remarque.text()
        }

class GestionMortalitesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des mortalités")
        self.resize(1000, 600)
        layout = QVBoxLayout(self)

        # Filtre par éleveur
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Éleveur:"))
        self.combo_filtre = QComboBox()
        self.combo_filtre.addItem("Tous", None)
        db = SessionLocal()
        for e in db.query(Eleveur).all():
            self.combo_filtre.addItem(f"{e.code_elevage} - {e.nom} {e.prenom}", e.code_elevage)
        db.close()
        self.combo_filtre.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.combo_filtre)
        layout.addLayout(filter_layout)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Éleveur", "Boucle", "Date décès", "Cause", "Remarque"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.clicked.connect(self.load_data)
        btn_modifier = QPushButton("Modifier")
        btn_modifier.clicked.connect(self.modifier)
        btn_supprimer = QPushButton("Supprimer")
        btn_supprimer.clicked.connect(self.supprimer)
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_modifier)
        btn_layout.addWidget(btn_supprimer)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.load_data()

    def load_data(self):
        code_filtre = self.combo_filtre.currentData()
        mortalites = MortaliteController.get_mortalites_par_eleveur(code_filtre)
        self.table.setRowCount(len(mortalites))
        for i, m in enumerate(mortalites):
            self.table.setItem(i, 0, QTableWidgetItem(str(m.id)))
            self.table.setItem(i, 1, QTableWidgetItem(m.code_elevage))
            self.table.setItem(i, 2, QTableWidgetItem(m.numero_boucle))
            self.table.setItem(i, 3, QTableWidgetItem(m.date_deces))
            self.table.setItem(i, 4, QTableWidgetItem(m.cause_deces))
            self.table.setItem(i, 5, QTableWidgetItem(m.remarque or ""))
        self.table.resizeColumnsToContents()

    def modifier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un enregistrement")
            return
        mort_id = int(self.table.item(row, 0).text())
        db = SessionLocal()
        mort = db.query(Mortalite).filter(Mortalite.id == mort_id).first()
        db.close()
        if not mort:
            QMessageBox.warning(self, "Erreur", "Mortalité introuvable")
            return
        dialog = ModifierMortaliteDialog(mort, self)
        if dialog.exec():
            data = dialog.get_data()
            ok, msg = MortaliteController.modifier_mortalite(mort_id, data)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", msg)

    def supprimer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un enregistrement")
            return
        mort_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette mortalité ? L'animal réapparaîtra.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = MortaliteController.supprimer_mortalite(mort_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", msg)