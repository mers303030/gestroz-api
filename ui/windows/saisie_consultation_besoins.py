# ui/windows/saisie_consultation_besoins.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import BesoinNutritionnel

class SaisieConsultationBesoinWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des besoins nutritionnels")
        self.resize(1200, 700)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE (HAUT) ====================
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        # Race
        self.race_edit = QLineEdit()
        self.race_edit.setPlaceholderText("Race (ex: Oulmès-Zaer)")
        form_layout.addRow(QLabel("Race :"), self.race_edit)

        # Catégorie
        self.categorie_combo = QComboBox()
        self.categorie_combo.addItems(["Veau", "Velle", "Génisse", "Taurillon", "Vache", "Géniteur"])
        form_layout.addRow(QLabel("Catégorie :"), self.categorie_combo)

        # Stade
        self.stade_combo = QComboBox()
        self.stade_combo.addItems(["Croissance", "Gestation", "Lactation", "Tarissement", "Indifférent"])
        form_layout.addRow(QLabel("Stade :"), self.stade_combo)

        # Poids min
        self.poids_min = QDoubleSpinBox()
        self.poids_min.setRange(0, 2000)
        self.poids_min.setSingleStep(1)
        self.poids_min.setSuffix(" kg")
        form_layout.addRow(QLabel("Poids min :"), self.poids_min)

        # Poids max
        self.poids_max = QDoubleSpinBox()
        self.poids_max.setRange(0, 2000)
        self.poids_max.setSingleStep(1)
        self.poids_max.setSuffix(" kg")
        form_layout.addRow(QLabel("Poids max :"), self.poids_max)

        # Production min
        self.prod_min = QDoubleSpinBox()
        self.prod_min.setRange(0, 100)
        self.prod_min.setSingleStep(0.5)
        self.prod_min.setSuffix(" kg/j")
        form_layout.addRow(QLabel("Production min (lait ou viande) :"), self.prod_min)

        # Production max
        self.prod_max = QDoubleSpinBox()
        self.prod_max.setRange(0, 100)
        self.prod_max.setSingleStep(0.5)
        self.prod_max.setSuffix(" kg/j")
        form_layout.addRow(QLabel("Production max :"), self.prod_max)

        # UFL
        self.ufl_edit = QDoubleSpinBox()
        self.ufl_edit.setRange(0, 10)
        self.ufl_edit.setSingleStep(0.01)
        self.ufl_edit.setSuffix(" UFL")
        form_layout.addRow(QLabel("UFL :"), self.ufl_edit)

        # UFV
        self.ufv_edit = QDoubleSpinBox()
        self.ufv_edit.setRange(0, 10)
        self.ufv_edit.setSingleStep(0.01)
        self.ufv_edit.setSuffix(" UFV")
        form_layout.addRow(QLabel("UFV :"), self.ufv_edit)

        # PDI
        self.pdi_edit = QDoubleSpinBox()
        self.pdi_edit.setRange(0, 500)
        self.pdi_edit.setSingleStep(0.5)
        self.pdi_edit.setSuffix(" g")
        form_layout.addRow(QLabel("PDI :"), self.pdi_edit)

        # Calcium
        self.ca_edit = QDoubleSpinBox()
        self.ca_edit.setRange(0, 100)
        self.ca_edit.setSingleStep(0.01)
        self.ca_edit.setSuffix(" %")
        form_layout.addRow(QLabel("Calcium (%) :"), self.ca_edit)

        # Phosphore
        self.p_edit = QDoubleSpinBox()
        self.p_edit.setRange(0, 100)
        self.p_edit.setSingleStep(0.01)
        self.p_edit.setSuffix(" %")
        form_layout.addRow(QLabel("Phosphore (%) :"), self.p_edit)

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
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "ID", "Race", "Catégorie", "Stade",
            "Poids min", "Poids max", "Prod min", "Prod max",
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

    # ==================== MÉTHODES ====================
    def load_table(self):
        db = SessionLocal()
        try:
            besoins = db.query(BesoinNutritionnel).order_by(BesoinNutritionnel.race).all()
        finally:
            db.close()

        self.table.setRowCount(len(besoins))
        for i, b in enumerate(besoins):
            self.table.setItem(i, 0, QTableWidgetItem(str(b.id)))
            self.table.setItem(i, 1, QTableWidgetItem(b.race))
            self.table.setItem(i, 2, QTableWidgetItem(b.categorie))
            self.table.setItem(i, 3, QTableWidgetItem(b.stade or ""))
            self.table.setItem(i, 4, QTableWidgetItem(f"{b.poids_min:.0f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{b.poids_max:.0f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{b.production_min:.1f}" if b.production_min is not None else ""))
            self.table.setItem(i, 7, QTableWidgetItem(f"{b.production_max:.1f}" if b.production_max is not None else ""))
            self.table.setItem(i, 8, QTableWidgetItem(f"{b.ufl:.2f}"))
            self.table.setItem(i, 9, QTableWidgetItem(f"{b.ufv:.2f}"))
            self.table.setItem(i, 10, QTableWidgetItem(f"{b.pdi:.1f}"))
            self.table.setItem(i, 11, QTableWidgetItem(f"{b.calcium:.2f}"))
            self.table.setItem(i, 12, QTableWidgetItem(f"{b.phosphore:.2f}"))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        self.race_edit.setText(self.table.item(row, 1).text())
        self.categorie_combo.setCurrentText(self.table.item(row, 2).text())
        self.stade_combo.setCurrentText(self.table.item(row, 3).text())
        self.poids_min.setValue(float(self.table.item(row, 4).text()))
        self.poids_max.setValue(float(self.table.item(row, 5).text()))
        self.prod_min.setValue(float(self.table.item(row, 6).text()) if self.table.item(row, 6).text() else 0)
        self.prod_max.setValue(float(self.table.item(row, 7).text()) if self.table.item(row, 7).text() else 0)
        self.ufl_edit.setValue(float(self.table.item(row, 8).text()))
        self.ufv_edit.setValue(float(self.table.item(row, 9).text()))
        self.pdi_edit.setValue(float(self.table.item(row, 10).text()))
        self.ca_edit.setValue(float(self.table.item(row, 11).text()))
        self.p_edit.setValue(float(self.table.item(row, 12).text()))
        self.obs_edit.setText("")  # les observations ne sont pas dans le tableau, on les laisse vides (on pourrait les récupérer depuis la base)
        self.btn_save.setText("Mettre à jour")

    def nouveau(self):
        self.current_id = None
        self.race_edit.clear()
        self.categorie_combo.setCurrentIndex(0)
        self.stade_combo.setCurrentIndex(0)
        self.poids_min.setValue(0)
        self.poids_max.setValue(0)
        self.prod_min.setValue(0)
        self.prod_max.setValue(0)
        self.ufl_edit.setValue(0)
        self.ufv_edit.setValue(0)
        self.pdi_edit.setValue(0)
        self.ca_edit.setValue(0)
        self.p_edit.setValue(0)
        self.obs_edit.clear()
        self.btn_save.setText("Sauvegarder")

    def enregistrer(self):
        race = self.race_edit.text().strip()
        if not race:
            QMessageBox.warning(self, "Erreur", "La race est obligatoire.")
            return

        db = SessionLocal()
        try:
            if self.current_id is None:
                # Vérifier si un enregistrement similaire existe déjà
                existing = db.query(BesoinNutritionnel).filter(
                    BesoinNutritionnel.race == race,
                    BesoinNutritionnel.categorie == self.categorie_combo.currentText(),
                    BesoinNutritionnel.stade == self.stade_combo.currentText(),
                    BesoinNutritionnel.poids_min == self.poids_min.value(),
                    BesoinNutritionnel.poids_max == self.poids_max.value()
                ).first()
                if existing:
                    QMessageBox.warning(self, "Erreur", "Cet enregistrement existe déjà.")
                    return

                besoin = BesoinNutritionnel(
                    race=race,
                    categorie=self.categorie_combo.currentText(),
                    stade=self.stade_combo.currentText(),
                    poids_min=self.poids_min.value(),
                    poids_max=self.poids_max.value(),
                    production_min=self.prod_min.value() if self.prod_min.value() > 0 else None,
                    production_max=self.prod_max.value() if self.prod_max.value() > 0 else None,
                    ufl=self.ufl_edit.value(),
                    ufv=self.ufv_edit.value(),
                    pdi=self.pdi_edit.value(),
                    calcium=self.ca_edit.value(),
                    phosphore=self.p_edit.value(),
                    observations=self.obs_edit.text().strip() or None
                )
                db.add(besoin)
            else:
                besoin = db.query(BesoinNutritionnel).filter(BesoinNutritionnel.id == self.current_id).first()
                if besoin:
                    besoin.race = race
                    besoin.categorie = self.categorie_combo.currentText()
                    besoin.stade = self.stade_combo.currentText()
                    besoin.poids_min = self.poids_min.value()
                    besoin.poids_max = self.poids_max.value()
                    besoin.production_min = self.prod_min.value() if self.prod_min.value() > 0 else None
                    besoin.production_max = self.prod_max.value() if self.prod_max.value() > 0 else None
                    besoin.ufl = self.ufl_edit.value()
                    besoin.ufv = self.ufv_edit.value()
                    besoin.pdi = self.pdi_edit.value()
                    besoin.calcium = self.ca_edit.value()
                    besoin.phosphore = self.p_edit.value()
                    besoin.observations = self.obs_edit.text().strip() or None
                else:
                    QMessageBox.warning(self, "Erreur", "Enregistrement introuvable.")
                    return
            db.commit()
            QMessageBox.information(self, "Succès", "Besoin enregistré.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un enregistrement.")
            return
        reply = QMessageBox.question(self, "Confirmation",
                                     "Supprimer ce besoin ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                besoin = db.query(BesoinNutritionnel).filter(BesoinNutritionnel.id == self.current_id).first()
                if besoin:
                    db.delete(besoin)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Besoin supprimé.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Enregistrement introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()