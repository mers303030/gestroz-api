# ui/windows/saisie_consultation_stock.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Aliment, MouvementStock

class SaisieConsultationStockWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation du stock d'aliments")
        self.resize(1100, 750)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE ====================
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.setPlaceholderText("Code élevage")
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        # Aliment : combo ÉDITABLE (choix ou saisie)
        self.aliment_combo = QComboBox()
        self.aliment_combo.setEditable(True)
        self.aliment_combo.setEnabled(False)
        self.aliment_combo.setPlaceholderText("Choisissez ou tapez un aliment")
        form_layout.addRow(QLabel("Aliment :"), self.aliment_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Stockage (entrée)", "Sortie vers animaux"])
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
        self.prix_edit.setRange(0, 10000)
        self.prix_edit.setSingleStep(0.01)
        self.prix_edit.setSuffix(" DH/kg")
        form_layout.addRow(QLabel("Prix unitaire :"), self.prix_edit)

        self.fournisseur_edit = QLineEdit()
        self.fournisseur_edit.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Fournisseur :"), self.fournisseur_edit)

        self.observations_edit = QLineEdit()
        self.observations_edit.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Observations :"), self.observations_edit)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.nouveau)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        form_layout.addRow(btn_layout)

        layout.addWidget(form_group)

        # Séparateur
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Type", "Aliment",
                                              "Qté (kg)", "Prix (DH/kg)", "Fournisseur", "Obs."])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.charger_selection)
        layout.addWidget(self.table)

        # Stock actuel
        stock_layout = QHBoxLayout()
        stock_layout.addWidget(QLabel("Stock actuel :"))
        self.stock_label = QLabel("0.00 kg")
        self.stock_label.setStyleSheet("font-weight: bold; color: #d4af37;")
        stock_layout.addWidget(self.stock_label)
        stock_layout.addStretch()
        layout.addLayout(stock_layout)

        self.current_id = None
        self.load_table()
        self.on_eleveur_changed()

    # ==================== MÉTHODES ====================
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
        self.load_table()
        self.mettre_a_jour_stock()

        if not code:
            return

        db = SessionLocal()
        try:
            aliments = db.query(Aliment).filter(Aliment.code_elevage == code).order_by(Aliment.nom).all()
            for a in aliments:
                self.aliment_combo.addItem(a.nom, a.id)
            self.aliment_combo.setEnabled(True)
        finally:
            db.close()

    def _get_or_create_aliment(self, nom, code):
        """Retourne l'ID de l'aliment. Crée l'aliment s'il n'existe pas."""
        db = SessionLocal()
        try:
            aliment = db.query(Aliment).filter(
                Aliment.code_elevage == code,
                Aliment.nom == nom
            ).first()
            if aliment:
                return aliment.id

            # Création avec valeurs par défaut
            nouvel = Aliment(
                code_elevage=code,
                nom=nom,
                type_aliment="Autre",
                matiere_seche=0.0,
                prix_kg=0.0,
                ufl=0.0,
                ufv=0.0,
                pdi=0.0
            )
            db.add(nouvel)
            db.commit()

            # Mettre à jour la combo
            self.aliment_combo.clear()
            aliments = db.query(Aliment).filter(Aliment.code_elevage == code).order_by(Aliment.nom).all()
            for a in aliments:
                self.aliment_combo.addItem(a.nom, a.id)
            self.aliment_combo.setCurrentText(nom)
            return nouvel.id
        finally:
            db.close()

    def mettre_a_jour_stock(self):
        aliment_id = self.aliment_combo.currentData()
        code = self.code_combo.currentText().strip()
        if not aliment_id or not code:
            self.stock_label.setText("0.00 kg")
            return

        db = SessionLocal()
        try:
            entrees = db.query(MouvementStock).filter(
                MouvementStock.aliment_id == aliment_id,
                MouvementStock.code_elevage == code,
                MouvementStock.type == "entree"
            ).all()
            sorties = db.query(MouvementStock).filter(
                MouvementStock.aliment_id == aliment_id,
                MouvementStock.code_elevage == code,
                MouvementStock.type == "sortie"
            ).all()
            total_entrees = sum(m.quantite for m in entrees) or 0
            total_sorties = sum(m.quantite for m in sorties) or 0
            self.stock_label.setText(f"{total_entrees - total_sorties:.2f} kg")
        finally:
            db.close()

    def load_table(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            mouvements = db.query(MouvementStock).filter(
                MouvementStock.code_elevage == code
            ).order_by(MouvementStock.date_mouvement.desc()).all()
        finally:
            db.close()

        self.table.setRowCount(len(mouvements))
        for i, m in enumerate(mouvements):
            aliment = db.query(Aliment).filter(Aliment.id == m.aliment_id).first()
            self.table.setItem(i, 0, QTableWidgetItem(str(m.id)))
            self.table.setItem(i, 1, QTableWidgetItem(m.date_mouvement))
            self.table.setItem(i, 2, QTableWidgetItem("Stockage" if m.type == "entree" else "Sortie"))
            self.table.setItem(i, 3, QTableWidgetItem(aliment.nom if aliment else ""))
            self.table.setItem(i, 4, QTableWidgetItem(f"{m.quantite:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{m.prix_unitaire:.2f}" if m.prix_unitaire else ""))
            self.table.setItem(i, 6, QTableWidgetItem(m.fournisseur or ""))
            self.table.setItem(i, 7, QTableWidgetItem(m.remarque or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.date_mouvement.setDate(QDate.fromString(self.table.item(row, 1).text(), "yyyy-MM-dd"))
        self.type_combo.setCurrentText(self.table.item(row, 2).text())
        nom_aliment = self.table.item(row, 3).text()
        for i in range(self.aliment_combo.count()):
            if self.aliment_combo.itemText(i) == nom_aliment:
                self.aliment_combo.setCurrentIndex(i)
                break
        self.quantite_edit.setValue(float(self.table.item(row, 4).text()))
        prix_text = self.table.item(row, 5).text()
        self.prix_edit.setValue(float(prix_text) if prix_text else 0)
        self.fournisseur_edit.setText(self.table.item(row, 6).text())
        self.observations_edit.setText(self.table.item(row, 7).text())
        self.btn_save.setText("Mettre à jour")
        self.mettre_a_jour_stock()

    def nouveau(self):
        self.current_id = None
        self.aliment_combo.setCurrentIndex(-1)
        self.type_combo.setCurrentIndex(0)
        self.date_mouvement.setDate(QDate.currentDate())
        self.quantite_edit.setValue(0)
        self.prix_edit.setValue(0)
        self.fournisseur_edit.clear()
        self.observations_edit.clear()
        self.btn_save.setText("Sauvegarder")
        self.mettre_a_jour_stock()

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        nom_aliment = self.aliment_combo.currentText().strip()
        if not nom_aliment:
            QMessageBox.warning(self, "Erreur", "Saisissez ou choisissez un aliment.")
            return

        aliment_id = self._get_or_create_aliment(nom_aliment, code)
        if aliment_id is None:
            return

        if self.quantite_edit.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Quantité positive requise.")
            return

        type_mvt = "entree" if self.type_combo.currentText() == "Stockage (entrée)" else "sortie"
        date_mvt = self.date_mouvement.date().toString("yyyy-MM-dd")
        quantite = self.quantite_edit.value()
        prix = self.prix_edit.value() if self.prix_edit.value() > 0 else None
        fournisseur = self.fournisseur_edit.text().strip() or None
        obs = self.observations_edit.text().strip() or None

        db = SessionLocal()
        try:
            if self.current_id is None:
                mvt = MouvementStock(
                    code_elevage=code,
                    aliment_id=aliment_id,
                    date_mouvement=date_mvt,
                    type=type_mvt,
                    quantite=quantite,
                    prix_unitaire=prix,
                    fournisseur=fournisseur,
                    remarque=obs
                )
                db.add(mvt)
            else:
                mvt = db.query(MouvementStock).filter(MouvementStock.id == self.current_id).first()
                if mvt:
                    mvt.aliment_id = aliment_id
                    mvt.date_mouvement = date_mvt
                    mvt.type = type_mvt
                    mvt.quantite = quantite
                    mvt.prix_unitaire = prix
                    mvt.fournisseur = fournisseur
                    mvt.remarque = obs
                else:
                    QMessageBox.warning(self, "Erreur", "Mouvement introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Mouvement enregistré.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un mouvement.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        db = SessionLocal()
        try:
            mvt = db.query(MouvementStock).filter(MouvementStock.id == self.current_id).first()
            if mvt:
                db.delete(mvt)
                db.commit()
                self.load_table()
                self.nouveau()
            else:
                QMessageBox.warning(self, "Erreur", "Mouvement introuvable.")
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()