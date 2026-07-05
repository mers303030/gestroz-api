# ui/windows/saisie_consultation_ressources.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Ressource

class SaisieConsultationRessourcesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des autres ressources")
        self.resize(1200, 800)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE (HAUT) ====================
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.setPlaceholderText("Sélectionnez ou tapez un code élevage")
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["", "Animaux", "Revenu extérieur"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow(QLabel("Type de ressource :"), self.type_combo)

        # Groupe Animaux
        self.animal_group = QWidget()
        animal_layout = QFormLayout(self.animal_group)

        self.espece_edit = QLineEdit()
        self.espece_edit.setPlaceholderText("Ovins, Caprins, Équidés, Volailles, Autres")
        animal_layout.addRow(QLabel("Espèce :"), self.espece_edit)

        self.effectif_edit = QSpinBox()
        self.effectif_edit.setRange(0, 100000)
        self.effectif_edit.setSingleStep(1)
        self.effectif_edit.setSuffix(" têtes")
        animal_layout.addRow(QLabel("Effectif :"), self.effectif_edit)

        self.production_edit = QLineEdit()
        self.production_edit.setPlaceholderText("Lait, Viande, Œufs, Laine, ...")
        animal_layout.addRow(QLabel("Production :"), self.production_edit)

        self.quantite_edit = QDoubleSpinBox()
        self.quantite_edit.setRange(0, 100000)
        self.quantite_edit.setSingleStep(1)
        self.quantite_edit.setSuffix(" kg/l/unités")
        animal_layout.addRow(QLabel("Quantité annuelle :"), self.quantite_edit)

        self.destination_combo = QComboBox()
        self.destination_combo.addItems(["", "Vente", "Autoconsommation", "Mixte"])
        animal_layout.addRow(QLabel("Destination :"), self.destination_combo)

        form_layout.addRow(QLabel(""), self.animal_group)

        # Groupe Revenu extérieur
        self.revenu_group = QWidget()
        revenu_layout = QFormLayout(self.revenu_group)

        self.type_revenu_edit = QComboBox()
        self.type_revenu_edit.addItems(["", "Activité non agricole", "Pension", "Envoi de fonds", "Commerce", "Location", "Autre"])
        revenu_layout.addRow(QLabel("Type de revenu :"), self.type_revenu_edit)

        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Menuisier, Électricien, Boutique, ...")
        revenu_layout.addRow(QLabel("Description :"), self.description_edit)

        self.montant_edit = QDoubleSpinBox()
        self.montant_edit.setRange(0, 1000000)
        self.montant_edit.setSingleStep(100)
        self.montant_edit.setSuffix(" DH")
        revenu_layout.addRow(QLabel("Montant annuel (DH) :"), self.montant_edit)

        self.periodicite_combo = QComboBox()
        self.periodicite_combo.addItems(["", "Mensuel", "Trimestriel", "Semestriel", "Annuel", "Saisonnier"])
        revenu_layout.addRow(QLabel("Périodicité :"), self.periodicite_combo)

        self.saisonnalite_edit = QLineEdit()
        self.saisonnalite_edit.setPlaceholderText("Période (ex: été, hiver, ...)")
        revenu_layout.addRow(QLabel("Saisonnalité :"), self.saisonnalite_edit)

        form_layout.addRow(QLabel(""), self.revenu_group)

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

        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Espèce / Revenu", "Effectif / Montant",
            "Production / Description", "Quantité / Périodicité",
            "Destination / Saisonnalité", "Observations"
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
        self.on_type_changed()

    def get_all_codes(self):
        db = SessionLocal()
        try:
            return [e.code_elevage for e in db.query(Eleveur).all()]
        finally:
            db.close()

    def on_type_changed(self):
        type_ = self.type_combo.currentText()
        self.animal_group.setVisible(type_ == "Animaux")
        self.revenu_group.setVisible(type_ == "Revenu extérieur")

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
            ressources = db.query(Ressource).filter(Ressource.code_elevage == code).all()
        finally:
            db.close()

        self.table.setRowCount(len(ressources))
        for i, r in enumerate(ressources):
            self.table.setItem(i, 0, QTableWidgetItem(str(r.id)))
            self.table.setItem(i, 1, QTableWidgetItem(r.type_ressource or ""))
            if r.type_ressource == "Animaux":
                self.table.setItem(i, 2, QTableWidgetItem(r.espece or ""))
                self.table.setItem(i, 3, QTableWidgetItem(str(r.effectif) if r.effectif else ""))
                self.table.setItem(i, 4, QTableWidgetItem(r.production or ""))
                self.table.setItem(i, 5, QTableWidgetItem(f"{r.quantite_annuelle:.1f}" if r.quantite_annuelle else ""))
                self.table.setItem(i, 6, QTableWidgetItem(r.destination or ""))
            else:
                self.table.setItem(i, 2, QTableWidgetItem(r.type_revenu or ""))
                self.table.setItem(i, 3, QTableWidgetItem(f"{r.montant_annuel:.0f}" if r.montant_annuel else ""))
                self.table.setItem(i, 4, QTableWidgetItem(r.description or ""))
                self.table.setItem(i, 5, QTableWidgetItem(r.periodicite or ""))
                self.table.setItem(i, 6, QTableWidgetItem(r.saisonnalite or ""))
            self.table.setItem(i, 7, QTableWidgetItem(r.observations or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())

        type_ressource = self.table.item(row, 1).text()
        self.type_combo.setCurrentText(type_ressource)
        self.on_type_changed()

        if type_ressource == "Animaux":
            self.espece_edit.setText(self.table.item(row, 2).text())
            self.effectif_edit.setValue(int(self.table.item(row, 3).text()) if self.table.item(row, 3).text() else 0)
            self.production_edit.setText(self.table.item(row, 4).text())
            self.quantite_edit.setValue(float(self.table.item(row, 5).text()) if self.table.item(row, 5).text() else 0)
            self.destination_combo.setCurrentText(self.table.item(row, 6).text())
        else:
            self.type_revenu_edit.setCurrentText(self.table.item(row, 2).text())
            self.montant_edit.setValue(float(self.table.item(row, 3).text()) if self.table.item(row, 3).text() else 0)
            self.description_edit.setText(self.table.item(row, 4).text())
            self.periodicite_combo.setCurrentText(self.table.item(row, 5).text())
            self.saisonnalite_edit.setText(self.table.item(row, 6).text())

        self.obs_edit.setText(self.table.item(row, 7).text())
        self.btn_save.setText("Mettre à jour")

    def nouveau(self):
        self.current_id = None
        self.type_combo.setCurrentIndex(0)
        self.espece_edit.clear()
        self.effectif_edit.setValue(0)
        self.production_edit.clear()
        self.quantite_edit.setValue(0)
        self.destination_combo.setCurrentIndex(0)
        self.type_revenu_edit.setCurrentIndex(0)
        self.description_edit.clear()
        self.montant_edit.setValue(0)
        self.periodicite_combo.setCurrentIndex(0)
        self.saisonnalite_edit.clear()
        self.obs_edit.clear()
        self.btn_save.setText("Sauvegarder")
        self.on_type_changed()

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        type_ressource = self.type_combo.currentText()
        if not type_ressource:
            QMessageBox.warning(self, "Erreur", "Choisissez un type de ressource.")
            return

        observations = self.obs_edit.text().strip() or None

        db = SessionLocal()
        try:
            if self.current_id is None:
                if type_ressource == "Animaux":
                    espece = self.espece_edit.text().strip()
                    if not espece:
                        QMessageBox.warning(self, "Erreur", "L'espèce est obligatoire.")
                        return
                    if self.effectif_edit.value() <= 0:
                        QMessageBox.warning(self, "Erreur", "L'effectif doit être positif.")
                        return

                    ressource = Ressource(
                        code_elevage=code,
                        type_ressource=type_ressource,
                        espece=espece,
                        effectif=self.effectif_edit.value(),
                        production=self.production_edit.text().strip() or None,
                        quantite_annuelle=self.quantite_edit.value(),
                        destination=self.destination_combo.currentText() or None,
                        observations=observations
                    )
                    db.add(ressource)
                else:
                    type_revenu = self.type_revenu_edit.currentText()
                    if not type_revenu:
                        QMessageBox.warning(self, "Erreur", "Le type de revenu est obligatoire.")
                        return
                    if self.montant_edit.value() <= 0:
                        QMessageBox.warning(self, "Erreur", "Le montant doit être positif.")
                        return

                    ressource = Ressource(
                        code_elevage=code,
                        type_ressource=type_ressource,
                        type_revenu=type_revenu,
                        description=self.description_edit.text().strip() or None,
                        montant_annuel=self.montant_edit.value(),
                        periodicite=self.periodicite_combo.currentText() or None,
                        saisonnalite=self.saisonnalite_edit.text().strip() or None,
                        observations=observations
                    )
                    db.add(ressource)
            else:
                ressource = db.query(Ressource).filter(Ressource.id == self.current_id).first()
                if ressource:
                    ressource.type_ressource = type_ressource
                    ressource.observations = observations

                    if type_ressource == "Animaux":
                        espece = self.espece_edit.text().strip()
                        if not espece:
                            QMessageBox.warning(self, "Erreur", "L'espèce est obligatoire.")
                            return
                        if self.effectif_edit.value() <= 0:
                            QMessageBox.warning(self, "Erreur", "L'effectif doit être positif.")
                            return

                        ressource.espece = espece
                        ressource.effectif = self.effectif_edit.value()
                        ressource.production = self.production_edit.text().strip() or None
                        ressource.quantite_annuelle = self.quantite_edit.value()
                        ressource.destination = self.destination_combo.currentText() or None
                        # Effacer les champs de revenu
                        ressource.type_revenu = None
                        ressource.description = None
                        ressource.montant_annuel = None
                        ressource.periodicite = None
                        ressource.saisonnalite = None
                    else:
                        type_revenu = self.type_revenu_edit.currentText()
                        if not type_revenu:
                            QMessageBox.warning(self, "Erreur", "Le type de revenu est obligatoire.")
                            return
                        if self.montant_edit.value() <= 0:
                            QMessageBox.warning(self, "Erreur", "Le montant doit être positif.")
                            return

                        ressource.type_revenu = type_revenu
                        ressource.description = self.description_edit.text().strip() or None
                        ressource.montant_annuel = self.montant_edit.value()
                        ressource.periodicite = self.periodicite_combo.currentText() or None
                        ressource.saisonnalite = self.saisonnalite_edit.text().strip() or None
                        # Effacer les champs d'animaux
                        ressource.espece = None
                        ressource.effectif = None
                        ressource.production = None
                        ressource.quantite_annuelle = None
                        ressource.destination = None
                else:
                    QMessageBox.warning(self, "Erreur", "Ressource introuvable.")
                    return

            db.commit()
            QMessageBox.information(self, "Succès", "Ressource enregistrée.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ressource.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette ressource ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                ressource = db.query(Ressource).filter(Ressource.id == self.current_id).first()
                if ressource:
                    db.delete(ressource)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Ressource supprimée.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Ressource introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()