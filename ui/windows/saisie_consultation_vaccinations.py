# ui/windows/saisie_consultation_vaccinations.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Vaccination

class SaisieConsultationVaccinationsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vaccinations et traitements collectifs")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        # ---- Formulaire ----
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.load_table)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Vaccination", "Antiparasitaire", "Autre collectif"])
        form_layout.addRow(QLabel("Type :"), self.type_combo)

        self.maladie = QLineEdit()
        self.maladie.setPlaceholderText("Maladie ou parasite visé")
        form_layout.addRow(QLabel("Maladie / Parasite :"), self.maladie)

        self.date_vaccination = QDateEdit()
        self.date_vaccination.setCalendarPopup(True)
        self.date_vaccination.setDate(QDate.currentDate())
        self.date_vaccination.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date :"), self.date_vaccination)

        self.administrateur = QComboBox()
        self.administrateur.addItems(["Docteur", "Technicien", "Éleveur", "Autre"])
        form_layout.addRow(QLabel("Administrateur :"), self.administrateur)

        self.nom_administrateur = QLineEdit()
        self.nom_administrateur.setPlaceholderText("Nom de l'administrateur")
        form_layout.addRow(QLabel("Nom :"), self.nom_administrateur)

        self.statut = QComboBox()
        self.statut.addItems(["État", "Privé"])
        self.statut.currentTextChanged.connect(self.on_statut_changed)
        form_layout.addRow(QLabel("Statut :"), self.statut)

        self.cout = QDoubleSpinBox()
        self.cout.setRange(0, 100000)
        self.cout.setSuffix(" DH")
        self.cout.setEnabled(False)
        form_layout.addRow(QLabel("Coût :"), self.cout)

        self.observations = QLineEdit()
        self.observations.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Observations :"), self.observations)

        # Boutons
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

        # ---- Tableau ----
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Maladie", "Date", "Admin", "Nom", "Statut", "Coût"])
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

    def on_statut_changed(self):
        self.cout.setEnabled(self.statut.currentText() == "Privé")

    def load_table(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return
        db = SessionLocal()
        vaccinations = db.query(Vaccination).filter(Vaccination.code_elevage == code).all()
        db.close()
        self.table.setRowCount(len(vaccinations))
        for i, v in enumerate(vaccinations):
            self.table.setItem(i, 0, QTableWidgetItem(str(v.id)))
            self.table.setItem(i, 1, QTableWidgetItem(v.type_evenement or ""))
            self.table.setItem(i, 2, QTableWidgetItem(v.maladie or ""))
            self.table.setItem(i, 3, QTableWidgetItem(v.date_vaccination or ""))
            self.table.setItem(i, 4, QTableWidgetItem(v.administrateur or ""))
            self.table.setItem(i, 5, QTableWidgetItem(v.nom_administrateur or ""))
            self.table.setItem(i, 6, QTableWidgetItem(v.statut or ""))
            self.table.setItem(i, 7, QTableWidgetItem(f"{v.cout_par_dose:.2f}" if v.cout_par_dose else ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.type_combo.setCurrentText(self.table.item(row, 1).text())
        self.maladie.setText(self.table.item(row, 2).text())
        self.date_vaccination.setDate(QDate.fromString(self.table.item(row, 3).text(), "yyyy-MM-dd"))
        self.administrateur.setCurrentText(self.table.item(row, 4).text())
        self.nom_administrateur.setText(self.table.item(row, 5).text())
        self.statut.setCurrentText(self.table.item(row, 6).text())
        cout = self.table.item(row, 7).text()
        self.cout.setValue(float(cout) if cout else 0)
        self.btn_save.setText("Mettre à jour")

    def annuler(self):
        self.current_id = None
        self.type_combo.setCurrentIndex(0)
        self.maladie.clear()
        self.date_vaccination.setDate(QDate.currentDate())
        self.administrateur.setCurrentIndex(0)
        self.nom_administrateur.clear()
        self.statut.setCurrentIndex(0)
        self.cout.setValue(0)
        self.observations.clear()
        self.btn_save.setText("Sauvegarder")

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        if not self.maladie.text().strip():
            QMessageBox.warning(self, "Erreur", "Maladie/parasite obligatoire.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                v = Vaccination(
                    code_elevage=code,
                    type_evenement=self.type_combo.currentText(),
                    maladie=self.maladie.text().strip(),
                    date_vaccination=self.date_vaccination.date().toString("yyyy-MM-dd"),
                    administrateur=self.administrateur.currentText(),
                    nom_administrateur=self.nom_administrateur.text().strip() or None,
                    statut=self.statut.currentText(),
                    cout_par_dose=self.cout.value() if self.statut.currentText() == "Privé" else None,
                    observations=self.observations.text().strip() or None
                )
                db.add(v)
            else:
                v = db.query(Vaccination).filter(Vaccination.id == self.current_id).first()
                if v:
                    v.type_evenement = self.type_combo.currentText()
                    v.maladie = self.maladie.text().strip()
                    v.date_vaccination = self.date_vaccination.date().toString("yyyy-MM-dd")
                    v.administrateur = self.administrateur.currentText()
                    v.nom_administrateur = self.nom_administrateur.text().strip() or None
                    v.statut = self.statut.currentText()
                    v.cout_par_dose = self.cout.value() if self.statut.currentText() == "Privé" else None
                    v.observations = self.observations.text().strip() or None
                else:
                    QMessageBox.warning(self, "Erreur", "Vaccination introuvable.")
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
            QMessageBox.warning(self, "Erreur", "Sélectionnez une vaccination.")
            return
        if QMessageBox.question(self, "Confirmation", "Supprimer ?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                v = db.query(Vaccination).filter(Vaccination.id == self.current_id).first()
                if v:
                    db.delete(v)
                    db.commit()
                    self.load_table()
                    self.annuler()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()