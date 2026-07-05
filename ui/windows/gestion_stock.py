# ui/windows/gestion_stock.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox,
                               QTabWidget)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Aliment, MouvementStock

class GestionStockWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion de stock - Alimentation")
        self.resize(1200, 700)
        layout = QVBoxLayout(self)

        # Onglets
        self.tabs = QTabWidget()
        self.tab_mouvements = QWidget()
        self.tab_stock = QWidget()
        self.tabs.addTab(self.tab_mouvements, "Mouvements")
        self.tabs.addTab(self.tab_stock, "Stock disponible")
        layout.addWidget(self.tabs)

        # ---- Onglet Mouvements ----
        form_group = QWidget()
        form_layout = QFormLayout(form_group)

        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.setPlaceholderText("Sélectionnez un code élevage")
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.aliment_combo = QComboBox()
        self.aliment_combo.setEnabled(False)
        form_layout.addRow(QLabel("Aliment :"), self.aliment_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["entree", "sortie"])
        form_layout.addRow(QLabel("Type :"), self.type_combo)

        self.date_mouvement = QDateEdit()
        self.date_mouvement.setCalendarPopup(True)
        self.date_mouvement.setDate(QDate.currentDate())
        self.date_mouvement.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date :"), self.date_mouvement)

        self.quantite_edit = QDoubleSpinBox()
        self.quantite_edit.setRange(0, 100000)
        self.quantite_edit.setSingleStep(1)
        self.quantite_edit.setSuffix(" kg")
        form_layout.addRow(QLabel("Quantité :"), self.quantite_edit)

        self.prix_edit = QDoubleSpinBox()
        self.prix_edit.setRange(0, 100000)
        self.prix_edit.setSingleStep(0.01)
        self.prix_edit.setSuffix(" DH")
        form_layout.addRow(QLabel("Prix unitaire :"), self.prix_edit)

        self.fournisseur_edit = QLineEdit()
        self.fournisseur_edit.setPlaceholderText("Nom du fournisseur (optionnel)")
        form_layout.addRow(QLabel("Fournisseur :"), self.fournisseur_edit)

        self.remarque_edit = QLineEdit()
        self.remarque_edit.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Remarque :"), self.remarque_edit)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Enregistrer le mouvement")
        self.btn_save.clicked.connect(self.enregistrer_mouvement)
        self.btn_refresh = QPushButton("Rafraîchir")
        self.btn_refresh.clicked.connect(self.load_mouvements)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        form_layout.addRow(btn_layout)

        self.table_mouvements = QTableWidget()
        self.table_mouvements.setColumnCount(6)
        self.table_mouvements.setHorizontalHeaderLabels([
            "Date", "Aliment", "Type", "Quantité", "Prix", "Fournisseur"
        ])
        self.table_mouvements.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_mouvements.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_mouvements.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_mouvements.setAlternatingRowColors(True)

        layout_mouvements = QVBoxLayout(self.tab_mouvements)
        layout_mouvements.addWidget(form_group)
        layout_mouvements.addWidget(self.table_mouvements)

        # ---- Onglet Stock ----
        self.table_stock = QTableWidget()
        self.table_stock.setColumnCount(4)
        self.table_stock.setHorizontalHeaderLabels([
            "Aliment", "Unité", "Stock initial", "Stock actuel"
        ])
        self.table_stock.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_stock.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_stock.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_stock.setAlternatingRowColors(True)

        layout_stock = QVBoxLayout(self.tab_stock)
        layout_stock.addWidget(self.table_stock)

        # Bouton Fermer en bas de la fenêtre (en plus de celui du formulaire)
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        btn_close_main = QPushButton("Fermer")
        btn_close_main.clicked.connect(self.close)
        close_layout.addWidget(btn_close_main)
        layout.addLayout(close_layout)

        self.current_id = None
        self.on_eleveur_changed()

    def get_all_codes(self):
        db = SessionLocal()
        try:
            return [e.code_elevage for e in db.query(Eleveur).all()]
        finally:
            db.close()

    def on_eleveur_changed(self):
        code = self.code_combo.currentText().strip()
        self.aliment_combo.clear()
        self.aliment_combo.setEnabled(False)
        self.load_mouvements()
        self.load_stock()

        if not code:
            return

        db = SessionLocal()
        try:
            aliments = db.query(Aliment).filter(Aliment.code_elevage == code).all()
            for a in aliments:
                self.aliment_combo.addItem(a.nom, a.id)
            self.aliment_combo.setEnabled(len(aliments) > 0)
        finally:
            db.close()

    def load_mouvements(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table_mouvements.setRowCount(0)
            return

        db = SessionLocal()
        try:
            mouvements = db.query(MouvementStock).filter(
                MouvementStock.code_elevage == code
            ).order_by(MouvementStock.date_mouvement.desc()).all()
        finally:
            db.close()

        self.table_mouvements.setRowCount(len(mouvements))
        for i, m in enumerate(mouvements):
            aliment = db.query(Aliment).filter(Aliment.id == m.aliment_id).first()
            self.table_mouvements.setItem(i, 0, QTableWidgetItem(m.date_mouvement))
            self.table_mouvements.setItem(i, 1, QTableWidgetItem(aliment.nom if aliment else ""))
            self.table_mouvements.setItem(i, 2, QTableWidgetItem(m.type))
            self.table_mouvements.setItem(i, 3, QTableWidgetItem(f"{m.quantite:.2f}"))
            self.table_mouvements.setItem(i, 4, QTableWidgetItem(f"{m.prix_unitaire:.2f}" if m.prix_unitaire else ""))
            self.table_mouvements.setItem(i, 5, QTableWidgetItem(m.fournisseur or ""))
        self.table_mouvements.resizeColumnsToContents()

    def load_stock(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table_stock.setRowCount(0)
            return

        db = SessionLocal()
        try:
            aliments = db.query(Aliment).filter(Aliment.code_elevage == code).all()
            lignes = []
            for a in aliments:
                entrees = db.query(MouvementStock).filter(
                    MouvementStock.aliment_id == a.id,
                    MouvementStock.type == "entree"
                )
                sorties = db.query(MouvementStock).filter(
                    MouvementStock.aliment_id == a.id,
                    MouvementStock.type == "sortie"
                )
                total_entrees = sum([m.quantite for m in entrees]) if entrees else 0
                total_sorties = sum([m.quantite for m in sorties]) if sorties else 0
                stock_actuel = a.stock_initial + total_entrees - total_sorties
                lignes.append((a.nom, a.unite, a.stock_initial, stock_actuel))
        finally:
            db.close()

        self.table_stock.setRowCount(len(lignes))
        for i, (nom, unite, stock_initial, stock_actuel) in enumerate(lignes):
            self.table_stock.setItem(i, 0, QTableWidgetItem(nom))
            self.table_stock.setItem(i, 1, QTableWidgetItem(unite))
            self.table_stock.setItem(i, 2, QTableWidgetItem(f"{stock_initial:.2f}"))
            self.table_stock.setItem(i, 3, QTableWidgetItem(f"{stock_actuel:.2f}"))
        self.table_stock.resizeColumnsToContents()

    def enregistrer_mouvement(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        aliment_id = self.aliment_combo.currentData()
        if not aliment_id:
            QMessageBox.warning(self, "Erreur", "Choisissez un aliment.")
            return

        if self.quantite_edit.value() <= 0:
            QMessageBox.warning(self, "Erreur", "La quantité doit être positive.")
            return

        db = SessionLocal()
        try:
            mouvement = MouvementStock(
                code_elevage=code,
                aliment_id=aliment_id,
                date_mouvement=self.date_mouvement.date().toString("yyyy-MM-dd"),
                type=self.type_combo.currentText(),
                quantite=self.quantite_edit.value(),
                prix_unitaire=self.prix_edit.value() if self.prix_edit.value() > 0 else None,
                fournisseur=self.fournisseur_edit.text().strip() or None,
                remarque=self.remarque_edit.text().strip() or None
            )
            db.add(mouvement)
            db.commit()
            QMessageBox.information(self, "Succès", "Mouvement enregistré.")
            self.load_mouvements()
            self.load_stock()
            self.quantite_edit.setValue(0)
            self.prix_edit.setValue(0)
            self.fournisseur_edit.clear()
            self.remarque_edit.clear()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()