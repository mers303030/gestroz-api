# ui/windows/gestion_reproduction.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Animal, Reproduction
from datetime import datetime, timedelta

class GestionReproductionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion de la reproduction")
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

        # Femelle (vache/génisse)
        self.femelle_combo = QComboBox()
        self.femelle_combo.setEditable(True)
        self.femelle_combo.setPlaceholderText("Choisissez ou tapez un numéro")
        self.femelle_combo.setEnabled(False)
        form_layout.addRow(QLabel("Femelle (numéro boucle) :"), self.femelle_combo)

        # Type d'événement
        self.type_combo = QComboBox()
        self.type_combo.addItems(["IA", "Saillie", "Diagnostic gestation", "Tarissement", "Vêlage"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow(QLabel("Type d'événement :"), self.type_combo)

        # Taureau (géniteur) - pour IA et Saillie
        self.taureau_combo = QComboBox()
        self.taureau_combo.setEditable(True)
        self.taureau_combo.setPlaceholderText("Choisissez ou tapez un numéro")
        self.taureau_combo.setEnabled(False)
        form_layout.addRow(QLabel("Taureau (géniteur) :"), self.taureau_combo)

        # Date de l'événement
        self.date_evenement = QDateEdit()
        self.date_evenement.setCalendarPopup(True)
        self.date_evenement.setDate(QDate.currentDate())
        self.date_evenement.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date :"), self.date_evenement)

        # Statut gestation (pour Diagnostic gestation)
        self.gestatif_combo = QComboBox()
        self.gestatif_combo.addItems(["", "Oui", "Non", "Non confirmé"])
        self.gestatif_combo.setEnabled(False)
        form_layout.addRow(QLabel("Gestatif :"), self.gestatif_combo)

        # Date vêlage prévu (pour Vêlage)
        self.date_velage = QDateEdit()
        self.date_velage.setCalendarPopup(True)
        self.date_velage.setDate(QDate.currentDate().addDays(285))
        self.date_velage.setDisplayFormat("yyyy-MM-dd")
        self.date_velage.setEnabled(False)
        form_layout.addRow(QLabel("Date vêlage prévu :"), self.date_velage)

        # Observations
        self.observations = QLineEdit()
        self.observations.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Observations :"), self.observations)

        # Boutons
        form_btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.annuler)
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

        # ==================== TABLEAU ====================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Date", "Type", "Femelle", "Taureau", "Gestatif", "Vêlage prévu"
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
        """Remplit les listes des femelles et des taureaux pour l'élevage sélectionné."""
        code = self.code_combo.currentText().strip()
        self.femelle_combo.clear()
        self.taureau_combo.clear()
        if not code:
            self.femelle_combo.setEnabled(False)
            self.taureau_combo.setEnabled(False)
            self.load_table()
            return

        db = SessionLocal()
        try:
            # Femelles (vaches et génisses)
            femelles = db.query(Animal).filter(
                Animal.code_elevage == code,
                Animal.sexe == 'F',
                Animal.categorie.in_(['Vache', 'Génisse']),
                Animal.actif == True
            ).all()
            for f in femelles:
                self.femelle_combo.addItem(f"{f.numero_boucle} - {f.categorie}", f.numero_boucle)
            self.femelle_combo.setEnabled(len(femelles) > 0)

            # Taureaux (géniteurs et taurillons)
            taureaux = db.query(Animal).filter(
                Animal.code_elevage == code,
                Animal.sexe == 'M',
                Animal.categorie.in_(['Géniteur', 'Taurillon']),
                Animal.actif == True
            ).all()
            for t in taureaux:
                self.taureau_combo.addItem(f"{t.numero_boucle} - {t.categorie}", t.numero_boucle)
            self.taureau_combo.setEnabled(len(taureaux) > 0)
        finally:
            db.close()

        self.load_table()
        self.on_type_changed()

    def on_type_changed(self):
        """Active/désactive les champs selon le type d'événement."""
        type_evt = self.type_combo.currentText()
        if type_evt in ["IA", "Saillie"]:
            self.taureau_combo.setEnabled(True)
            self.gestatif_combo.setEnabled(False)
            self.date_velage.setEnabled(False)
        elif type_evt == "Diagnostic gestation":
            self.taureau_combo.setEnabled(False)
            self.gestatif_combo.setEnabled(True)
            self.date_velage.setEnabled(False)
        elif type_evt == "Vêlage":
            self.taureau_combo.setEnabled(False)
            self.gestatif_combo.setEnabled(False)
            self.date_velage.setEnabled(True)
        else:  # Tarissement, Autre
            self.taureau_combo.setEnabled(False)
            self.gestatif_combo.setEnabled(False)
            self.date_velage.setEnabled(False)

    def load_table(self):
        """Charge tous les événements pour l'élevage sélectionné."""
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            evenements = db.query(Reproduction).filter(
                Reproduction.code_elevage == code
            ).order_by(Reproduction.date_evenement.desc()).all()
        finally:
            db.close()

        self.table.setRowCount(len(evenements))
        for i, evt in enumerate(evenements):
            self.table.setItem(i, 0, QTableWidgetItem(str(evt.id)))
            self.table.setItem(i, 1, QTableWidgetItem(evt.date_evenement))
            self.table.setItem(i, 2, QTableWidgetItem(evt.type_evenement or ""))
            self.table.setItem(i, 3, QTableWidgetItem(evt.numero_boucle or ""))
            self.table.setItem(i, 4, QTableWidgetItem(evt.taureau_boucle or ""))
            self.table.setItem(i, 5, QTableWidgetItem(evt.gestatif or ""))
            self.table.setItem(i, 6, QTableWidgetItem(evt.date_velage_prevu or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        """Double-clic sur une ligne : charge l'événement dans le formulaire."""
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        date_evt = self.table.item(row, 1).text()
        type_evt = self.table.item(row, 2).text()
        femelle = self.table.item(row, 3).text()
        taureau = self.table.item(row, 4).text()
        gestatif = self.table.item(row, 5).text()
        velage = self.table.item(row, 6).text()

        # Charger dans le formulaire
        self.type_combo.setCurrentText(type_evt)
        self.on_type_changed()
        self.femelle_combo.setEditText(femelle)
        self.taureau_combo.setEditText(taureau)
        self.date_evenement.setDate(QDate.fromString(date_evt, "yyyy-MM-dd"))
        self.gestatif_combo.setCurrentText(gestatif)
        if velage:
            self.date_velage.setDate(QDate.fromString(velage, "yyyy-MM-dd"))
        else:
            self.date_velage.setDate(QDate.currentDate().addDays(285))
        self.observations.setText("")
        self.btn_save.setText("Mettre à jour")

    def annuler(self):
        """Réinitialise le formulaire."""
        self.current_id = None
        self.type_combo.setCurrentIndex(0)
        self.femelle_combo.setCurrentIndex(-1)
        self.taureau_combo.setCurrentIndex(-1)
        self.date_evenement.setDate(QDate.currentDate())
        self.gestatif_combo.setCurrentIndex(0)
        self.date_velage.setDate(QDate.currentDate().addDays(285))
        self.observations.clear()
        self.btn_save.setText("Sauvegarder")
        self.on_eleveur_changed()

    def enregistrer(self):
        """Sauvegarde ou met à jour un événement."""
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        # Récupérer la femelle
        numero_boucle = self.femelle_combo.currentData()
        if not numero_boucle:
            numero_boucle = self.femelle_combo.currentText().strip()
            if not numero_boucle:
                QMessageBox.warning(self, "Erreur", "Choisissez ou saisissez une femelle.")
                return

        # Récupérer le taureau (si nécessaire)
        type_evt = self.type_combo.currentText()
        taureau = None
        if type_evt in ["IA", "Saillie"]:
            taureau = self.taureau_combo.currentData()
            if not taureau:
                taureau = self.taureau_combo.currentText().strip()
                if not taureau:
                    QMessageBox.warning(self, "Erreur", "Veuillez sélectionner ou saisir un taureau.")
                    return

        # Récupérer les autres champs
        date_evt = self.date_evenement.date().toString("yyyy-MM-dd")
        gestatif = self.gestatif_combo.currentText() if self.gestatif_combo.isEnabled() else None
        velage = None
        if type_evt == "Vêlage" and self.date_velage.isEnabled():
            velage = self.date_velage.date().toString("yyyy-MM-dd")
        observations = self.observations.text().strip() or None

        db = SessionLocal()
        try:
            if self.current_id is None:
                # Création
                evenement = Reproduction(
                    code_elevage=code,
                    numero_boucle=numero_boucle,
                    type_evenement=type_evt,
                    taureau_boucle=taureau,
                    date_evenement=date_evt,
                    gestatif=gestatif,
                    date_velage_prevu=velage,
                    observations=observations
                )
                db.add(evenement)
            else:
                # Modification
                evenement = db.query(Reproduction).filter(Reproduction.id == self.current_id).first()
                if evenement:
                    evenement.type_evenement = type_evt
                    evenement.numero_boucle = numero_boucle
                    evenement.taureau_boucle = taureau
                    evenement.date_evenement = date_evt
                    evenement.gestatif = gestatif
                    evenement.date_velage_prevu = velage
                    evenement.observations = observations
                else:
                    QMessageBox.warning(self, "Erreur", "Événement introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Événement enregistré.")
            self.load_table()
            self.annuler()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        """Supprime l'événement sélectionné."""
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un événement à supprimer.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet événement ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                evenement = db.query(Reproduction).filter(Reproduction.id == self.current_id).first()
                if evenement:
                    db.delete(evenement)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Événement supprimé.")
                    self.load_table()
                    self.annuler()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()