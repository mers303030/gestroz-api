# ui/windows/saisie_consultation_traitements.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, TraitementCuratif

class SaisieConsultationTraitementsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Traitements curatifs")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.load_table)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.symptome = QLineEdit()
        self.symptome.setPlaceholderText("Symptôme observé")
        form_layout.addRow(QLabel("Symptôme :"), self.symptome)

        self.cause = QLineEdit()
        self.cause.setPlaceholderText("Cause présumée")
        form_layout.addRow(QLabel("Cause :"), self.cause)

        self.maladie = QLineEdit()
        self.maladie.setPlaceholderText("Maladie")
        form_layout.addRow(QLabel("Maladie :"), self.maladie)

        self.traitement = QLineEdit()
        self.traitement.setPlaceholderText("Traitement appliqué")
        form_layout.addRow(QLabel("Traitement :"), self.traitement)

        self.nom_traiteur = QLineEdit()
        self.nom_traiteur.setPlaceholderText("Nom du vétérinaire/traiteur")
        form_layout.addRow(QLabel("Traiteur :"), self.nom_traiteur)

        self.date_traitement = QDateEdit()
        self.date_traitement.setCalendarPopup(True)
        self.date_traitement.setDate(QDate.currentDate())
        self.date_traitement.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date :"), self.date_traitement)

        self.produit = QLineEdit()
        self.produit.setPlaceholderText("Produit utilisé")
        form_layout.addRow(QLabel("Produit :"), self.produit)

        self.dose = QLineEdit()
        self.dose.setPlaceholderText("Dose administrée")
        form_layout.addRow(QLabel("Dose :"), self.dose)

        self.observations = QLineEdit()
        self.observations.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Observations :"), self.observations)

        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.annuler)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        for btn in [self.btn_new, self.btn_save, self.btn_delete, self.btn_close]:
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        form_layout.addRow(btn_layout)

        layout.addWidget(form_group)

        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Symptôme", "Cause", "Maladie", "Traitement", "Traiteur", "Date", "Produit", "Dose"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.charger_selection)
        layout.addWidget(self.table)

        self.current_id = None
        self.load_table()

    def get_all_codes(self):
        db = SessionLocal()
        codes = [e.code_elevage for e in db.query(Eleveur).all()]
        db.close()
        return codes

    def load_table(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return
        db = SessionLocal()
        traitements = db.query(TraitementCuratif).filter(TraitementCuratif.code_elevage == code).all()
        db.close()
        self.table.setRowCount(len(traitements))
        for i, t in enumerate(traitements):
            self.table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(i, 1, QTableWidgetItem(t.symptome or ""))
            self.table.setItem(i, 2, QTableWidgetItem(t.cause or ""))
            self.table.setItem(i, 3, QTableWidgetItem(t.maladie or ""))
            self.table.setItem(i, 4, QTableWidgetItem(t.traitement or ""))
            self.table.setItem(i, 5, QTableWidgetItem(t.nom_traiteur or ""))
            self.table.setItem(i, 6, QTableWidgetItem(t.date_traitement or ""))
            self.table.setItem(i, 7, QTableWidgetItem(t.produit or ""))
            self.table.setItem(i, 8, QTableWidgetItem(t.dose or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.symptome.setText(self.table.item(row, 1).text())
        self.cause.setText(self.table.item(row, 2).text())
        self.maladie.setText(self.table.item(row, 3).text())
        self.traitement.setText(self.table.item(row, 4).text())
        self.nom_traiteur.setText(self.table.item(row, 5).text())
        self.date_traitement.setDate(QDate.fromString(self.table.item(row, 6).text(), "yyyy-MM-dd"))
        self.produit.setText(self.table.item(row, 7).text())
        self.dose.setText(self.table.item(row, 8).text())
        self.btn_save.setText("Mettre à jour")

    def annuler(self):
        self.current_id = None
        self.symptome.clear()
        self.cause.clear()
        self.maladie.clear()
        self.traitement.clear()
        self.nom_traiteur.clear()
        self.date_traitement.setDate(QDate.currentDate())
        self.produit.clear()
        self.dose.clear()
        self.observations.clear()
        self.btn_save.setText("Sauvegarder")

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        if not self.symptome.text().strip() or not self.traitement.text().strip():
            QMessageBox.warning(self, "Erreur", "Symptôme et traitement obligatoires.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                t = TraitementCuratif(
                    code_elevage=code,
                    symptome=self.symptome.text().strip(),
                    cause=self.cause.text().strip() or None,
                    maladie=self.maladie.text().strip() or None,
                    traitement=self.traitement.text().strip(),
                    nom_traiteur=self.nom_traiteur.text().strip() or None,
                    date_traitement=self.date_traitement.date().toString("yyyy-MM-dd"),
                    produit=self.produit.text().strip() or None,
                    dose=self.dose.text().strip() or None,
                    observations=self.observations.text().strip() or None
                )
                db.add(t)
            else:
                t = db.query(TraitementCuratif).filter(TraitementCuratif.id == self.current_id).first()
                if t:
                    t.symptome = self.symptome.text().strip()
                    t.cause = self.cause.text().strip() or None
                    t.maladie = self.maladie.text().strip() or None
                    t.traitement = self.traitement.text().strip()
                    t.nom_traiteur = self.nom_traiteur.text().strip() or None
                    t.date_traitement = self.date_traitement.date().toString("yyyy-MM-dd")
                    t.produit = self.produit.text().strip() or None
                    t.dose = self.dose.text().strip() or None
                    t.observations = self.observations.text().strip() or None
                else:
                    QMessageBox.warning(self, "Erreur", "Traitement introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Enregistré.")
            self.load_table()
            self.annuler()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un traitement.")
            return
        if QMessageBox.question(self, "Confirmation", "Supprimer ?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                t = db.query(TraitementCuratif).filter(TraitementCuratif.id == self.current_id).first()
                if t:
                    db.delete(t)
                    db.commit()
                    self.load_table()
                    self.annuler()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()