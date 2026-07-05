from PySide6.QtWidgets import (QWidget, QFormLayout, QComboBox, QLineEdit,
                               QPushButton, QMessageBox, QDateEdit, QLabel, QHBoxLayout)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from controllers.stock_controller import StockController
from controllers.aliment_base_controller import AlimentBaseController
from ui.widgets.eleveur_selector import EleveurSelector

class AjoutStockWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un lot d'aliment (stock)")
        self.setFixedSize(550, 600)
        layout = QFormLayout(self)

        self.eleveur_selector = EleveurSelector()
        self.combo_aliment_base = QComboBox()
        self.load_aliments_base()
        self.combo_aliment_base.currentIndexChanged.connect(self.afficher_valeurs)

        self.combo_origine = QComboBox()
        self.combo_origine.addItems(["Exploitation", "Achat"])

        self.label_ufl = QLabel("UFL : --")
        self.label_pdi = QLabel("PDI : --")
        self.quantite = QLineEdit()
        self.prix_kg = QLineEdit()
        self.date_entree = QDateEdit()
        self.date_entree.setCalendarPopup(True)
        self.date_entree.setDate(QDate.currentDate())
        self.date_entree.setDisplayFormat("yyyy-MM-dd")
        self.observations = QLineEdit()

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Enregistrer")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_close)

        layout.addRow("Éleveur", self.eleveur_selector)
        layout.addRow("Aliment", self.combo_aliment_base)
        layout.addRow("Origine", self.combo_origine)
        layout.addRow("Valeurs nutritives", self.label_ufl)
        layout.addRow("", self.label_pdi)
        layout.addRow("Quantité (kg)", self.quantite)
        layout.addRow("Prix unitaire (DH/kg)", self.prix_kg)
        layout.addRow("Date d'entrée", self.date_entree)
        layout.addRow("Observations", self.observations)
        layout.addRow(btn_layout)

        self.afficher_valeurs()

    def load_aliments_base(self):
        aliments_par_cat = AlimentBaseController.get_by_categorie()
        model = QStandardItemModel()
        ordre_cat = ["Pailles", "Grains", "Ensilage", "Pulpes", "Autres"]
        for cat in ordre_cat:
            if cat in aliments_par_cat:
                aliments = aliments_par_cat[cat]
                cat_item = QStandardItem(cat)
                cat_item.setSelectable(False)
                font = cat_item.font()
                font.setBold(True)
                cat_item.setFont(font)
                model.appendRow(cat_item)
                for a in aliments:
                    item = QStandardItem(a.nom)
                    item.setData(a.id, Qt.UserRole)
                    model.appendRow(item)
        self.combo_aliment_base.setModel(model)
        self.combo_aliment_base.setCurrentIndex(-1)

    def afficher_valeurs(self):
        idx = self.combo_aliment_base.currentIndex()
        if idx >= 0:
            aliment_id = self.combo_aliment_base.itemData(idx, Qt.UserRole)
            if aliment_id:
                db = SessionLocal()
                a = db.query(AlimentBase).filter(AlimentBase.id == aliment_id).first()
                if a:
                    self.label_ufl.setText(f"UFL : {a.ufl:.2f} / kg MS")
                    self.label_pdi.setText(f"PDI : {a.pdi:.0f} g/kg MS")
                db.close()
                return
        self.label_ufl.setText("UFL : --")
        self.label_pdi.setText("PDI : --")

    def enregistrer(self):
        code = self.eleveur_selector.get_code()
        if not code:
            QMessageBox.warning(self, "Erreur", "Éleveur non reconnu")
            return
        if self.combo_aliment_base.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un aliment")
            return
        aliment_id = self.combo_aliment_base.itemData(self.combo_aliment_base.currentIndex(), Qt.UserRole)
        if not aliment_id:
            QMessageBox.warning(self, "Erreur", "Aliment invalide")
            return
        if not self.quantite.text().strip():
            QMessageBox.warning(self, "Erreur", "La quantité est obligatoire")
            return
        if not self.prix_kg.text().strip():
            QMessageBox.warning(self, "Erreur", "Le prix unitaire est obligatoire")
            return
        try:
            quantite = float(self.quantite.text())
            prix = float(self.prix_kg.text())
            if quantite <= 0 or prix <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Erreur", "Quantité et prix doivent être des nombres positifs")
            return

        data = {
            'code_elevage': code,
            'aliment_base_id': aliment_id,
            'quantite_kg': quantite,
            'prix_kg': prix,
            'date_entree': self.date_entree.date().toString("yyyy-MM-dd"),
            'origine': self.combo_origine.currentText(),
            'observations': self.observations.text(),
        }
        ok, msg = StockController.ajouter_stock(data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.quantite.clear()
            self.prix_kg.clear()
            self.observations.clear()
        else:
            QMessageBox.warning(self, "Erreur", msg)