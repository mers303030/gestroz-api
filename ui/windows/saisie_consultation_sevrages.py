# ui/windows/saisie_consultation_sevrages.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Animal, Naissance
from datetime import datetime, date, timedelta

class SaisieConsultationSevragesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des sevrages")
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

        # Animal à sevrer (uniquement non sevrés, veaux/velles de moins d'un an)
        self.animal_combo = QComboBox()
        self.animal_combo.setEditable(True)
        self.animal_combo.setPlaceholderText("Sélectionnez un animal (veau/velle non sevré)")
        self.animal_combo.setEnabled(False)
        self.animal_combo.currentIndexChanged.connect(self.update_gmq_preview)
        form_layout.addRow(QLabel("Animal (numéro boucle) :"), self.animal_combo)

        # Date de sevrage
        self.date_sevrage = QDateEdit()
        self.date_sevrage.setCalendarPopup(True)
        self.date_sevrage.setDate(QDate.currentDate())
        self.date_sevrage.setDisplayFormat("yyyy-MM-dd")
        self.date_sevrage.dateChanged.connect(self.update_gmq_preview)
        form_layout.addRow(QLabel("Date de sevrage :"), self.date_sevrage)

        # Poids au sevrage
        self.poids_sevrage = QLineEdit()
        self.poids_sevrage.setPlaceholderText("kg")
        self.poids_sevrage.textChanged.connect(self.update_gmq_preview)
        form_layout.addRow(QLabel("Poids au sevrage (kg) :"), self.poids_sevrage)

        # GMQ
        self.gmq_label = QLabel("GMQ (g/j) : ---")
        form_layout.addRow(QLabel("GMQ calculé :"), self.gmq_label)

        # Boutons
        form_btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.annuler_edition)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer_sevrage)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)

        form_btn_layout.addWidget(self.btn_save)
        form_btn_layout.addWidget(self.btn_cancel)
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
        self.table.setColumnCount(8)  # <-- 8 colonnes
        self.table.setHorizontalHeaderLabels([
            "ID Naiss.", "Boucle", "Date naiss.", "Catégorie",
            "Poids naiss. (kg)", "Poids sevrage (kg)", "Sevré", "Date sevrage"
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
        """Remplit la combo avec les veaux/velles non sevrés de moins d'un an."""
        code = self.code_combo.currentText().strip()
        self.animal_combo.clear()
        if not code:
            self.animal_combo.setEnabled(False)
            self.load_table()
            return

        db = SessionLocal()
        try:
            today = date.today()
            naissances = db.query(Naissance).filter(
                Naissance.code_elevage == code,
                Naissance.actif == True
            ).all()
        finally:
            db.close()

        eligibles = []
        for n in naissances:
            if n.sevre:
                continue
            if not n.date_naissance or not n.sexe:
                continue
            if isinstance(n.date_naissance, str):
                date_naiss = datetime.strptime(n.date_naissance, "%Y-%m-%d").date()
            else:
                date_naiss = n.date_naissance
            age_jours = (today - date_naiss).days
            if age_jours >= 365:
                continue
            cat = "Velle" if n.sexe == "F" else "Veau"
            if cat in ("Veau", "Velle"):
                eligibles.append((n, cat))

        for n, cat in eligibles:
            self.animal_combo.addItem(f"{n.numero_boucle} ({cat})", n.id)

        self.animal_combo.setEnabled(len(eligibles) > 0)
        if len(eligibles) == 0:
            self.animal_combo.addItem("Aucun animal éligible", None)

        self.load_table()
        self.gmq_label.setText("GMQ (g/j) : ---")
        self.date_sevrage.setDate(QDate.currentDate())
        self.poids_sevrage.clear()
        self.current_id = None

    def load_table(self):
        """Affiche les animaux éligibles avec poids naissance et poids sevrage."""
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            naissances = db.query(Naissance).filter(
                Naissance.code_elevage == code,
                Naissance.actif == True
            ).order_by(Naissance.date_naissance.desc()).all()
        finally:
            db.close()

        today = date.today()
        lignes = []
        for n in naissances:
            if not n.date_naissance or not n.sexe:
                continue
            if isinstance(n.date_naissance, str):
                date_naiss = datetime.strptime(n.date_naissance, "%Y-%m-%d").date()
            else:
                date_naiss = n.date_naissance
            age_jours = (today - date_naiss).days
            if age_jours >= 365:
                continue
            cat = "Velle" if n.sexe == "F" else "Veau"
            if cat not in ("Veau", "Velle"):
                continue
            lignes.append(n)

        self.table.setRowCount(len(lignes))
        for i, n in enumerate(lignes):
            self.table.setItem(i, 0, QTableWidgetItem(str(n.id)))
            self.table.setItem(i, 1, QTableWidgetItem(n.numero_boucle or ""))
            self.table.setItem(i, 2, QTableWidgetItem(str(n.date_naissance) if n.date_naissance else ""))
            cat = "Velle" if n.sexe == "F" else "Veau"
            self.table.setItem(i, 3, QTableWidgetItem(cat))
            # Poids naissance
            poids_naiss = str(n.poids_naissance) if n.poids_naissance is not None else "-"
            self.table.setItem(i, 4, QTableWidgetItem(poids_naiss))
            # Poids sevrage (NOUVEAU)
            poids_sevrage = str(n.poids_sevrage) if n.poids_sevrage is not None else "-"
            self.table.setItem(i, 5, QTableWidgetItem(poids_sevrage))
            self.table.setItem(i, 6, QTableWidgetItem("Oui" if n.sevre else "Non"))
            self.table.setItem(i, 7, QTableWidgetItem(str(n.date_sevrage) if n.date_sevrage else ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        naissance_id = int(self.table.item(row, 0).text())
        code = self.code_combo.currentText().strip()
        if not code:
            return

        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == naissance_id).first()
            if not naissance:
                QMessageBox.warning(self, "Erreur", "Animal introuvable.")
                return
        finally:
            db.close()

        self.current_id = naissance_id
        found = False
        for i in range(self.animal_combo.count()):
            if self.animal_combo.itemData(i) == naissance_id:
                self.animal_combo.setCurrentIndex(i)
                found = True
                break
        if not found:
            self.animal_combo.setEditText(naissance.numero_boucle)

        if naissance.date_sevrage:
            self.date_sevrage.setDate(QDate.fromString(naissance.date_sevrage, "yyyy-MM-dd"))
        else:
            self.date_sevrage.setDate(QDate.currentDate())
        self.poids_sevrage.setText(str(naissance.poids_sevrage) if naissance.poids_sevrage else "")
        self.update_gmq_preview()

    def annuler_edition(self):
        self.current_id = None
        self.animal_combo.setCurrentIndex(-1)
        self.date_sevrage.setDate(QDate.currentDate())
        self.poids_sevrage.clear()
        self.gmq_label.setText("GMQ (g/j) : ---")
        self.on_eleveur_changed()

    def update_gmq_preview(self):
        naissance_id = self.animal_combo.currentData()
        if not naissance_id:
            self.gmq_label.setText("GMQ (g/j) : ---")
            return
        poids_str = self.poids_sevrage.text().strip()
        if not poids_str:
            self.gmq_label.setText("GMQ (g/j) : ---")
            return
        try:
            poids = float(poids_str)
        except:
            self.gmq_label.setText("GMQ : poids invalide")
            return
        date_sev = self.date_sevrage.date().toString("yyyy-MM-dd")

        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == naissance_id).first()
            if not naissance or not naissance.poids_naissance or not naissance.date_naissance:
                self.gmq_label.setText("GMQ : données naissance manquantes")
                return
            if isinstance(naissance.date_naissance, str):
                date_naiss = datetime.strptime(naissance.date_naissance, "%Y-%m-%d")
            else:
                date_naiss = naissance.date_naissance
            date_sev_obj = datetime.strptime(date_sev, "%Y-%m-%d")
            jours = (date_sev_obj - date_naiss).days
            if jours > 0:
                gmq = (poids - naissance.poids_naissance) / jours * 1000
                self.gmq_label.setText(f"GMQ (g/j) : {gmq:.0f}")
            else:
                self.gmq_label.setText("GMQ : date sevrage antérieure")
        except Exception:
            self.gmq_label.setText("GMQ : erreur calcul")
        finally:
            db.close()

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return
        naissance_id = self.animal_combo.currentData()
        if not naissance_id:
            texte = self.animal_combo.currentText().strip()
            if texte:
                db = SessionLocal()
                try:
                    naissance = db.query(Naissance).filter(
                        Naissance.code_elevage == code,
                        Naissance.numero_boucle == texte
                    ).first()
                    if naissance:
                        naissance_id = naissance.id
                    else:
                        QMessageBox.warning(self, "Erreur", "Animal non trouvé.")
                        return
                finally:
                    db.close()
            else:
                QMessageBox.warning(self, "Erreur", "Choisissez un animal.")
                return
        poids_str = self.poids_sevrage.text().strip()
        if not poids_str:
            QMessageBox.warning(self, "Erreur", "Poids obligatoire.")
            return
        try:
            poids = float(poids_str)
            if poids <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Erreur", "Poids invalide.")
            return
        date_sev = self.date_sevrage.date().toString("yyyy-MM-dd")

        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == naissance_id).first()
            if not naissance:
                QMessageBox.warning(self, "Erreur", "Naissance introuvable.")
                return
            if naissance.date_naissance:
                if isinstance(naissance.date_naissance, str):
                    date_naiss = datetime.strptime(naissance.date_naissance, "%Y-%m-%d")
                else:
                    date_naiss = naissance.date_naissance
                date_sev_obj = datetime.strptime(date_sev, "%Y-%m-%d")
                if date_sev_obj <= date_naiss:
                    QMessageBox.warning(self, "Erreur", "Date sevrage postérieure à la naissance.")
                    return
                jours = (date_sev_obj - date_naiss).days
                if jours > 0:
                    gmq = (poids - naissance.poids_naissance) / jours * 1000
                else:
                    gmq = 0
            else:
                QMessageBox.warning(self, "Erreur", "Date de naissance manquante.")
                return

            if gmq > 2000:
                reply = QMessageBox.question(self, "GMQ élevé",
                                             f"GMQ = {gmq:.0f} g/j (>2000). Enregistrer ?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            elif gmq < 0:
                reply = QMessageBox.question(self, "GMQ négatif",
                                             f"GMQ = {gmq:.0f} g/j. Enregistrer ?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return

            naissance.sevre = True
            naissance.date_sevrage = date_sev
            naissance.poids_sevrage = poids
            naissance.gmq_naissance_sevrage = round(gmq, 1) if jours > 0 else 0
            db.commit()
            QMessageBox.information(self, "Succès", "Sevrage enregistré.")
            self.load_table()
            self.annuler_edition()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer_sevrage(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un animal sevré.")
            return
        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == self.current_id).first()
            if not naissance or not naissance.sevre:
                QMessageBox.warning(self, "Erreur", "Cet animal n'est pas sevré.")
                return
            reply = QMessageBox.question(self, "Confirmation",
                                         f"Supprimer le sevrage de {naissance.numero_boucle} ?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                naissance.sevre = False
                naissance.date_sevrage = None
                naissance.poids_sevrage = None
                naissance.gmq_naissance_sevrage = None
                db.commit()
                QMessageBox.information(self, "Succès", "Sevrage supprimé.")
                self.load_table()
                self.annuler_edition()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()