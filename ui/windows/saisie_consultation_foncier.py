# ui/windows/saisie_consultation_foncier.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Parcelle

class SaisieConsultationFoncierWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation du capital foncier")
        self.resize(1100, 700)
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

        # Numéro ou nom de la parcelle
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Numéro ou nom de la parcelle")
        form_layout.addRow(QLabel("Nom / Numéro :"), self.nom_edit)

        # Statut foncier
        self.statut_combo = QComboBox()
        self.statut_combo.addItems(["", "Melk", "Location", "Offre provisoire", "Autre"])
        form_layout.addRow(QLabel("Statut foncier :"), self.statut_combo)

        # Superficie
        self.surface_edit = QDoubleSpinBox()
        self.surface_edit.setRange(0, 10000)
        self.surface_edit.setSingleStep(0.5)
        self.surface_edit.setSuffix(" ha")
        form_layout.addRow(QLabel("Superficie (ha) :"), self.surface_edit)

        # Occupation (année en cours)
        self.occupation_edit = QLineEdit()
        self.occupation_edit.setPlaceholderText("Occupation actuelle (ex: blé, prairie, ...)")
        form_layout.addRow(QLabel("Occupation actuelle :"), self.occupation_edit)

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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Statut", "Superficie (ha)", "Occupation", "Observations"
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

    def on_eleveur_changed(self):
        self.load_table()
        self.nouveau()

    def load_table(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            parcelles = db.query(Parcelle).filter(Parcelle.code_elevage == code).all()
        finally:
            db.close()

        self.table.setRowCount(len(parcelles))
        for i, p in enumerate(parcelles):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(p.numero_parcelle or ""))
            self.table.setItem(i, 2, QTableWidgetItem(p.statut_foncier or ""))
            self.table.setItem(i, 3, QTableWidgetItem(f"{p.surface_ha:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(p.occupation_actuelle or ""))
            self.table.setItem(i, 5, QTableWidgetItem(p.observations or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.nom_edit.setText(self.table.item(row, 1).text())
        self.statut_combo.setCurrentText(self.table.item(row, 2).text())
        self.surface_edit.setValue(float(self.table.item(row, 3).text()))
        self.occupation_edit.setText(self.table.item(row, 4).text())
        self.obs_edit.setText(self.table.item(row, 5).text())
        self.btn_save.setText("Mettre à jour")

    def nouveau(self):
        self.current_id = None
        self.nom_edit.clear()
        self.statut_combo.setCurrentIndex(0)
        self.surface_edit.setValue(0)
        self.occupation_edit.clear()
        self.obs_edit.clear()
        self.btn_save.setText("Sauvegarder")

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        nom = self.nom_edit.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de la parcelle est obligatoire.")
            return

        surface = self.surface_edit.value()
        if surface <= 0:
            QMessageBox.warning(self, "Erreur", "La superficie doit être positive.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                parcelle = Parcelle(
                    code_elevage=code,
                    numero_parcelle=nom,
                    surface_ha=surface,
                    statut_foncier=self.statut_combo.currentText() or None,
                    occupation_actuelle=self.occupation_edit.text().strip() or None,
                    observations=self.obs_edit.text().strip() or None
                )
                db.add(parcelle)
            else:
                parcelle = db.query(Parcelle).filter(Parcelle.id == self.current_id).first()
                if parcelle:
                    parcelle.numero_parcelle = nom
                    parcelle.surface_ha = surface
                    parcelle.statut_foncier = self.statut_combo.currentText() or None
                    parcelle.occupation_actuelle = self.occupation_edit.text().strip() or None
                    parcelle.observations = self.obs_edit.text().strip() or None
                else:
                    QMessageBox.warning(self, "Erreur", "Parcelle introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Parcelle enregistrée.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une parcelle.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette parcelle ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                parcelle = db.query(Parcelle).filter(Parcelle.id == self.current_id).first()
                if parcelle:
                    db.delete(parcelle)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Parcelle supprimée.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Parcelle introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()