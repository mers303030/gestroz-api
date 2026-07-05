# ui/windows/saisie_consultation_famille.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Personne

class SaisieConsultationFamilleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des membres de la famille")
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

        # Nom
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom")
        form_layout.addRow(QLabel("Nom :"), self.nom_edit)

        # Prénom
        self.prenom_edit = QLineEdit()
        self.prenom_edit.setPlaceholderText("Prénom")
        form_layout.addRow(QLabel("Prénom :"), self.prenom_edit)

        # Date de naissance
        self.date_naissance = QDateEdit()
        self.date_naissance.setCalendarPopup(True)
        self.date_naissance.setDate(QDate.currentDate())
        self.date_naissance.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date de naissance :"), self.date_naissance)

        # Occupation
        self.occupation_edit = QLineEdit()
        self.occupation_edit.setPlaceholderText("Occupation")
        form_layout.addRow(QLabel("Occupation :"), self.occupation_edit)

        # Lien de parenté
        self.lien_edit = QLineEdit()
        self.lien_edit.setPlaceholderText("Époux, enfant, frère, etc.")
        form_layout.addRow(QLabel("Lien de parenté :"), self.lien_edit)

        # Lieu de résidence
        self.lieu_edit = QLineEdit()
        self.lieu_edit.setPlaceholderText("Ville, commune, ...")
        form_layout.addRow(QLabel("Lieu de résidence :"), self.lieu_edit)

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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Date naiss.",
            "Occupation", "Lien parenté", "Lieu résidence"
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
            personnes = db.query(Personne).filter(Personne.code_elevage == code).all()
        finally:
            db.close()

        self.table.setRowCount(len(personnes))
        for i, p in enumerate(personnes):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(p.nom or ""))
            self.table.setItem(i, 2, QTableWidgetItem(p.prenom or ""))
            self.table.setItem(i, 3, QTableWidgetItem(p.date_naissance or ""))
            self.table.setItem(i, 4, QTableWidgetItem(p.occupation or ""))
            self.table.setItem(i, 5, QTableWidgetItem(p.lien_parente or ""))
            self.table.setItem(i, 6, QTableWidgetItem(p.lieu_residence or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.nom_edit.setText(self.table.item(row, 1).text())
        self.prenom_edit.setText(self.table.item(row, 2).text())
        self.date_naissance.setDate(QDate.fromString(self.table.item(row, 3).text(), "yyyy-MM-dd"))
        self.occupation_edit.setText(self.table.item(row, 4).text())
        self.lien_edit.setText(self.table.item(row, 5).text())
        self.lieu_edit.setText(self.table.item(row, 6).text())
        self.obs_edit.setText("")
        self.btn_save.setText("Mettre à jour")

    def nouveau(self):
        self.current_id = None
        self.nom_edit.clear()
        self.prenom_edit.clear()
        self.date_naissance.setDate(QDate.currentDate())
        self.occupation_edit.clear()
        self.lien_edit.clear()
        self.lieu_edit.clear()
        self.obs_edit.clear()
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

        prenom = self.prenom_edit.text().strip()
        if not prenom:
            QMessageBox.warning(self, "Erreur", "Le prénom est obligatoire.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                personne = Personne(
                    code_elevage=code,
                    nom=nom,
                    prenom=prenom,
                    date_naissance=self.date_naissance.date().toString("yyyy-MM-dd"),
                    occupation=self.occupation_edit.text().strip() or None,
                    lien_parente=self.lien_edit.text().strip() or None,
                    lieu_residence=self.lieu_edit.text().strip() or None,
                    observations=self.obs_edit.text().strip() or None
                )
                db.add(personne)
            else:
                personne = db.query(Personne).filter(Personne.id == self.current_id).first()
                if personne:
                    personne.nom = nom
                    personne.prenom = prenom
                    personne.date_naissance = self.date_naissance.date().toString("yyyy-MM-dd")
                    personne.occupation = self.occupation_edit.text().strip() or None
                    personne.lien_parente = self.lien_edit.text().strip() or None
                    personne.lieu_residence = self.lieu_edit.text().strip() or None
                    personne.observations = self.obs_edit.text().strip() or None
                else:
                    QMessageBox.warning(self, "Erreur", "Personne introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Membre de la famille enregistré.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une personne.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette personne ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                personne = db.query(Personne).filter(Personne.id == self.current_id).first()
                if personne:
                    db.delete(personne)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Personne supprimée.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Personne introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()