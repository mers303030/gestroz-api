# ui/windows/saisie_consultation_eleveurs.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QLabel,
                               QTableWidget, QTableWidgetItem, QMessageBox,
                               QGroupBox, QHeaderView)
from PySide6.QtCore import Qt
from database.db_session import SessionLocal
from database.models import Eleveur
from sqlalchemy import func

class SaisieConsultationEleveursWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des éleveurs")
        self.resize(1100, 750)
        layout = QVBoxLayout(self)

        # --- Formulaire ---
        form_group = QWidget()
        form_layout = QFormLayout(form_group)

        self.commune_combo = QComboBox()
        self.commune_combo.addItems(["Oulmès", "Aït Ichou", "Boukchmir"])
        self.commune_combo.currentTextChanged.connect(self.on_commune_changed)
        form_layout.addRow(QLabel("Commune :"), self.commune_combo)

        self.code_edit = QLineEdit()
        self.code_edit.setReadOnly(True)
        form_layout.addRow(QLabel("Code élevage :"), self.code_edit)

        self.nom_edit = QLineEdit()
        self.nom_edit.textChanged.connect(self._on_nom_changed)
        form_layout.addRow(QLabel("Nom :"), self.nom_edit)

        self.prenom_edit = QLineEdit()
        self.prenom_edit.textChanged.connect(self._on_prenom_changed)
        form_layout.addRow(QLabel("Prénom :"), self.prenom_edit)

        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow(QLabel("Date de naissance :"), self.date_edit)

        self.niveau_combo = QComboBox()
        self.niveau_combo.addItems(["Aucun", "Primaire", "Collège", "Lycée", "Supérieur"])
        form_layout.addRow(QLabel("Niveau scolaire :"), self.niveau_combo)

        self.cnie_edit = QLineEdit()
        form_layout.addRow(QLabel("CNIE :"), self.cnie_edit)

        self.tel_edit = QLineEdit()
        form_layout.addRow(QLabel("Téléphone :"), self.tel_edit)

        layout.addWidget(form_group)

        # --- Boutons ---
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.nouveau)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.sauvegarder)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.annuler)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        # --- Tableau ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Code", "Nom", "Prénom", "CNIE", "Téléphone", "Date naiss.", "Niveau"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.charger_depuis_table)
        layout.addWidget(self.table)

        # --- Statistiques ---
        self.stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(self.stats_group)
        self.lbl_total = QLabel()
        self.lbl_par_commune = QLabel()
        stats_layout.addWidget(self.lbl_total)
        stats_layout.addWidget(self.lbl_par_commune)
        layout.addWidget(self.stats_group)

        # --- Variables ---
        self.current_id = None

        # Chargement initial
        self.load_table()

    # === MÉTHODES DE FORMATAGE ===
    def _format_nom(self, texte):
        return texte.strip().upper()

    def _format_prenom(self, texte):
        if not texte:
            return ""
        texte = texte.strip().lower()
        if len(texte) == 1:
            return texte.upper()
        return texte[0].upper() + texte[1:]

    def _on_nom_changed(self):
        self.nom_edit.blockSignals(True)
        self.nom_edit.setText(self._format_nom(self.nom_edit.text()))
        self.nom_edit.blockSignals(False)

    def _on_prenom_changed(self):
        self.prenom_edit.blockSignals(True)
        self.prenom_edit.setText(self._format_prenom(self.prenom_edit.text()))
        self.prenom_edit.blockSignals(False)

    # === GÉNÉRATION DU CODE ===
    def generer_code(self):
        commune = self.commune_combo.currentText()
        mapping = {"Oulmès": "OLM", "Aït Ichou": "AIT", "Boukchmir": "BOK"}
        prefix = mapping.get(commune, "UNK")
        db = SessionLocal()
        count = db.query(Eleveur).filter(Eleveur.commune == commune).count()
        db.close()
        new_num = count + 1
        self.code_edit.setText(f"{prefix}{new_num:03d}")

    # === CHANGEMENT DE COMMUNE ===
    def on_commune_changed(self):
        self.generer_code()
        self.load_table()

    # === CHARGEMENT DE LA TABLE ===
    def load_table(self):
        commune = self.commune_combo.currentText()
        db = SessionLocal()
        try:
            query = db.query(Eleveur).filter(Eleveur.commune == commune)
            eleveurs = query.order_by(Eleveur.code_elevage.asc()).all()
            self.table.setRowCount(len(eleveurs))
            for i, e in enumerate(eleveurs):
                self.table.setItem(i, 0, QTableWidgetItem(e.code_elevage))
                self.table.setItem(i, 1, QTableWidgetItem(e.nom or ""))
                self.table.setItem(i, 2, QTableWidgetItem(e.prenom or ""))
                self.table.setItem(i, 3, QTableWidgetItem(e.cnie or ""))
                self.table.setItem(i, 4, QTableWidgetItem(e.telephone or ""))
                self.table.setItem(i, 5, QTableWidgetItem(e.date_naissance or ""))
                self.table.setItem(i, 6, QTableWidgetItem(e.niveau_scolaire or ""))
            self.table.resizeColumnsToContents()
            self._refresh_stats()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement : {e}")
        finally:
            db.close()

    def _refresh_stats(self):
        db = SessionLocal()
        total = db.query(Eleveur).count()
        communes = db.query(Eleveur.commune, func.count(Eleveur.code_elevage)).group_by(Eleveur.commune).all()
        stats = "\n".join([f"{c or 'Non renseignée'} : {nb}" for c, nb in communes if c])
        db.close()
        self.lbl_total.setText(f"Total général : {total}")
        self.lbl_par_commune.setText(f"Répartition :\n{stats}" if stats else "Aucune commune")

    # === CHARGEMENT D'UN ÉLEVEUR DANS LE FORMULAIRE ===
    def charger_eleveur(self, eleveur):
        self.current_id = eleveur.code_elevage
        self.commune_combo.setCurrentText(eleveur.commune or "Oulmès")
        self.code_edit.setText(eleveur.code_elevage)
        self.nom_edit.setText(self._format_nom(eleveur.nom or ""))
        self.prenom_edit.setText(self._format_prenom(eleveur.prenom or ""))
        self.date_edit.setText(eleveur.date_naissance or "")
        idx = self.niveau_combo.findText(eleveur.niveau_scolaire or "Aucun")
        if idx >= 0:
            self.niveau_combo.setCurrentIndex(idx)
        self.cnie_edit.setText(eleveur.cnie or "")
        self.tel_edit.setText(eleveur.telephone or "")

    def on_selection_changed(self):
        row = self.table.currentRow()
        if row < 0:
            return
        code = self.table.item(row, 0).text()
        db = SessionLocal()
        eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
        db.close()
        if eleveur:
            self.charger_eleveur(eleveur)

    def charger_depuis_table(self):
        self.on_selection_changed()

    # === BOUTONS ===
    def nouveau(self):
        self.current_id = None
        self.generer_code()
        self.nom_edit.clear()
        self.prenom_edit.clear()
        self.date_edit.clear()
        self.niveau_combo.setCurrentIndex(0)
        self.cnie_edit.clear()
        self.tel_edit.clear()
        self.load_table()

    def annuler(self):
        self.nouveau()

    # === SAUVEGARDE OPTIMISÉE (vérification unique) ===
    def sauvegarder(self):
        code = self.code_edit.text().strip()
        nom = self._format_nom(self.nom_edit.text().strip())
        prenom = self._format_prenom(self.prenom_edit.text().strip())
        if not code or not nom or not prenom:
            QMessageBox.warning(self, "Erreur", "Code, nom et prénom sont obligatoires.")
            return

        cnie = self.cnie_edit.text().strip() or None
        tel = self.tel_edit.text().strip() or None

        db = SessionLocal()
        try:
            # 🔥 Vérification unique (code, CNIE, téléphone)
            if self.current_id is None:
                existing = db.query(Eleveur).filter(
                    (Eleveur.code_elevage == code) |
                    (Eleveur.cnie == cnie) |
                    (Eleveur.telephone == tel)
                ).first()
                if existing:
                    if existing.code_elevage == code:
                        QMessageBox.warning(self, "Erreur", f"Le code {code} existe déjà.")
                    elif existing.cnie == cnie:
                        QMessageBox.warning(self, "Erreur", "CNIE déjà utilisé.")
                    elif existing.telephone == tel:
                        QMessageBox.warning(self, "Erreur", "Téléphone déjà utilisé.")
                    return
                # Création
                eleveur = Eleveur(
                    code_elevage=code,
                    nom=nom,
                    prenom=prenom,
                    commune=self.commune_combo.currentText(),
                    date_naissance=self.date_edit.text().strip() or None,
                    niveau_scolaire=self.niveau_combo.currentText(),
                    cnie=cnie,
                    telephone=tel
                )
                db.add(eleveur)
            else:
                # Modification : on exclut l'éleveur courant
                existing = db.query(Eleveur).filter(
                    (Eleveur.code_elevage == code) |
                    (Eleveur.cnie == cnie) |
                    (Eleveur.telephone == tel),
                    Eleveur.code_elevage != self.current_id
                ).first()
                if existing:
                    if existing.code_elevage == code:
                        QMessageBox.warning(self, "Erreur", f"Le code {code} existe déjà (un autre éleveur).")
                    elif existing.cnie == cnie:
                        QMessageBox.warning(self, "Erreur", "CNIE déjà utilisé par un autre éleveur.")
                    elif existing.telephone == tel:
                        QMessageBox.warning(self, "Erreur", "Téléphone déjà utilisé par un autre éleveur.")
                    return
                eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == self.current_id).first()
                if not eleveur:
                    QMessageBox.warning(self, "Erreur", "Éleveur introuvable.")
                    return
                eleveur.nom = nom
                eleveur.prenom = prenom
                eleveur.commune = self.commune_combo.currentText()
                eleveur.date_naissance = self.date_edit.text().strip() or None
                eleveur.niveau_scolaire = self.niveau_combo.currentText()
                eleveur.cnie = cnie
                eleveur.telephone = tel

            db.commit()
            QMessageBox.information(self, "Succès", "Éleveur enregistré.")
            self.load_table()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un éleveur.")
            return
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer {self.current_id} ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == self.current_id).first()
                if eleveur:
                    db.delete(eleveur)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Éleveur supprimé.")
                    self.load_table()
                    self.nouveau()
                else:
                    QMessageBox.warning(self, "Erreur", "Éleveur introuvable.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()