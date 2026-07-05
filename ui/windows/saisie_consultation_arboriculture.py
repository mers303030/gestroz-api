# ui/windows/saisie_consultation_arboriculture.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Parcelle, Arbre

class SaisieConsultationArboricultureWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation de l'arboriculture")
        self.resize(1200, 700)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE (HAUT) ====================
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        # Code élevage
        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.setPlaceholderText("Sélectionnez ou tapez un code élevage")
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        # Parcelle
        self.parcelle_combo = QComboBox()
        self.parcelle_combo.setEnabled(False)
        form_layout.addRow(QLabel("Parcelle :"), self.parcelle_combo)

        # Espèce / Arbre
        self.espece_edit = QLineEdit()
        self.espece_edit.setPlaceholderText("Olivier, Amandier, Pommier, ...")
        form_layout.addRow(QLabel("Espèce :"), self.espece_edit)

        # Nombre d'arbres
        self.nb_arbres = QSpinBox()
        self.nb_arbres.setRange(0, 100000)
        self.nb_arbres.setSingleStep(1)
        self.nb_arbres.setSuffix(" arbres")
        form_layout.addRow(QLabel("Nombre d'arbres :"), self.nb_arbres)

        # Destination
        self.destination_combo = QComboBox()
        self.destination_combo.addItems(["", "Vente", "Consommation"])
        self.destination_combo.currentTextChanged.connect(self.on_destination_changed)
        form_layout.addRow(QLabel("Destination :"), self.destination_combo)

        # Récolte N-1 (kg/arbre)
        self.recolte_edit = QDoubleSpinBox()
        self.recolte_edit.setRange(0, 1000)
        self.recolte_edit.setSingleStep(0.5)
        self.recolte_edit.setSuffix(" kg/arbre")
        form_layout.addRow(QLabel("Récolte N-1 (kg/arbre) :"), self.recolte_edit)

        # Quantité vendue (kg)
        self.qte_vendue = QDoubleSpinBox()
        self.qte_vendue.setRange(0, 100000)
        self.qte_vendue.setSingleStep(1)
        self.qte_vendue.setSuffix(" kg")
        self.qte_vendue.setEnabled(False)
        form_layout.addRow(QLabel("Quantité vendue (kg) :"), self.qte_vendue)

        # Prix de vente (DH/kg)
        self.prix_vente = QDoubleSpinBox()
        self.prix_vente.setRange(0, 1000)
        self.prix_vente.setSingleStep(0.01)
        self.prix_vente.setSuffix(" DH/kg")
        self.prix_vente.setEnabled(False)
        form_layout.addRow(QLabel("Prix de vente (DH/kg) :"), self.prix_vente)

        # Observations
        self.obs_edit = QLineEdit()
        self.obs_edit.setPlaceholderText("Observations (optionnel)")
        form_layout.addRow(QLabel("Observations :"), self.obs_edit)

        # ==================== BOUTONS ====================
        form_btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.nouveau)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)

        form_btn_layout.addWidget(self.btn_new)
        form_btn_layout.addWidget(self.btn_save)
        form_btn_layout.addWidget(self.btn_delete)
        form_btn_layout.addStretch()
        form_btn_layout.addWidget(self.btn_close)
        form_layout.addRow(form_btn_layout)

        layout.addWidget(form_group)

        # ==================== SÉPARATEUR ====================
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # ==================== TABLEAU (BAS) ====================
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Parcelle", "Espèce", "Nb arbres",
            "Destination", "Récolte (kg/arbre)",
            "Qté vendue (kg)", "Prix (DH/kg)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.charger_selection)
        layout.addWidget(self.table)

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

    def on_destination_changed(self):
        """Active/désactive les champs de vente selon la destination."""
        is_vente = (self.destination_combo.currentText() == "Vente")
        self.qte_vendue.setEnabled(is_vente)
        self.prix_vente.setEnabled(is_vente)
        if not is_vente:
            self.qte_vendue.setValue(0)
            self.prix_vente.setValue(0)

    def on_eleveur_changed(self):
        code = self.code_combo.currentText().strip()
        self.parcelle_combo.clear()
        self.parcelle_combo.setEnabled(False)
        self.load_table()

        if not code:
            return

        db = SessionLocal()
        try:
            parcelles = db.query(Parcelle).filter(Parcelle.code_elevage == code).all()
            for p in parcelles:
                self.parcelle_combo.addItem(f"{p.numero_parcelle} ({p.surface_ha} ha)", p.id)
            self.parcelle_combo.setEnabled(len(parcelles) > 0)
        finally:
            db.close()

    def load_table(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            arbres = db.query(Arbre).filter(Arbre.code_elevage == code).all()
        finally:
            db.close()

        self.table.setRowCount(len(arbres))
        for i, a in enumerate(arbres):
            # Récupérer le nom de la parcelle
            parcelle_nom = ""
            if a.parcelle_id:
                db2 = SessionLocal()
                try:
                    p = db2.query(Parcelle).filter(Parcelle.id == a.parcelle_id).first()
                    if p:
                        parcelle_nom = p.numero_parcelle
                finally:
                    db2.close()

            self.table.setItem(i, 0, QTableWidgetItem(str(a.id)))
            self.table.setItem(i, 1, QTableWidgetItem(parcelle_nom))
            self.table.setItem(i, 2, QTableWidgetItem(a.espece or ""))
            self.table.setItem(i, 3, QTableWidgetItem(f"{a.nombre_arbres:.0f}" if a.nombre_arbres else ""))
            self.table.setItem(i, 4, QTableWidgetItem(a.destination or ""))
            self.table.setItem(i, 5, QTableWidgetItem(f"{a.rendement_kg_arbre:.1f}" if a.rendement_kg_arbre else ""))
            self.table.setItem(i, 6, QTableWidgetItem(f"{a.quantite_vendue_kg:.1f}" if a.quantite_vendue_kg else ""))
            self.table.setItem(i, 7, QTableWidgetItem(f"{a.prix_vente_kg:.2f}" if a.prix_vente_kg else ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())

        # Parcelle
        parcelle_nom = self.table.item(row, 1).text()
        for i in range(self.parcelle_combo.count()):
            if self.parcelle_combo.itemText(i).startswith(parcelle_nom):
                self.parcelle_combo.setCurrentIndex(i)
                break

        self.espece_edit.setText(self.table.item(row, 2).text())
        self.nb_arbres.setValue(float(self.table.item(row, 3).text()) if self.table.item(row, 3).text() else 0)
        self.destination_combo.setCurrentText(self.table.item(row, 4).text())
        self.recolte_edit.setValue(float(self.table.item(row, 5).text()) if self.table.item(row, 5).text() else 0)
        self.qte_vendue.setValue(float(self.table.item(row, 6).text()) if self.table.item(row, 6).text() else 0)
        self.prix_vente.setValue(float(self.table.item(row, 7).text()) if self.table.item(row, 7).text() else 0)
        self.obs_edit.setText("")
        self.btn_save.setText("Mettre à jour")
        self.on_destination_changed()

    def nouveau(self):
        self.current_id = None
        self.parcelle_combo.setCurrentIndex(-1)
        self.espece_edit.clear()
        self.nb_arbres.setValue(0)
        self.destination_combo.setCurrentIndex(0)
        self.recolte_edit.setValue(0)
        self.qte_vendue.setValue(0)
        self.prix_vente.setValue(0)
        self.obs_edit.clear()
        self.btn_save.setText("Sauvegarder")
        self.on_destination_changed()

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        parcelle_id = self.parcelle_combo.currentData()
        if not parcelle_id:
            QMessageBox.warning(self, "Erreur", "Choisissez une parcelle.")
            return

        espece = self.espece_edit.text().strip()
        if not espece:
            QMessageBox.warning(self, "Erreur", "L'espèce est obligatoire.")
            return

        if self.nb_arbres.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le nombre d'arbres doit être positif.")
            return

        destination = self.destination_combo.currentText()
        if not destination:
            QMessageBox.warning(self, "Erreur", "Choisissez une destination (Vente ou Consommation).")
            return

        # Vérifier les champs de vente si destination = Vente
        if destination == "Vente":
            if self.qte_vendue.value() <= 0:
                QMessageBox.warning(self, "Erreur", "La quantité vendue doit être positive.")
                return
            if self.prix_vente.value() <= 0:
                QMessageBox.warning(self, "Erreur", "Le prix de vente doit être positif.")
                return

        db = SessionLocal()
        try:
            if self.current_id is None:
                arbre = Arbre(
                    code_elevage=code,
                    parcelle_id=parcelle_id,
                    espece=espece,
                    nombre_arbres=self.nb_arbres.value(),
                    destination=destination,
                    rendement_kg_arbre=self.recolte_edit.value(),
                    quantite_vendue_kg=self.qte_vendue.value() if destination == "Vente" else 0,
                    prix_vente_kg=self.prix_vente.value() if destination == "Vente" else 0,
                    observations=self.obs_edit.text().strip() or None
                )
                db.add(arbre)
            else:
                arbre = db.query(Arbre).filter(Arbre.id == self.current_id).first()
                if arbre:
                    arbre.parcelle_id = parcelle_id
                    arbre.espece = espece
                    arbre.nombre_arbres = self.nb_arbres.value()
                    arbre.destination = destination
                    arbre.rendement_kg_arbre = self.recolte_edit.value()
                    arbre.quantite_vendue_kg = self.qte_vendue.value() if destination == "Vente" else 0
                    arbre.prix_vente_kg = self.prix_vente.value() if destination == "Vente" else 0
                    arbre.observations = self.obs_edit.text().strip() or None
                else:
                    QMessageBox.warning(self, "Erreur", "Enregistrement introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Enregistrement arboricole sauvegardé.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un enregistrement.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet enregistrement ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                arbre = db.query(Arbre).filter(Arbre.id == self.current_id).first()
                if arbre:
                    db.delete(arbre)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Enregistrement supprimé.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Enregistrement introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()