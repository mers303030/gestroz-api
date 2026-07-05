from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox, QComboBox, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QDateEdit)
from PySide6.QtCore import QDate
from database.db_session import SessionLocal
from database.models.eleveur import Eleveur
from database.models.vente import Vente
from controllers.vente_controller import VenteController

class ModifierVenteDialog(QDialog):
    def __init__(self, vente, parent=None):
        super().__init__(parent)
        self.vente = vente
        self.setWindowTitle("Modifier vente")
        self.setModal(True)
        layout = QFormLayout(self)
        self.numero_boucle = QLineEdit(vente.numero_boucle)
        self.date_vente = QDateEdit()
        self.date_vente.setCalendarPopup(True)
        self.date_vente.setDate(QDate.fromString(vente.date_vente, "yyyy-MM-dd"))
        self.date_vente.setDisplayFormat("yyyy-MM-dd")
        self.prix_vente = QLineEdit(str(vente.prix_vente))
        self.lieu_vente = QLineEdit(vente.lieu_vente)
        self.poids_vente = QLineEdit(str(vente.poids_vente) if vente.poids_vente else "")
        self.remarque = QLineEdit(vente.remarque or "")
        layout.addRow("Numéro boucle:", self.numero_boucle)
        layout.addRow("Date vente:", self.date_vente)
        layout.addRow("Prix (DH):", self.prix_vente)
        layout.addRow("Lieu:", self.lieu_vente)
        layout.addRow("Poids (kg):", self.poids_vente)
        layout.addRow("Remarque:", self.remarque)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    def get_data(self):
        return {
            'numero_boucle': self.numero_boucle.text(),
            'date_vente': self.date_vente.date().toString("yyyy-MM-dd"),
            'prix_vente': float(self.prix_vente.text()) if self.prix_vente.text() else 0,
            'lieu_vente': self.lieu_vente.text(),
            'poids_vente': float(self.poids_vente.text()) if self.poids_vente.text() else None,
            'remarque': self.remarque.text()
        }

class GestionVentesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des ventes")
        self.resize(1100, 600)
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Éleveur", "Boucle", "Date vente", "Prix (DH)", "Lieu", "Poids (kg)"])
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
        ventes = VenteController.get_ventes_par_eleveur(code_filtre)
        self.table.setRowCount(len(ventes))
        for i, v in enumerate(ventes):
            self.table.setItem(i, 0, QTableWidgetItem(str(v.id)))
            self.table.setItem(i, 1, QTableWidgetItem(v.code_elevage))
            self.table.setItem(i, 2, QTableWidgetItem(v.numero_boucle))
            self.table.setItem(i, 3, QTableWidgetItem(v.date_vente))
            self.table.setItem(i, 4, QTableWidgetItem(str(v.prix_vente)))
            self.table.setItem(i, 5, QTableWidgetItem(v.lieu_vente))
            self.table.setItem(i, 6, QTableWidgetItem(str(v.poids_vente) if v.poids_vente else ""))
        self.table.resizeColumnsToContents()

    def modifier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez une vente")
            return
        vente_id = int(self.table.item(row, 0).text())
        db = SessionLocal()
        vente = db.query(Vente).filter(Vente.id == vente_id).first()
        db.close()
        if not vente:
            QMessageBox.warning(self, "Erreur", "Vente introuvable")
            return
        dialog = ModifierVenteDialog(vente, self)
        if dialog.exec():
            data = dialog.get_data()
            ok, msg = VenteController.modifier_vente(vente_id, data)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", msg)

    def supprimer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez une vente")
            return
        vente_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette vente ? L'animal réapparaîtra.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = VenteController.supprimer_vente(vente_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", msg)