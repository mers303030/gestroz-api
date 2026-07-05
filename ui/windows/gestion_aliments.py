# ui/windows/gestion_aliments.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Aliment

class GestionAlimentsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des aliments")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE ====================
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

        # Nom
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom de l'aliment")
        form_layout.addRow(QLabel("Nom :"), self.nom_edit)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Concentré", "Fourrage", "Minéral", "Autre"])
        form_layout.addRow(QLabel("Type :"), self.type_combo)

        # Matière sèche (%)
        self.ms_edit = QDoubleSpinBox()
        self.ms_edit.setRange(0, 100)
        self.ms_edit.setSingleStep(0.5)
        self.ms_edit.setSuffix(" %")
        self.ms_edit.setValue(0)
        form_layout.addRow(QLabel("Matière sèche :"), self.ms_edit)

        # Prix / kg
        self.prix_edit = QDoubleSpinBox()
        self.prix_edit.setRange(0, 1000)
        self.prix_edit.setSingleStep(0.01)
        self.prix_edit.setSuffix(" DH/kg")
        self.prix_edit.setValue(0)
        form_layout.addRow(QLabel("Prix (DH/kg) :"), self.prix_edit)

        # UFL
        self.ufl_edit = QDoubleSpinBox()
        self.ufl_edit.setRange(0, 10)
        self.ufl_edit.setSingleStep(0.01)
        self.ufl_edit.setSuffix(" UFL")
        self.ufl_edit.setValue(0)
        form_layout.addRow(QLabel("UFL :"), self.ufl_edit)

        # UFV
        self.ufv_edit = QDoubleSpinBox()
        self.ufv_edit.setRange(0, 10)
        self.ufv_edit.setSingleStep(0.01)
        self.ufv_edit.setSuffix(" UFV")
        self.ufv_edit.setValue(0)
        form_layout.addRow(QLabel("UFV :"), self.ufv_edit)

        # PDI
        self.pdi_edit = QDoubleSpinBox()
        self.pdi_edit.setRange(0, 500)
        self.pdi_edit.setSingleStep(0.5)
        self.pdi_edit.setSuffix(" g/kg MS")
        self.pdi_edit.setValue(0)
        form_layout.addRow(QLabel("PDI :"), self.pdi_edit)

        # Boutons
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

        # Séparateur
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # ==================== TABLEAU ====================
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Type", "MS %", "Prix DH/kg", "UFL", "UFV", "PDI"
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
            aliments = db.query(Aliment).filter(Aliment.code_elevage == code).all()
        finally:
            db.close()

        self.table.setRowCount(len(aliments))
        for i, a in enumerate(aliments):
            self.table.setItem(i, 0, QTableWidgetItem(str(a.id)))
            self.table.setItem(i, 1, QTableWidgetItem(a.nom))
            self.table.setItem(i, 2, QTableWidgetItem(a.type_aliment or ""))
            self.table.setItem(i, 3, QTableWidgetItem(f"{a.matiere_seche:.1f}" if a.matiere_seche else ""))
            self.table.setItem(i, 4, QTableWidgetItem(f"{a.prix_kg:.2f}" if a.prix_kg else ""))
            self.table.setItem(i, 5, QTableWidgetItem(f"{a.ufl:.2f}" if a.ufl else ""))
            self.table.setItem(i, 6, QTableWidgetItem(f"{a.ufv:.2f}" if a.ufv else ""))
            self.table.setItem(i, 7, QTableWidgetItem(f"{a.pdi:.1f}" if a.pdi else ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.nom_edit.setText(self.table.item(row, 1).text())
        self.type_combo.setCurrentText(self.table.item(row, 2).text())
        self.ms_edit.setValue(float(self.table.item(row, 3).text()) if self.table.item(row, 3).text() else 0)
        self.prix_edit.setValue(float(self.table.item(row, 4).text()) if self.table.item(row, 4).text() else 0)
        self.ufl_edit.setValue(float(self.table.item(row, 5).text()) if self.table.item(row, 5).text() else 0)
        self.ufv_edit.setValue(float(self.table.item(row, 6).text()) if self.table.item(row, 6).text() else 0)
        self.pdi_edit.setValue(float(self.table.item(row, 7).text()) if self.table.item(row, 7).text() else 0)
        self.btn_save.setText("Mettre à jour")

    def nouveau(self):
        self.current_id = None
        self.nom_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.ms_edit.setValue(0)
        self.prix_edit.setValue(0)
        self.ufl_edit.setValue(0)
        self.ufv_edit.setValue(0)
        self.pdi_edit.setValue(0)
        self.btn_save.setText("Sauvegarder")

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        nom = self.nom_edit.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                aliment = Aliment(
                    code_elevage=code,
                    nom=nom,
                    type_aliment=self.type_combo.currentText(),
                    matiere_seche=self.ms_edit.value(),
                    prix_kg=self.prix_edit.value(),
                    ufl=self.ufl_edit.value(),
                    ufv=self.ufv_edit.value(),
                    pdi=self.pdi_edit.value()
                )
                db.add(aliment)
            else:
                aliment = db.query(Aliment).filter(Aliment.id == self.current_id).first()
                if aliment:
                    aliment.nom = nom
                    aliment.type_aliment = self.type_combo.currentText()
                    aliment.matiere_seche = self.ms_edit.value()
                    aliment.prix_kg = self.prix_edit.value()
                    aliment.ufl = self.ufl_edit.value()
                    aliment.ufv = self.ufv_edit.value()
                    aliment.pdi = self.pdi_edit.value()
                else:
                    QMessageBox.warning(self, "Erreur", "Aliment introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Aliment enregistré.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un aliment.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet aliment ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                aliment = db.query(Aliment).filter(Aliment.id == self.current_id).first()
                if aliment:
                    db.delete(aliment)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Aliment supprimé.")
                    self.load_table()
                    self.nouveau()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()