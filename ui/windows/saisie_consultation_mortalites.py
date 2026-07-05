# ui/windows/saisie_consultation_mortalites.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Animal, Naissance, Mortalite
from controllers.mortalite_controller import MortaliteController

class SaisieConsultationMortalitesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des mortalités")
        self.resize(1000, 700)
        layout = QVBoxLayout(self)

        # Formulaire
        form_group = QWidget()
        form_layout = QFormLayout(form_group)

        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.animal_combo = QComboBox()
        self.animal_combo.setEditable(True)
        self.animal_combo.setEnabled(False)
        form_layout.addRow(QLabel("Animal (numéro boucle) :"), self.animal_combo)

        self.date_deces = QDateEdit()
        self.date_deces.setCalendarPopup(True)
        self.date_deces.setDate(QDate.currentDate())
        self.date_deces.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date de décès :"), self.date_deces)

        self.cause_deces = QLineEdit()
        self.cause_deces.setPlaceholderText("Cause du décès")
        form_layout.addRow(QLabel("Cause :"), self.cause_deces)

        self.remarque = QLineEdit()
        self.remarque.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Remarque :"), self.remarque)

        # Boutons
        form_btn_layout = QHBoxLayout()
        self.btn_modify = QPushButton("Modifier")
        self.btn_modify.clicked.connect(self.charger_selection)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer_mortalite)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.annuler_edition)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        form_btn_layout.addWidget(self.btn_modify)
        form_btn_layout.addWidget(self.btn_delete)
        form_btn_layout.addWidget(self.btn_cancel)
        form_btn_layout.addWidget(self.btn_save)
        form_btn_layout.addWidget(self.btn_close)
        form_layout.addRow(form_btn_layout)

        layout.addWidget(form_group)

        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # Tableau
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Éleveur :"))
        self.combo_filtre = QComboBox()
        self.combo_filtre.addItem("Tous", None)
        db = SessionLocal()
        for e in db.query(Eleveur).all():
            self.combo_filtre.addItem(f"{e.code_elevage} - {e.nom} {e.prenom}", e.code_elevage)
        db.close()
        self.combo_filtre.currentIndexChanged.connect(self.load_table)
        filter_layout.addWidget(self.combo_filtre)
        filter_layout.addStretch()
        self.btn_refresh = QPushButton("Rafraîchir")
        self.btn_refresh.clicked.connect(self.load_table)
        filter_layout.addWidget(self.btn_refresh)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Éleveur", "Boucle", "Date décès", "Cause"])
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

    def on_eleveur_changed(self):
        code = self.code_combo.currentText().strip()
        self.animal_combo.clear()
        if not code:
            self.animal_combo.setEnabled(False)
            return
        db = SessionLocal()
        # Animaux actifs (Naissance)
        animaux = db.query(Naissance).filter(Naissance.code_elevage == code, Naissance.actif == True).all()
        for a in animaux:
            self.animal_combo.addItem(f"{a.numero_boucle} (né le {a.date_naissance})", a.numero_boucle)
        self.animal_combo.setEnabled(self.animal_combo.count() > 0)
        db.close()

    def load_table(self):
        code_filtre = self.combo_filtre.currentData()
        db = SessionLocal()
        query = db.query(Mortalite)
        if code_filtre:
            query = query.filter(Mortalite.code_elevage == code_filtre)
        mortalites = query.order_by(Mortalite.date_deces.desc()).all()
        self.table.setRowCount(len(mortalites))
        for i, m in enumerate(mortalites):
            self.table.setItem(i, 0, QTableWidgetItem(str(m.id)))
            self.table.setItem(i, 1, QTableWidgetItem(m.code_elevage))
            self.table.setItem(i, 2, QTableWidgetItem(m.numero_boucle))
            self.table.setItem(i, 3, QTableWidgetItem(m.date_deces))
            self.table.setItem(i, 4, QTableWidgetItem(m.cause_deces))
        self.table.resizeColumnsToContents()
        db.close()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner une mortalité.")
            return
        self.current_id = int(self.table.item(row, 0).text())
        code = self.table.item(row, 1).text()
        boucle = self.table.item(row, 2).text()
        date_deces = self.table.item(row, 3).text()
        cause = self.table.item(row, 4).text()

        self.code_combo.setCurrentText(code)
        self.on_eleveur_changed()
        QApplication.processEvents()
        for i in range(self.animal_combo.count()):
            if self.animal_combo.itemText(i).startswith(boucle):
                self.animal_combo.setCurrentIndex(i)
                break
        self.date_deces.setDate(QDate.fromString(date_deces, "yyyy-MM-dd"))
        self.cause_deces.setText(cause)
        self.remarque.clear()  # à récupérer si besoin

    def annuler_edition(self):
        self.current_id = None
        self.code_combo.setCurrentIndex(-1)
        self.code_combo.setEditText("")
        self.animal_combo.clear()
        self.date_deces.setDate(QDate.currentDate())
        self.cause_deces.clear()
        self.remarque.clear()

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        num = self.animal_combo.currentData()
        if not num:
            QMessageBox.warning(self, "Erreur", "Choisissez un animal.")
            return
        cause = self.cause_deces.text().strip()
        if not cause:
            QMessageBox.warning(self, "Erreur", "Cause obligatoire.")
            return
        data = {
            'code_elevage': code,
            'numero_boucle': num,
            'date_deces': self.date_deces.date().toString("yyyy-MM-dd"),
            'cause_deces': cause,
            'remarque': self.remarque.text().strip() or None
        }
        if self.current_id is None:
            ok, msg = MortaliteController.ajouter_mortalite(data)
        else:
            ok, msg = MortaliteController.modifier_mortalite(self.current_id, data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_table()
            self.annuler_edition()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def supprimer_mortalite(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Sélection", "Sélectionnez une mortalité.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette mortalité ? L'animal réapparaîtra.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = MortaliteController.supprimer_mortalite(self.current_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_table()
                self.annuler_edition()
            else:
                QMessageBox.warning(self, "Erreur", msg)