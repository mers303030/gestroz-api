from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox, QComboBox, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QDateEdit)
from PySide6.QtCore import QDate
from database.db_session import SessionLocal
from database.models.eleveur import Eleveur
from database.models.stock import Stock
from database.models.aliment_base import AlimentBase
from controllers.stock_controller import StockController

class ModifierStockDialog(QDialog):
    def __init__(self, stock, parent=None):
        super().__init__(parent)
        self.stock = stock
        self.setWindowTitle("Modifier stock")
        self.setModal(True)
        layout = QFormLayout(self)
        self.quantite = QLineEdit(str(stock.quantite_kg))
        self.prix_kg = QLineEdit(str(stock.prix_kg))
        self.origine = QComboBox()
        self.origine.addItems(["Exploitation", "Achat"])
        self.origine.setCurrentText(stock.origine)
        self.date_entree = QDateEdit()
        self.date_entree.setCalendarPopup(True)
        self.date_entree.setDate(QDate.fromString(stock.date_entree, "yyyy-MM-dd"))
        self.date_entree.setDisplayFormat("yyyy-MM-dd")
        self.observations = QLineEdit(stock.observations or "")
        layout.addRow("Quantité (kg):", self.quantite)
        layout.addRow("Prix (DH/kg):", self.prix_kg)
        layout.addRow("Origine:", self.origine)
        layout.addRow("Date entrée:", self.date_entree)
        layout.addRow("Observations:", self.observations)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    def get_data(self):
        return {
            'quantite_kg': float(self.quantite.text()) if self.quantite.text() else 0,
            'prix_kg': float(self.prix_kg.text()) if self.prix_kg.text() else 0,
            'origine': self.origine.currentText(),
            'date_entree': self.date_entree.date().toString("yyyy-MM-dd"),
            'observations': self.observations.text()
        }

class GestionStocksWindow(QWidget):
    def __init__(self, role=None, code_elevage=None, parent=None):
        super().__init__(parent)
        self.role = role
        self.code_elevage = code_elevage
        self.setWindowTitle("Gestion des stocks d'aliments")
        self.resize(1100, 500)
        layout = QVBoxLayout(self)

        # Filtre par éleveur (si l'utilisateur est admin ou technicien, on peut choisir un éleveur)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Éleveur:"))
        self.combo_filtre = QComboBox()
        self.combo_filtre.addItem("Tous", None)
        db = SessionLocal()
        eleveurs = db.query(Eleveur).all()
        for e in eleveurs:
            self.combo_filtre.addItem(f"{e.code_elevage} - {e.nom} {e.prenom}", e.code_elevage)
        db.close()
        self.combo_filtre.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.combo_filtre)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Éleveur", "Aliment", "Origine", "Quantité (kg)", "Prix (DH/kg)", "Date entrée", "UFL/kg", "PDI/kg"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.clicked.connect(self.load_data)
        btn_modifier = QPushButton("Modifier")
        btn_modifier.clicked.connect(self.modifier)
        btn_supprimer = QPushButton("Supprimer")
        btn_supprimer.clicked.connect(self.supprimer)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_modifier)
        btn_layout.addWidget(btn_supprimer)
        layout.addLayout(btn_layout)

        # Si l'utilisateur est un éleveur, on force le filtre sur son code et on désactive le combo
        if self.role == "eleveur" and self.code_elevage:
            # Trouver l'index du code dans le combo
            idx = self.combo_filtre.findData(self.code_elevage)
            if idx >= 0:
                self.combo_filtre.setCurrentIndex(idx)
            self.combo_filtre.setEnabled(False)

        self.load_data()

    def load_data(self):
        code_filtre = self.combo_filtre.currentData()
        # Si l'utilisateur est éleveur, on ignore le choix du combo et on filtre par son code
        if self.role == "eleveur" and self.code_elevage:
            code_filtre = self.code_elevage
        stocks = StockController.get_stocks_par_eleveur(code_filtre)
        db = SessionLocal()
        self.table.setRowCount(len(stocks))
        for i, s in enumerate(stocks):
            aliment = db.query(AlimentBase).filter(AlimentBase.id == s.aliment_base_id).first()
            nom_aliment = aliment.nom if aliment else "?"
            ufl = aliment.ufl if aliment else 0
            pdi = aliment.pdi if aliment else 0
            self.table.setItem(i, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(i, 1, QTableWidgetItem(s.code_elevage))
            self.table.setItem(i, 2, QTableWidgetItem(nom_aliment))
            self.table.setItem(i, 3, QTableWidgetItem(s.origine or ""))
            self.table.setItem(i, 4, QTableWidgetItem(str(s.quantite_kg)))
            self.table.setItem(i, 5, QTableWidgetItem(str(s.prix_kg)))
            self.table.setItem(i, 6, QTableWidgetItem(s.date_entree))
            self.table.setItem(i, 7, QTableWidgetItem(f"{ufl:.2f}"))
            self.table.setItem(i, 8, QTableWidgetItem(f"{pdi:.0f}"))
        self.table.resizeColumnsToContents()
        db.close()

    def modifier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un stock")
            return
        stock_id = int(self.table.item(row, 0).text())
        db = SessionLocal()
        stock = db.query(Stock).filter(Stock.id == stock_id).first()
        db.close()
        if not stock:
            return
        dialog = ModifierStockDialog(stock, self)
        if dialog.exec():
            data = dialog.get_data()
            ok, msg = StockController.modifier_stock(stock_id, data)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", msg)

    def supprimer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un stock")
            return
        stock_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirmation", "Supprimer ce lot ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = StockController.supprimer_stock(stock_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", msg)