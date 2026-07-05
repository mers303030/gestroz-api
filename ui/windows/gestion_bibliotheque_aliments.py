# ui/windows/gestion_bibliotheque_aliments.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import BibliothequeAliment

class GestionBibliothequeAlimentsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation de la bibliothèque d'aliments")
        self.resize(1200, 700)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE ====================
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom de l'aliment (ex: Orge, Luzerne, ...)")
        form_layout.addRow(QLabel("Nom :"), self.nom_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Fourrage", "Concentré", "Sous-produit", "Minéral", "Autre"])
        form_layout.addRow(QLabel("Type :"), self.type_combo)

        self.ms_edit = QDoubleSpinBox()
        self.ms_edit.setRange(0, 100)
        self.ms_edit.setSingleStep(0.5)
        self.ms_edit.setSuffix(" %")
        self.ms_edit.setValue(0)
        form_layout.addRow(QLabel("Matière sèche (%) :"), self.ms_edit)

        self.ufl_edit = QDoubleSpinBox()
        self.ufl_edit.setRange(0, 10)
        self.ufl_edit.setSingleStep(0.01)
        self.ufl_edit.setSuffix(" UFL")
        self.ufl_edit.setValue(0)
        form_layout.addRow(QLabel("UFL :"), self.ufl_edit)

        self.ufv_edit = QDoubleSpinBox()
        self.ufv_edit.setRange(0, 10)
        self.ufv_edit.setSingleStep(0.01)
        self.ufv_edit.setSuffix(" UFV")
        self.ufv_edit.setValue(0)
        form_layout.addRow(QLabel("UFV :"), self.ufv_edit)

        self.pdi_edit = QDoubleSpinBox()
        self.pdi_edit.setRange(0, 500)
        self.pdi_edit.setSingleStep(0.5)
        self.pdi_edit.setSuffix(" g/kg MS")
        self.pdi_edit.setValue(0)
        form_layout.addRow(QLabel("PDI :"), self.pdi_edit)

        self.ca_edit = QDoubleSpinBox()
        self.ca_edit.setRange(0, 100)
        self.ca_edit.setSingleStep(0.01)
        self.ca_edit.setSuffix(" %")
        self.ca_edit.setValue(0)
        form_layout.addRow(QLabel("Calcium (%) :"), self.ca_edit)

        self.p_edit = QDoubleSpinBox()
        self.p_edit.setRange(0, 100)
        self.p_edit.setSingleStep(0.01)
        self.p_edit.setSuffix(" %")
        self.p_edit.setValue(0)
        form_layout.addRow(QLabel("Phosphore (%) :"), self.p_edit)

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

        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # ==================== TABLEAU ====================
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # ID, Nom, Type, MS %, UFL, UFV, PDI, Ca %, P %
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Type", "MS %",
            "UFL", "UFV", "PDI", "Ca %", "P %"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.charger_selection)
        layout.addWidget(self.table)

        self.current_id = None
        self.load_table()
        self.nouveau()

    def load_table(self):
        db = SessionLocal()
        try:
            aliments = db.query(BibliothequeAliment).order_by(BibliothequeAliment.nom).all()
        finally:
            db.close()

        self.table.setRowCount(len(aliments))
        for i, a in enumerate(aliments):
            self.table.setItem(i, 0, QTableWidgetItem(str(a.id)))
            self.table.setItem(i, 1, QTableWidgetItem(a.nom))
            self.table.setItem(i, 2, QTableWidgetItem(a.type_aliment or ""))
            self.table.setItem(i, 3, QTableWidgetItem(f"{a.matiere_seche:.1f}" if a.matiere_seche else ""))
            self.table.setItem(i, 4, QTableWidgetItem(f"{a.ufl:.2f}" if a.ufl else ""))
            self.table.setItem(i, 5, QTableWidgetItem(f"{a.ufv:.2f}" if a.ufv else ""))
            self.table.setItem(i, 6, QTableWidgetItem(f"{a.pdi:.1f}" if a.pdi else ""))
            self.table.setItem(i, 7, QTableWidgetItem(f"{a.calcium:.2f}" if a.calcium else ""))
            self.table.setItem(i, 8, QTableWidgetItem(f"{a.phosphore:.2f}" if a.phosphore else ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.nom_edit.setText(self.table.item(row, 1).text())
        self.type_combo.setCurrentText(self.table.item(row, 2).text())
        self.ms_edit.setValue(float(self.table.item(row, 3).text()) if self.table.item(row, 3).text() else 0)
        self.ufl_edit.setValue(float(self.table.item(row, 4).text()) if self.table.item(row, 4).text() else 0)
        self.ufv_edit.setValue(float(self.table.item(row, 5).text()) if self.table.item(row, 5).text() else 0)
        self.pdi_edit.setValue(float(self.table.item(row, 6).text()) if self.table.item(row, 6).text() else 0)
        self.ca_edit.setValue(float(self.table.item(row, 7).text()) if self.table.item(row, 7).text() else 0)
        self.p_edit.setValue(float(self.table.item(row, 8).text()) if self.table.item(row, 8).text() else 0)
        self.btn_save.setText("Mettre à jour")

    def nouveau(self):
        self.current_id = None
        self.nom_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.ms_edit.setValue(0)
        self.ufl_edit.setValue(0)
        self.ufv_edit.setValue(0)
        self.pdi_edit.setValue(0)
        self.ca_edit.setValue(0)
        self.p_edit.setValue(0)
        self.btn_save.setText("Sauvegarder")

    def enregistrer(self):
        nom = self.nom_edit.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                existing = db.query(BibliothequeAliment).filter(BibliothequeAliment.nom == nom).first()
                if existing:
                    QMessageBox.warning(self, "Erreur", f"L'aliment '{nom}' existe déjà dans la bibliothèque.")
                    return
                aliment = BibliothequeAliment(
                    nom=nom,
                    type_aliment=self.type_combo.currentText(),
                    matiere_seche=self.ms_edit.value(),
                    ufl=self.ufl_edit.value(),
                    ufv=self.ufv_edit.value(),
                    pdi=self.pdi_edit.value(),
                    calcium=self.ca_edit.value(),
                    phosphore=self.p_edit.value()
                )
                db.add(aliment)
            else:
                aliment = db.query(BibliothequeAliment).filter(BibliothequeAliment.id == self.current_id).first()
                if aliment:
                    other = db.query(BibliothequeAliment).filter(
                        BibliothequeAliment.nom == nom,
                        BibliothequeAliment.id != self.current_id
                    ).first()
                    if other:
                        QMessageBox.warning(self, "Erreur", f"Un autre aliment porte déjà le nom '{nom}'.")
                        return
                    aliment.nom = nom
                    aliment.type_aliment = self.type_combo.currentText()
                    aliment.matiere_seche = self.ms_edit.value()
                    aliment.ufl = self.ufl_edit.value()
                    aliment.ufv = self.ufv_edit.value()
                    aliment.pdi = self.pdi_edit.value()
                    aliment.calcium = self.ca_edit.value()
                    aliment.phosphore = self.p_edit.value()
                else:
                    QMessageBox.warning(self, "Erreur", "Aliment introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Aliment enregistré dans la bibliothèque.")
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
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer définitivement '{self.nom_edit.text()}' de la bibliothèque ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                aliment = db.query(BibliothequeAliment).filter(BibliothequeAliment.id == self.current_id).first()
                if aliment:
                    db.delete(aliment)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Aliment supprimé de la bibliothèque.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Aliment introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()