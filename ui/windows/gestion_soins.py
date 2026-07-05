from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Animal, Soin
from controllers.soin_controller import SoinController

class GestionSoinsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carnet sanitaire (soins)")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        # --- Formulaire d'ajout ---
        form_group = QWidget()
        form_layout = QFormLayout(form_group)

        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.animal_combo = QComboBox()
        self.animal_combo.setEnabled(False)
        form_layout.addRow(QLabel("Animal :"), self.animal_combo)

        self.date_soin = QDateEdit()
        self.date_soin.setCalendarPopup(True)
        self.date_soin.setDate(QDate.currentDate())
        self.date_soin.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date du soin :"), self.date_soin)

        self.type_soin = QComboBox()
        self.type_soin.addItems(["Vaccination", "Traitement", "Antiparasitaire", "Examen", "Autre"])
        form_layout.addRow(QLabel("Type de soin :"), self.type_soin)

        self.produit = QLineEdit()
        self.produit.setPlaceholderText("Ex: Vermectin, etc.")
        form_layout.addRow(QLabel("Produit :"), self.produit)

        self.dose = QLineEdit()
        self.dose.setPlaceholderText("Ex: 10 ml")
        form_layout.addRow(QLabel("Dose :"), self.dose)

        self.voie = QComboBox()
        self.voie.addItems(["", "IM", "IV", "SC", "Orale", "Topique"])
        form_layout.addRow(QLabel("Voie d'administration :"), self.voie)

        self.veterinaire = QLineEdit()
        self.veterinaire.setPlaceholderText("Nom du vétérinaire (optionnel)")
        form_layout.addRow(QLabel("Vétérinaire :"), self.veterinaire)

        self.date_rappel = QDateEdit()
        self.date_rappel.setCalendarPopup(True)
        self.date_rappel.setDate(QDate.currentDate().addDays(180))
        self.date_rappel.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date de rappel :"), self.date_rappel)

        self.observations = QLineEdit()
        form_layout.addRow(QLabel("Observations :"), self.observations)

        # Boutons
        form_btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Ajouter")
        self.btn_save.clicked.connect(self.ajouter)
        self.btn_modify = QPushButton("Modifier")
        self.btn_modify.clicked.connect(self.modifier)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.annuler)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        form_btn_layout.addWidget(self.btn_save)
        form_btn_layout.addWidget(self.btn_modify)
        form_btn_layout.addWidget(self.btn_delete)
        form_btn_layout.addWidget(self.btn_cancel)
        form_btn_layout.addStretch()
        form_btn_layout.addWidget(self.btn_close)
        form_layout.addRow(form_btn_layout)

        layout.addWidget(form_group)

        # --- Séparateur ---
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # --- Tableau des soins ---
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Type", "Animal", "Produit", "Dose", "Voie", "Rappel"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

        self.current_id = None
        self.load_table()
        self.on_eleveur_changed()

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
        eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
        if not eleveur:
            self.animal_combo.setEnabled(False)
            db.close()
            return
        animaux = SoinController.get_animaux_actifs(code)
        for a in animaux:
            self.animal_combo.addItem(f"{a.numero_boucle} - {a.categorie}", a.numero_boucle)
        self.animal_combo.setEnabled(len(animaux) > 0)
        db.close()

    def load_table(self):
        code_filtre = self.combo_filtre.currentData()
        db = SessionLocal()
        query = db.query(Soin)
        if code_filtre:
            query = query.filter(Soin.code_elevage == code_filtre)
        soins = query.order_by(Soin.date_soin.desc()).all()
        self.table.setRowCount(len(soins))
        for i, s in enumerate(soins):
            self.table.setItem(i, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(i, 1, QTableWidgetItem(s.date_soin))
            self.table.setItem(i, 2, QTableWidgetItem(s.type_soin))
            self.table.setItem(i, 3, QTableWidgetItem(s.numero_boucle))
            self.table.setItem(i, 4, QTableWidgetItem(s.produit or ""))
            self.table.setItem(i, 5, QTableWidgetItem(s.dose or ""))
            self.table.setItem(i, 6, QTableWidgetItem(s.voie or ""))
            self.table.setItem(i, 7, QTableWidgetItem(s.date_rappel or ""))
        self.table.resizeColumnsToContents()
        db.close()

    def on_selection_changed(self):
        row = self.table.currentRow()
        if row < 0:
            self.current_id = None
            self.annuler()
            return
        self.current_id = int(self.table.item(row, 0).text())
        date = self.table.item(row, 1).text()
        type_soin = self.table.item(row, 2).text()
        animal = self.table.item(row, 3).text()
        produit = self.table.item(row, 4).text()
        dose = self.table.item(row, 5).text()
        voie = self.table.item(row, 6).text()
        rappel = self.table.item(row, 7).text()
        self.code_combo.setCurrentText("")  # on ne change pas l'élevage
        self.animal_combo.setEditText(animal)
        self.date_soin.setDate(QDate.fromString(date, "yyyy-MM-dd"))
        self.type_soin.setCurrentText(type_soin)
        self.produit.setText(produit)
        self.dose.setText(dose)
        self.voie.setCurrentText(voie)
        if rappel:
            self.date_rappel.setDate(QDate.fromString(rappel, "yyyy-MM-dd"))
        else:
            self.date_rappel.setDate(QDate.currentDate().addDays(180))
        self.btn_save.setText("Modifier")
        self.btn_cancel.setEnabled(True)

    def annuler(self):
        self.current_id = None
        self.code_combo.setCurrentIndex(-1)
        self.code_combo.setEditText("")
        self.animal_combo.clear()
        self.date_soin.setDate(QDate.currentDate())
        self.type_soin.setCurrentIndex(0)
        self.produit.clear()
        self.dose.clear()
        self.voie.setCurrentIndex(0)
        self.date_rappel.setDate(QDate.currentDate().addDays(180))
        self.observations.clear()
        self.btn_save.setText("Ajouter")
        self.btn_cancel.setEnabled(False)
        self.on_eleveur_changed()

    def ajouter(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        numero_boucle = self.animal_combo.currentData()
        if not numero_boucle:
            QMessageBox.warning(self, "Erreur", "Choisissez un animal.")
            return
        data = {
            'code_elevage': code,
            'numero_boucle': numero_boucle,
            'date_soin': self.date_soin.date().toString("yyyy-MM-dd"),
            'type_soin': self.type_soin.currentText(),
            'produit': self.produit.text().strip() or None,
            'dose': self.dose.text().strip() or None,
            'voie': self.voie.currentText() or None,
            'veterinaire': self.veterinaire.text().strip() or None,
            'date_rappel': self.date_rappel.date().toString("yyyy-MM-dd") if self.date_rappel.isEnabled() else None,
            'observations': self.observations.text().strip() or None
        }
        ok, msg = SoinController.ajouter_soin(data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_table()
            self.annuler()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def modifier(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un soin à modifier.")
            return
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        numero_boucle = self.animal_combo.currentData()
        if not numero_boucle:
            QMessageBox.warning(self, "Erreur", "Choisissez un animal.")
            return
        data = {
            'code_elevage': code,
            'numero_boucle': numero_boucle,
            'date_soin': self.date_soin.date().toString("yyyy-MM-dd"),
            'type_soin': self.type_soin.currentText(),
            'produit': self.produit.text().strip() or None,
            'dose': self.dose.text().strip() or None,
            'voie': self.voie.currentText() or None,
            'veterinaire': self.veterinaire.text().strip() or None,
            'date_rappel': self.date_rappel.date().toString("yyyy-MM-dd") if self.date_rappel.isEnabled() else None,
            'observations': self.observations.text().strip() or None
        }
        ok, msg = SoinController.modifier_soin(self.current_id, data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_table()
            self.annuler()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un soin à supprimer.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer ce soin ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = SoinController.supprimer_soin(self.current_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_table()
                self.annuler()
            else:
                QMessageBox.warning(self, "Erreur", msg)