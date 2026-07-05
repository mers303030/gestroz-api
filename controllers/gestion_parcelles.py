from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QTabWidget, QHeaderView, QSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur
from controllers.parcelle_controller import ParcelleController

class GestionParcellesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capital foncier et pratiques culturales")
        self.resize(1200, 800)
        layout = QVBoxLayout(self)

        # Filtre par éleveur
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Éleveur :"))
        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        filter_layout.addWidget(self.code_combo)
        layout.addLayout(filter_layout)

        # Onglets
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Onglet Capital foncier
        self.parcelles_tab = QWidget()
        self.setup_parcelles_tab()
        self.tabs.addTab(self.parcelles_tab, "📌 Capital foncier")

        # Onglet Pratiques culturales
        self.pratiques_tab = QWidget()
        self.setup_pratiques_tab()
        self.tabs.addTab(self.pratiques_tab, "🌾 Pratiques culturales")

        self.current_parcelle_id = None
        self.current_fiche_id = None
        self.on_eleveur_changed()

    def get_all_codes(self):
        db = SessionLocal()
        codes = [e.code_elevage for e in db.query(Eleveur).all()]
        db.close()
        return codes

    def on_eleveur_changed(self):
        code = self.code_combo.currentText().strip()
        self.load_parcelles(code)
        self.current_parcelle_id = None
        self.annuler_parcelle()

    # ---------------------- Onglet Capital foncier ----------------------
    def setup_parcelles_tab(self):
        layout = QVBoxLayout(self.parcelles_tab)

        form = QFormLayout()
        self.numero_parcelle = QLineEdit()
        form.addRow("Numéro de parcelle :", self.numero_parcelle)
        self.surface_ha = QLineEdit()
        self.surface_ha.setPlaceholderText("Hectares")
        form.addRow("Surface (ha) :", self.surface_ha)
        self.statut_foncier = QComboBox()
        self.statut_foncier.addItems(["", "Propriété", "Location", "Autre"])
        form.addRow("Statut foncier :", self.statut_foncier)
        self.parcelle_obs = QLineEdit()
        form.addRow("Observations :", self.parcelle_obs)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.btn_add_parcelle = QPushButton("Ajouter parcelle")
        self.btn_add_parcelle.clicked.connect(self.ajouter_parcelle)
        self.btn_modify_parcelle = QPushButton("Modifier parcelle")
        self.btn_modify_parcelle.clicked.connect(self.modifier_parcelle)
        self.btn_delete_parcelle = QPushButton("Supprimer parcelle")
        self.btn_delete_parcelle.clicked.connect(self.supprimer_parcelle)
        self.btn_cancel_parcelle = QPushButton("Annuler")
        self.btn_cancel_parcelle.clicked.connect(self.annuler_parcelle)
        btn_layout.addWidget(self.btn_add_parcelle)
        btn_layout.addWidget(self.btn_modify_parcelle)
        btn_layout.addWidget(self.btn_delete_parcelle)
        btn_layout.addWidget(self.btn_cancel_parcelle)
        layout.addLayout(btn_layout)

        self.table_parcelles = QTableWidget()
        self.table_parcelles.setColumnCount(5)
        self.table_parcelles.setHorizontalHeaderLabels(["ID", "Numéro", "Surface (ha)", "Statut", "Observations"])
        self.table_parcelles.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_parcelles.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_parcelles.itemSelectionChanged.connect(self.on_parcelle_selected)
        layout.addWidget(self.table_parcelles)

    def load_parcelles(self, code_elevage):
        if not code_elevage:
            self.table_parcelles.setRowCount(0)
            return
        parcelles = ParcelleController.get_parcelles_par_eleveur(code_elevage)
        self.table_parcelles.setRowCount(len(parcelles))
        for i, p in enumerate(parcelles):
            self.table_parcelles.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table_parcelles.setItem(i, 1, QTableWidgetItem(p.numero_parcelle))
            self.table_parcelles.setItem(i, 2, QTableWidgetItem(str(p.surface_ha)))
            self.table_parcelles.setItem(i, 3, QTableWidgetItem(p.statut_foncier or ""))
            self.table_parcelles.setItem(i, 4, QTableWidgetItem(p.observations or ""))
        self.table_parcelles.resizeColumnsToContents()

    def on_parcelle_selected(self):
        row = self.table_parcelles.currentRow()
        if row < 0:
            return
        self.current_parcelle_id = int(self.table_parcelles.item(row, 0).text())
        self.numero_parcelle.setText(self.table_parcelles.item(row, 1).text())
        self.surface_ha.setText(self.table_parcelles.item(row, 2).text())
        self.statut_foncier.setCurrentText(self.table_parcelles.item(row, 3).text() or "")
        self.parcelle_obs.setText(self.table_parcelles.item(row, 4).text())
        self.load_parcelle_combo()
        self.load_historique_fiches()
        if self.parcelle_combo.count() > 0:
            self.on_parcelle_combo_changed()

    def annuler_parcelle(self):
        self.current_parcelle_id = None
        self.numero_parcelle.clear()
        self.surface_ha.clear()
        self.statut_foncier.setCurrentIndex(0)
        self.parcelle_obs.clear()
        self.load_parcelles(self.code_combo.currentText().strip())
        self.vider_formulaire_pratiques()

    def ajouter_parcelle(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        if not self.numero_parcelle.text().strip() or not self.surface_ha.text().strip():
            QMessageBox.warning(self, "Erreur", "Numéro et surface obligatoires.")
            return
        try:
            surface = float(self.surface_ha.text())
        except:
            QMessageBox.warning(self, "Erreur", "Surface invalide.")
            return
        data = {
            'code_elevage': code,
            'numero_parcelle': self.numero_parcelle.text().strip(),
            'surface_ha': surface,
            'statut_foncier': self.statut_foncier.currentText() or None,
            'observations': self.parcelle_obs.text().strip() or None
        }
        ok, pid, msg = ParcelleController.ajouter_parcelle(data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_parcelles(code)
            self.annuler_parcelle()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def modifier_parcelle(self):
        if self.current_parcelle_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une parcelle.")
            return
        if not self.numero_parcelle.text().strip() or not self.surface_ha.text().strip():
            QMessageBox.warning(self, "Erreur", "Numéro et surface obligatoires.")
            return
        try:
            surface = float(self.surface_ha.text())
        except:
            QMessageBox.warning(self, "Erreur", "Surface invalide.")
            return
        data = {
            'numero_parcelle': self.numero_parcelle.text().strip(),
            'surface_ha': surface,
            'statut_foncier': self.statut_foncier.currentText() or None,
            'observations': self.parcelle_obs.text().strip() or None
        }
        ok, msg = ParcelleController.modifier_parcelle(self.current_parcelle_id, data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_parcelles(self.code_combo.currentText().strip())
            self.annuler_parcelle()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def supprimer_parcelle(self):
        if self.current_parcelle_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une parcelle.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette parcelle (toutes ses fiches culturales) ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = ParcelleController.supprimer_parcelle(self.current_parcelle_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_parcelles(self.code_combo.currentText().strip())
                self.annuler_parcelle()
            else:
                QMessageBox.warning(self, "Erreur", msg)

    # ---------------------- Onglet Pratiques culturales ----------------------
    def setup_pratiques_tab(self):
        layout = QVBoxLayout(self.pratiques_tab)

        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Parcelle :"))
        self.parcelle_combo = QComboBox()
        self.parcelle_combo.currentIndexChanged.connect(self.on_parcelle_combo_changed)
        select_layout.addWidget(self.parcelle_combo)
        select_layout.addWidget(QLabel("Année :"))
        self.annee_spin = QSpinBox()
        self.annee_spin.setRange(2000, 2100)
        self.annee_spin.setValue(QDate.currentDate().year())
        self.annee_spin.valueChanged.connect(self.charger_fiche_par_annee)
        select_layout.addWidget(self.annee_spin)
        select_layout.addStretch()
        layout.addLayout(select_layout)

        form_scroll = QWidget()
        form_layout = QFormLayout(form_scroll)
        form_layout.setSpacing(10)

        form_layout.addRow(QLabel("<b>Culture</b>"))
        self.culture = QLineEdit()
        form_layout.addRow("Culture :", self.culture)

        form_layout.addRow(QLabel("<b>Labour</b>"))
        self.date_labour = QDateEdit()
        self.date_labour.setCalendarPopup(True)
        self.date_labour.setDate(QDate.currentDate())
        self.date_labour.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date :", self.date_labour)
        self.moyen_labour = QComboBox()
        self.moyen_labour.addItems(["", "Attelage", "Tracteur", "Manuel"])
        form_layout.addRow("Moyen :", self.moyen_labour)

        form_layout.addRow(QLabel("<b>Semis</b>"))
        self.date_semis = QDateEdit()
        self.date_semis.setCalendarPopup(True)
        self.date_semis.setDate(QDate.currentDate())
        self.date_semis.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date :", self.date_semis)
        self.dose_semis = QLineEdit()
        self.dose_semis.setPlaceholderText("kg/ha")
        form_layout.addRow("Dose semis :", self.dose_semis)
        self.moyen_semis = QComboBox()
        self.moyen_semis.addItems(["", "Manuel", "Mécanique (semoir)"])
        form_layout.addRow("Moyen :", self.moyen_semis)

        form_layout.addRow(QLabel("<b>Engrais de fond</b>"))
        self.type_engrais_fond = QComboBox()
        self.type_engrais_fond.addItems(["", "Fumier", "Compost", "Chimique (NPK)", "Urée"])
        form_layout.addRow("Type :", self.type_engrais_fond)
        self.dose_engrais_fond = QLineEdit()
        self.dose_engrais_fond.setPlaceholderText("tonnes/ha ou kg/ha")
        form_layout.addRow("Dose :", self.dose_engrais_fond)

        form_layout.addRow(QLabel("<b>Désherbage</b>"))
        self.desherbage_type = QComboBox()
        self.desherbage_type.addItems(["", "Mécanique", "Chimique"])
        self.desherbage_type.currentTextChanged.connect(self.on_desherbage_type_changed)
        form_layout.addRow("Type :", self.desherbage_type)
        self.desherbage_produit = QLineEdit()
        self.desherbage_produit.setPlaceholderText("Nom produit (si chimique)")
        form_layout.addRow("Produit :", self.desherbage_produit)
        self.desherbage_dose = QLineEdit()
        self.desherbage_dose.setPlaceholderText("Dose")
        form_layout.addRow("Dose :", self.desherbage_dose)
        self.desherbage_date = QDateEdit()
        self.desherbage_date.setCalendarPopup(True)
        self.desherbage_date.setDate(QDate.currentDate())
        self.desherbage_date.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date :", self.desherbage_date)

        form_layout.addRow(QLabel("<b>Engrais de couverture</b>"))
        self.engrais_couverture_date = QDateEdit()
        self.engrais_couverture_date.setCalendarPopup(True)
        self.engrais_couverture_date.setDate(QDate.currentDate())
        self.engrais_couverture_date.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date :", self.engrais_couverture_date)
        self.engrais_couverture_type = QComboBox()
        self.engrais_couverture_type.addItems(["", "Urée", "NPK", "Autre"])
        form_layout.addRow("Type :", self.engrais_couverture_type)
        self.engrais_couverture_dose = QLineEdit()
        self.engrais_couverture_dose.setPlaceholderText("kg/ha")
        form_layout.addRow("Dose :", self.engrais_couverture_dose)

        form_layout.addRow(QLabel("<b>Récolte</b>"))
        self.date_recolte = QDateEdit()
        self.date_recolte.setCalendarPopup(True)
        self.date_recolte.setDate(QDate.currentDate())
        self.date_recolte.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date :", self.date_recolte)
        self.moyen_recolte = QComboBox()
        self.moyen_recolte.addItems(["", "Machine (moissonneuse)", "Faucille", "Manuelle", "Autre"])
        form_layout.addRow("Moyen :", self.moyen_recolte)
        self.rendement_grain = QLineEdit()
        self.rendement_grain.setPlaceholderText("tonnes")
        form_layout.addRow("Rendement grain (t) :", self.rendement_grain)
        self.rendement_paille = QLineEdit()
        self.rendement_paille.setPlaceholderText("tonnes")
        form_layout.addRow("Rendement paille (t) :", self.rendement_paille)
        self.rendement_foin = QLineEdit()
        self.rendement_foin.setPlaceholderText("tonnes (foin/ensilage)")
        form_layout.addRow("Rendement foin/ensilage (t) :", self.rendement_foin)

        self.fiche_obs = QLineEdit()
        form_layout.addRow("Observations :", self.fiche_obs)

        layout.addWidget(form_scroll)

        btn_layout = QHBoxLayout()
        self.btn_save_fiche = QPushButton("Enregistrer la fiche")
        self.btn_save_fiche.clicked.connect(self.enregistrer_fiche)
        self.btn_delete_fiche = QPushButton("Supprimer cette fiche")
        self.btn_delete_fiche.clicked.connect(self.supprimer_fiche)
        self.btn_cancel_fiche = QPushButton("Annuler")
        self.btn_cancel_fiche.clicked.connect(self.vider_formulaire_pratiques)
        btn_layout.addWidget(self.btn_save_fiche)
        btn_layout.addWidget(self.btn_delete_fiche)
        btn_layout.addWidget(self.btn_cancel_fiche)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("Historique des fiches culturales :"))
        self.table_fiches = QTableWidget()
        self.table_fiches.setColumnCount(5)
        self.table_fiches.setHorizontalHeaderLabels(["Année", "Culture", "Date semis", "Date récolte", "Rendement grain (t)"])
        self.table_fiches.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_fiches.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_fiches.itemSelectionChanged.connect(self.on_historique_selected)
        layout.addWidget(self.table_fiches)

    def on_desherbage_type_changed(self):
        enabled = (self.desherbage_type.currentText() == "Chimique")
        self.desherbage_produit.setEnabled(enabled)
        self.desherbage_dose.setEnabled(enabled)
        self.desherbage_date.setEnabled(enabled)
        if not enabled:
            self.desherbage_produit.clear()
            self.desherbage_dose.clear()

    def load_parcelle_combo(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.parcelle_combo.clear()
            return
        parcelles = ParcelleController.get_parcelles_par_eleveur(code)
        self.parcelle_combo.clear()
        for p in parcelles:
            self.parcelle_combo.addItem(f"{p.numero_parcelle} - {p.surface_ha} ha", p.id)
        if self.parcelle_combo.count() > 0:
            self.parcelle_combo.setCurrentIndex(0)
        else:
            self.vider_formulaire_pratiques()

    def on_parcelle_combo_changed(self):
        self.current_parcelle_id = self.parcelle_combo.currentData()
        self.charger_fiche_par_annee()

    def charger_fiche_par_annee(self):
        if self.current_parcelle_id is None:
            self.vider_formulaire_pratiques()
            return
        annee = str(self.annee_spin.value())
        fiche = ParcelleController.get_fiche_par_parcelle_annee(self.current_parcelle_id, annee)
        if fiche:
            self.current_fiche_id = fiche.id
            self.charger_fiche_dans_formulaire(fiche)
        else:
            self.current_fiche_id = None
            self.vider_formulaire_pratiques()
        self.load_historique_fiches()

    def charger_fiche_dans_formulaire(self, f):
        self.culture.setText(f.culture or "")
        if f.date_labour:
            self.date_labour.setDate(QDate.fromString(f.date_labour, "yyyy-MM-dd"))
        self.moyen_labour.setCurrentText(f.moyen_labour or "")
        if f.date_semis:
            self.date_semis.setDate(QDate.fromString(f.date_semis, "yyyy-MM-dd"))
        self.dose_semis.setText(f.dose_semis or "")
        self.moyen_semis.setCurrentText(f.moyen_semis or "")
        self.type_engrais_fond.setCurrentText(f.type_engrais_fond or "")
        self.dose_engrais_fond.setText(f.dose_engrais_fond or "")
        self.desherbage_type.setCurrentText(f.desherbage_type or "")
        self.desherbage_produit.setText(f.desherbage_produit or "")
        self.desherbage_dose.setText(f.desherbage_dose or "")
        if f.desherbage_date:
            self.desherbage_date.setDate(QDate.fromString(f.desherbage_date, "yyyy-MM-dd"))
        if f.engrais_couverture_date:
            self.engrais_couverture_date.setDate(QDate.fromString(f.engrais_couverture_date, "yyyy-MM-dd"))
        self.engrais_couverture_type.setCurrentText(f.engrais_couverture_type or "")
        self.engrais_couverture_dose.setText(f.engrais_couverture_dose or "")
        if f.date_recolte:
            self.date_recolte.setDate(QDate.fromString(f.date_recolte, "yyyy-MM-dd"))
        self.moyen_recolte.setCurrentText(f.moyen_recolte or "")
        self.rendement_grain.setText(str(f.rendement_grain) if f.rendement_grain else "")
        self.rendement_paille.setText(str(f.rendement_paille) if f.rendement_paille else "")
        self.rendement_foin.setText(str(f.rendement_foin) if f.rendement_foin else "")
        self.fiche_obs.setText(f.observations or "")

    def vider_formulaire_pratiques(self):
        self.culture.clear()
        self.date_labour.setDate(QDate.currentDate())
        self.moyen_labour.setCurrentIndex(0)
        self.date_semis.setDate(QDate.currentDate())
        self.dose_semis.clear()
        self.moyen_semis.setCurrentIndex(0)
        self.type_engrais_fond.setCurrentIndex(0)
        self.dose_engrais_fond.clear()
        self.desherbage_type.setCurrentIndex(0)
        self.desherbage_produit.clear()
        self.desherbage_dose.clear()
        self.desherbage_date.setDate(QDate.currentDate())
        self.engrais_couverture_date.setDate(QDate.currentDate())
        self.engrais_couverture_type.setCurrentIndex(0)
        self.engrais_couverture_dose.clear()
        self.date_recolte.setDate(QDate.currentDate())
        self.moyen_recolte.setCurrentIndex(0)
        self.rendement_grain.clear()
        self.rendement_paille.clear()
        self.rendement_foin.clear()
        self.fiche_obs.clear()
        self.current_fiche_id = None

    def load_historique_fiches(self):
        if self.current_parcelle_id is None:
            self.table_fiches.setRowCount(0)
            return
        fiches = ParcelleController.get_all_fiches_par_parcelle(self.current_parcelle_id)
        self.table_fiches.setRowCount(len(fiches))
        for i, f in enumerate(fiches):
            self.table_fiches.setItem(i, 0, QTableWidgetItem(f.annee))
            self.table_fiches.setItem(i, 1, QTableWidgetItem(f.culture or ""))
            self.table_fiches.setItem(i, 2, QTableWidgetItem(f.date_semis or ""))
            self.table_fiches.setItem(i, 3, QTableWidgetItem(f.date_recolte or ""))
            grain = f"{f.rendement_grain:.2f}" if f.rendement_grain else ""
            self.table_fiches.setItem(i, 4, QTableWidgetItem(grain))
        self.table_fiches.resizeColumnsToContents()

    def on_historique_selected(self):
        row = self.table_fiches.currentRow()
        if row < 0:
            return
        annee = self.table_fiches.item(row, 0).text()
        self.annee_spin.setValue(int(annee))
        self.charger_fiche_par_annee()

    def enregistrer_fiche(self):
        if self.current_parcelle_id is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une parcelle.")
            return
        annee = str(self.annee_spin.value())
        data = {
            'parcelle_id': self.current_parcelle_id,
            'annee': annee,
            'culture': self.culture.text().strip() or None,
            'date_labour': self.date_labour.date().toString("yyyy-MM-dd") if self.moyen_labour.currentIndex() > 0 else None,
            'moyen_labour': self.moyen_labour.currentText() or None,
            'date_semis': self.date_semis.date().toString("yyyy-MM-dd") if self.date_semis.date().toPython() else None,
            'dose_semis': self.dose_semis.text().strip() or None,
            'moyen_semis': self.moyen_semis.currentText() or None,
            'type_engrais_fond': self.type_engrais_fond.currentText() or None,
            'dose_engrais_fond': self.dose_engrais_fond.text().strip() or None,
            'desherbage_type': self.desherbage_type.currentText() or None,
            'desherbage_produit': self.desherbage_produit.text().strip() or None,
            'desherbage_dose': self.desherbage_dose.text().strip() or None,
            'desherbage_date': self.desherbage_date.date().toString("yyyy-MM-dd") if self.desherbage_type.currentText() == "Chimique" else None,
            'engrais_couverture_date': self.engrais_couverture_date.date().toString("yyyy-MM-dd") if self.engrais_couverture_type.currentIndex() > 0 else None,
            'engrais_couverture_type': self.engrais_couverture_type.currentText() or None,
            'engrais_couverture_dose': self.engrais_couverture_dose.text().strip() or None,
            'date_recolte': self.date_recolte.date().toString("yyyy-MM-dd") if self.date_recolte.date().toPython() else None,
            'moyen_recolte': self.moyen_recolte.currentText() or None,
            'rendement_grain': float(self.rendement_grain.text()) if self.rendement_grain.text() else None,
            'rendement_paille': float(self.rendement_paille.text()) if self.rendement_paille.text() else None,
            'rendement_foin': float(self.rendement_foin.text()) if self.rendement_foin.text() else None,
            'observations': self.fiche_obs.text().strip() or None
        }
        if self.current_fiche_id:
            ok, msg = ParcelleController.modifier_fiche(self.current_fiche_id, data)
        else:
            ok, msg = ParcelleController.ajouter_fiche(data)
        if ok:
            QMessageBox.information(self, "Succès", msg)
            self.load_historique_fiches()
            self.charger_fiche_par_annee()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def supprimer_fiche(self):
        if self.current_fiche_id is None:
            QMessageBox.warning(self, "Erreur", "Aucune fiche sélectionnée.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette fiche culturale ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = ParcelleController.supprimer_fiche(self.current_fiche_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.current_fiche_id = None
                self.vider_formulaire_pratiques()
                self.load_historique_fiches()
            else:
                QMessageBox.warning(self, "Erreur", msg)