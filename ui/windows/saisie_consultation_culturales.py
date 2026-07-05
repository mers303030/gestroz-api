# ui/windows/saisie_consultation_culturales.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Parcelle, FicheCulturale
from sqlalchemy.orm import joinedload

class SaisieConsultationCulturalesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des pratiques culturales")
        self.resize(1300, 800)
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

        self.parcelle_combo = QComboBox()
        self.parcelle_combo.setEnabled(False)
        form_layout.addRow(QLabel("Parcelle :"), self.parcelle_combo)

        self.annee_edit = QLineEdit()
        self.annee_edit.setPlaceholderText("2025")
        form_layout.addRow(QLabel("Année :"), self.annee_edit)

        self.culture_edit = QLineEdit()
        self.culture_edit.setPlaceholderText("Culture principale")
        form_layout.addRow(QLabel("Culture :"), self.culture_edit)

        # Labour
        self.labour_profondeur = QComboBox()
        self.labour_profondeur.addItems(["", "Profond (>25 cm)", "Moyen (15-25 cm)", "Superficiel (<15 cm)"])
        form_layout.addRow(QLabel("Labour (profondeur) :"), self.labour_profondeur)

        self.labour_moyen = QComboBox()
        self.labour_moyen.addItems(["", "Tracteur", "Attelage", "Manuel"])
        form_layout.addRow(QLabel("Moyen de labour :"), self.labour_moyen)

        # Engrais de fond
        self.engrais_fond_date = QDateEdit()
        self.engrais_fond_date.setCalendarPopup(True)
        self.engrais_fond_date.setDate(QDate.currentDate())
        self.engrais_fond_date.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Engrais fond - Date :"), self.engrais_fond_date)

        self.engrais_fond_type = QLineEdit()
        self.engrais_fond_type.setPlaceholderText("Type (NPK, Urée, Fumier, ...)")
        form_layout.addRow(QLabel("Type :"), self.engrais_fond_type)

        self.engrais_fond_dose = QLineEdit()
        self.engrais_fond_dose.setPlaceholderText("Dose (kg/ha ou tonnes/ha)")
        form_layout.addRow(QLabel("Dose :"), self.engrais_fond_dose)

        # Engrais de couverture
        self.engrais_couv_date = QDateEdit()
        self.engrais_couv_date.setCalendarPopup(True)
        self.engrais_couv_date.setDate(QDate.currentDate())
        self.engrais_couv_date.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Engrais couverture - Date :"), self.engrais_couv_date)

        self.engrais_couv_type = QLineEdit()
        self.engrais_couv_type.setPlaceholderText("Type (NPK, Urée, ...)")
        form_layout.addRow(QLabel("Type :"), self.engrais_couv_type)

        self.engrais_couv_dose = QLineEdit()
        self.engrais_couv_dose.setPlaceholderText("Dose (kg/ha)")
        form_layout.addRow(QLabel("Dose :"), self.engrais_couv_dose)

        # Traitement phytosanitaire
        self.phytosanitaire_date = QDateEdit()
        self.phytosanitaire_date.setCalendarPopup(True)
        self.phytosanitaire_date.setDate(QDate.currentDate())
        self.phytosanitaire_date.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Phytosanitaire - Date :"), self.phytosanitaire_date)

        self.phytosanitaire_type = QLineEdit()
        self.phytosanitaire_type.setPlaceholderText("Type (herbicide, fongicide, ...)")
        form_layout.addRow(QLabel("Type :"), self.phytosanitaire_type)

        self.phytosanitaire_dose = QLineEdit()
        self.phytosanitaire_dose.setPlaceholderText("Dose")
        form_layout.addRow(QLabel("Dose :"), self.phytosanitaire_dose)

        # Récolte
        self.recolte_type = QComboBox()
        self.recolte_type.addItems(["", "Grain + Paille", "Foin", "Ensilage", "Pâturage sur pied"])
        self.recolte_type.currentTextChanged.connect(self.on_recolte_type_changed)
        form_layout.addRow(QLabel("Type de récolte :"), self.recolte_type)

        self.recolte_grain = QLineEdit()
        self.recolte_grain.setPlaceholderText("Rendement grain (qx/ha)")
        form_layout.addRow(QLabel("Rendement grain (qx/ha) :"), self.recolte_grain)

        self.recolte_paille = QLineEdit()
        self.recolte_paille.setPlaceholderText("Nombre de bottes / ha (paille)")
        form_layout.addRow(QLabel("Bottes de paille/ha :"), self.recolte_paille)

        self.recolte_foin = QLineEdit()
        self.recolte_foin.setPlaceholderText("Nombre de bottes / ha (foin)")
        form_layout.addRow(QLabel("Bottes de foin/ha :"), self.recolte_foin)

        self.recolte_ensilage = QLineEdit()
        self.recolte_ensilage.setPlaceholderText("Tonnes/ha")
        form_layout.addRow(QLabel("Ensilage (tonnes/ha) :"), self.recolte_ensilage)

        self.recolte_paturage_debut = QDateEdit()
        self.recolte_paturage_debut.setCalendarPopup(True)
        self.recolte_paturage_debut.setDate(QDate.currentDate())
        self.recolte_paturage_debut.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Pâturage - Début :"), self.recolte_paturage_debut)

        self.recolte_paturage_fin = QDateEdit()
        self.recolte_paturage_fin.setCalendarPopup(True)
        self.recolte_paturage_fin.setDate(QDate.currentDate())
        self.recolte_paturage_fin.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Pâturage - Fin :"), self.recolte_paturage_fin)

        self.obs_edit = QLineEdit()
        self.obs_edit.setPlaceholderText("Observations (optionnel)")
        form_layout.addRow(QLabel("Observations :"), self.obs_edit)

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

        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Parcelle", "Année", "Culture",
            "Labour", "Engrais fond", "Engrais couv",
            "Phytosanitaire", "Type récolte",
            "Rdt grain (qx/ha)", "Bottes/ha", "Observations"
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
        self.on_recolte_type_changed()

    # ==================== MÉTHODES ====================
    def get_all_codes(self):
        db = SessionLocal()
        try:
            return [e.code_elevage for e in db.query(Eleveur).all()]
        finally:
            db.close()

    def on_recolte_type_changed(self):
        type_ = self.recolte_type.currentText()
        self.recolte_grain.setVisible(type_ == "Grain + Paille")
        self.recolte_paille.setVisible(type_ == "Grain + Paille")
        self.recolte_foin.setVisible(type_ == "Foin")
        self.recolte_ensilage.setVisible(type_ == "Ensilage")
        self.recolte_paturage_debut.setVisible(type_ == "Pâturage sur pied")
        self.recolte_paturage_fin.setVisible(type_ == "Pâturage sur pied")

    def on_eleveur_changed(self):
        code = self.code_combo.currentText().strip()
        self.parcelle_combo.clear()
        self.parcelle_combo.setEnabled(False)
        self.load_table()

        if not code:
            return

        db = SessionLocal()
        try:
            parcelles = db.query(Parcelle).filter(Parcelle.code_elevage == code).all()
            for p in parcelles:
                self.parcelle_combo.addItem(f"{p.numero_parcelle} ({p.surface_ha} ha)", p.id)
            self.parcelle_combo.setEnabled(len(parcelles) > 0)
        finally:
            db.close()

    def load_table(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            fiches = db.query(FicheCulturale).options(joinedload(FicheCulturale.parcelle))\
                .join(Parcelle).filter(Parcelle.code_elevage == code)\
                .order_by(FicheCulturale.annee.desc()).all()
        finally:
            db.close()

        self.table.setRowCount(len(fiches))
        for i, f in enumerate(fiches):
            self.table.setItem(i, 0, QTableWidgetItem(str(f.id)))
            parcelle_nom = f.parcelle.numero_parcelle if f.parcelle else ""
            self.table.setItem(i, 1, QTableWidgetItem(parcelle_nom))
            self.table.setItem(i, 2, QTableWidgetItem(f.annee))
            self.table.setItem(i, 3, QTableWidgetItem(f.culture or ""))
            # Labour
            labour = f"{f.labour_profondeur or ''} ({f.moyen_labour or ''})".strip(" ()")
            self.table.setItem(i, 4, QTableWidgetItem(labour))
            # Engrais fond
            engrais_fond = f"{f.type_engrais_fond or ''} {f.dose_engrais_fond or ''}".strip()
            self.table.setItem(i, 5, QTableWidgetItem(engrais_fond))
            # Engrais couverture (corrigé)
            engrais_couv = f"{f.type_engrais_couverture or ''} {f.dose_engrais_couverture or ''}".strip()
            self.table.setItem(i, 6, QTableWidgetItem(engrais_couv))
            # Phytosanitaire
            phyto = f"{f.type_phytosanitaire or ''} {f.dose_phytosanitaire or ''}".strip()
            self.table.setItem(i, 7, QTableWidgetItem(phyto))
            self.table.setItem(i, 8, QTableWidgetItem(f.type_recolte or ""))
            self.table.setItem(i, 9, QTableWidgetItem(f"{f.rendement_grain:.1f}" if f.rendement_grain else ""))
            bottes = f"{f.rendement_paille:.0f}" if f.rendement_paille else ""
            if not bottes and f.rendement_foin:
                bottes = f"{f.rendement_foin:.0f}"
            self.table.setItem(i, 10, QTableWidgetItem(bottes))
            self.table.setItem(i, 11, QTableWidgetItem(f.observations or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())

        parcelle_nom = self.table.item(row, 1).text()
        for i in range(self.parcelle_combo.count()):
            if self.parcelle_combo.itemText(i).startswith(parcelle_nom):
                self.parcelle_combo.setCurrentIndex(i)
                break

        self.annee_edit.setText(self.table.item(row, 2).text())
        self.culture_edit.setText(self.table.item(row, 3).text())

        labour_text = self.table.item(row, 4).text()
        if labour_text:
            if '(' in labour_text and ')' in labour_text:
                profondeur = labour_text[:labour_text.find('(')].strip()
                moyen = labour_text[labour_text.find('(')+1:labour_text.find(')')].strip()
                self.labour_profondeur.setCurrentText(profondeur)
                self.labour_moyen.setCurrentText(moyen)
            else:
                self.labour_profondeur.setCurrentText(labour_text)

        engrais_fond = self.table.item(row, 5).text()
        if engrais_fond:
            self.engrais_fond_type.setText(engrais_fond)

        engrais_couv = self.table.item(row, 6).text()
        if engrais_couv:
            self.engrais_couv_type.setText(engrais_couv)

        phyto = self.table.item(row, 7).text()
        if phyto:
            self.phytosanitaire_type.setText(phyto)

        self.recolte_type.setCurrentText(self.table.item(row, 8).text())
        self.recolte_grain.setText(self.table.item(row, 9).text())
        bottes = self.table.item(row, 10).text()
        self.recolte_paille.setText(bottes)
        self.recolte_foin.setText(bottes)
        self.obs_edit.setText(self.table.item(row, 11).text())
        self.btn_save.setText("Mettre à jour")

    def nouveau(self):
        self.current_id = None
        self.parcelle_combo.setCurrentIndex(-1)
        self.annee_edit.setText(str(QDate.currentDate().year()))
        self.culture_edit.clear()
        self.labour_profondeur.setCurrentIndex(0)
        self.labour_moyen.setCurrentIndex(0)
        self.engrais_fond_date.setDate(QDate.currentDate())
        self.engrais_fond_type.clear()
        self.engrais_fond_dose.clear()
        self.engrais_couv_date.setDate(QDate.currentDate())
        self.engrais_couv_type.clear()
        self.engrais_couv_dose.clear()
        self.phytosanitaire_date.setDate(QDate.currentDate())
        self.phytosanitaire_type.clear()
        self.phytosanitaire_dose.clear()
        self.recolte_type.setCurrentIndex(0)
        self.recolte_grain.clear()
        self.recolte_paille.clear()
        self.recolte_foin.clear()
        self.recolte_ensilage.clear()
        self.recolte_paturage_debut.setDate(QDate.currentDate())
        self.recolte_paturage_fin.setDate(QDate.currentDate())
        self.obs_edit.clear()
        self.btn_save.setText("Sauvegarder")
        self.on_recolte_type_changed()

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        parcelle_id = self.parcelle_combo.currentData()
        if not parcelle_id:
            QMessageBox.warning(self, "Erreur", "Choisissez une parcelle.")
            return

        annee = self.annee_edit.text().strip()
        if not annee:
            QMessageBox.warning(self, "Erreur", "L'année est obligatoire.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                fiche = FicheCulturale(
                    parcelle_id=parcelle_id,
                    annee=annee,
                    culture=self.culture_edit.text().strip() or None,
                    labour_profondeur=self.labour_profondeur.currentText() or None,
                    moyen_labour=self.labour_moyen.currentText() or None,
                    date_engrais_fond=self.engrais_fond_date.date().toString("yyyy-MM-dd"),
                    type_engrais_fond=self.engrais_fond_type.text().strip() or None,
                    dose_engrais_fond=self.engrais_fond_dose.text().strip() or None,
                    date_engrais_couverture=self.engrais_couv_date.date().toString("yyyy-MM-dd"),
                    type_engrais_couverture=self.engrais_couv_type.text().strip() or None,
                    dose_engrais_couverture=self.engrais_couv_dose.text().strip() or None,
                    date_phytosanitaire=self.phytosanitaire_date.date().toString("yyyy-MM-dd"),
                    type_phytosanitaire=self.phytosanitaire_type.text().strip() or None,
                    dose_phytosanitaire=self.phytosanitaire_dose.text().strip() or None,
                    type_recolte=self.recolte_type.currentText() or None,
                    rendement_grain=float(self.recolte_grain.text()) if self.recolte_grain.text() else None,
                    rendement_paille=float(self.recolte_paille.text()) if self.recolte_paille.text() else None,
                    rendement_foin=float(self.recolte_foin.text()) if self.recolte_foin.text() else None,
                    rendement_ensilage=float(self.recolte_ensilage.text()) if self.recolte_ensilage.text() else None,
                    paturage_debut=self.recolte_paturage_debut.date().toString("yyyy-MM-dd") if self.recolte_type.currentText() == "Pâturage sur pied" else None,
                    paturage_fin=self.recolte_paturage_fin.date().toString("yyyy-MM-dd") if self.recolte_type.currentText() == "Pâturage sur pied" else None,
                    observations=self.obs_edit.text().strip() or None
                )
                db.add(fiche)
            else:
                fiche = db.query(FicheCulturale).filter(FicheCulturale.id == self.current_id).first()
                if fiche:
                    fiche.parcelle_id = parcelle_id
                    fiche.annee = annee
                    fiche.culture = self.culture_edit.text().strip() or None
                    fiche.labour_profondeur = self.labour_profondeur.currentText() or None
                    fiche.moyen_labour = self.labour_moyen.currentText() or None
                    fiche.date_engrais_fond = self.engrais_fond_date.date().toString("yyyy-MM-dd")
                    fiche.type_engrais_fond = self.engrais_fond_type.text().strip() or None
                    fiche.dose_engrais_fond = self.engrais_fond_dose.text().strip() or None
                    fiche.date_engrais_couverture = self.engrais_couv_date.date().toString("yyyy-MM-dd")
                    fiche.type_engrais_couverture = self.engrais_couv_type.text().strip() or None
                    fiche.dose_engrais_couverture = self.engrais_couv_dose.text().strip() or None
                    fiche.date_phytosanitaire = self.phytosanitaire_date.date().toString("yyyy-MM-dd")
                    fiche.type_phytosanitaire = self.phytosanitaire_type.text().strip() or None
                    fiche.dose_phytosanitaire = self.phytosanitaire_dose.text().strip() or None
                    fiche.type_recolte = self.recolte_type.currentText() or None
                    fiche.rendement_grain = float(self.recolte_grain.text()) if self.recolte_grain.text() else None
                    fiche.rendement_paille = float(self.recolte_paille.text()) if self.recolte_paille.text() else None
                    fiche.rendement_foin = float(self.recolte_foin.text()) if self.recolte_foin.text() else None
                    fiche.rendement_ensilage = float(self.recolte_ensilage.text()) if self.recolte_ensilage.text() else None
                    fiche.paturage_debut = self.recolte_paturage_debut.date().toString("yyyy-MM-dd") if self.recolte_type.currentText() == "Pâturage sur pied" else None
                    fiche.paturage_fin = self.recolte_paturage_fin.date().toString("yyyy-MM-dd") if self.recolte_type.currentText() == "Pâturage sur pied" else None
                    fiche.observations = self.obs_edit.text().strip() or None
                else:
                    QMessageBox.warning(self, "Erreur", "Fiche introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Fiche culturale enregistrée.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une fiche.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette fiche ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                fiche = db.query(FicheCulturale).filter(FicheCulturale.id == self.current_id).first()
                if fiche:
                    db.delete(fiche)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Fiche supprimée.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Fiche introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()