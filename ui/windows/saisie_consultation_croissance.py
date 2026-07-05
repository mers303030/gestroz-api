# ui/windows/saisie_consultation_croissance.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Naissance, Croissance
from datetime import datetime, date, timedelta

class SaisieConsultationCroissanceWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des pesées (croissance)")
        self.resize(1300, 700)  # élargi pour accueillir les colonnes
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

        # Animal sevré (uniquement les sevrés de moins d'un an)
        self.animal_combo = QComboBox()
        self.animal_combo.setEditable(True)
        self.animal_combo.setPlaceholderText("Sélectionnez un animal sevré (veau/velle)")
        self.animal_combo.setEnabled(False)
        self.animal_combo.currentIndexChanged.connect(self.update_gmq_preview)
        form_layout.addRow(QLabel("Animal (numéro boucle) :"), self.animal_combo)

        # Date de pesée
        self.date_pesee = QDateEdit()
        self.date_pesee.setCalendarPopup(True)
        self.date_pesee.setDate(QDate.currentDate())
        self.date_pesee.setDisplayFormat("yyyy-MM-dd")
        self.date_pesee.dateChanged.connect(self.update_gmq_preview)
        form_layout.addRow(QLabel("Date de pesée :"), self.date_pesee)

        # Poids
        self.poids = QLineEdit()
        self.poids.setPlaceholderText("kg")
        self.poids.textChanged.connect(self.update_gmq_preview)
        form_layout.addRow(QLabel("Poids (kg) :"), self.poids)

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
        self.btn_delete.clicked.connect(self.supprimer_pesee)
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
        self.table.setColumnCount(9)  # N°, ID, Boucle, Date naiss., Poids naiss., GMQ N-S, Date pesée, Poids, GMQ post-sevrage
        self.table.setHorizontalHeaderLabels([
            "N°", "ID", "Boucle", "Date naiss.", "Poids naiss. (kg)",
            "GMQ N-S (g/j)", "Date pesée", "Poids (kg)", "GMQ (g/j)"
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
        """Remplit la combo avec les animaux sevrés de moins d'un an."""
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
                Naissance.sevre == True,
                Naissance.actif == True
            ).all()
        finally:
            db.close()

        eligibles = []
        for n in naissances:
            if not n.date_naissance:
                continue
            if isinstance(n.date_naissance, str):
                date_naiss = datetime.strptime(n.date_naissance, "%Y-%m-%d").date()
            else:
                date_naiss = n.date_naissance
            if (date.today() - date_naiss).days < 365:
                eligibles.append(n)

        # Compter le nombre de pesées pour chaque animal et l'afficher dans la combo
        for n in eligibles:
            db = SessionLocal()
            try:
                nb_pesees = db.query(Croissance).filter(
                    Croissance.code_elevage == code,
                    Croissance.numero_boucle == n.numero_boucle
                ).count()
            finally:
                db.close()
            text = f"{n.numero_boucle} (sevré le {n.date_sevrage}) - {nb_pesees} pesée(s)"
            self.animal_combo.addItem(text, n.id)

        self.animal_combo.setEnabled(len(eligibles) > 0)
        if len(eligibles) == 0:
            self.animal_combo.addItem("Aucun animal sevré de moins d'un an", None)

        self.load_table()
        self.gmq_label.setText("GMQ (g/j) : ---")
        self.date_pesee.setDate(QDate.currentDate())
        self.poids.clear()
        self.current_id = None

    def load_table(self):
        """Affiche les pesées avec numéro d'ordre, date naissance, poids naissance et GMQ N-S."""
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            # Récupérer les numéros de boucle des animaux éligibles (sevré, <365 jours)
            today = date.today()
            naissances = db.query(Naissance).filter(
                Naissance.code_elevage == code,
                Naissance.sevre == True,
                Naissance.actif == True
            ).all()
            boucles_eligibles = []
            infos_naissance = {}  # pour récupérer date_naissance, poids_naissance, gmq_naissance_sevrage
            for n in naissances:
                if not n.date_naissance:
                    continue
                if isinstance(n.date_naissance, str):
                    date_naiss = datetime.strptime(n.date_naissance, "%Y-%m-%d").date()
                else:
                    date_naiss = n.date_naissance
                if (today - date_naiss).days < 365:
                    boucles_eligibles.append(n.numero_boucle)
                    infos_naissance[n.numero_boucle] = {
                        'date_naissance': n.date_naissance,
                        'poids_naissance': n.poids_naissance,
                        'gmq_naissance_sevrage': n.gmq_naissance_sevrage
                    }

            if not boucles_eligibles:
                self.table.setRowCount(0)
                return

            # Récupérer toutes les pesées pour ces animaux, triées par boucle puis par date
            pesees = db.query(Croissance).filter(
                Croissance.code_elevage == code,
                Croissance.numero_boucle.in_(boucles_eligibles)
            ).order_by(
                Croissance.numero_boucle,
                Croissance.date_pesee.asc()
            ).all()
        finally:
            db.close()

        # Grouper par boucle et attribuer un numéro d'ordre
        self.table.setRowCount(len(pesees))
        current_boucle = None
        ordre = 0
        for i, p in enumerate(pesees):
            if p.numero_boucle != current_boucle:
                current_boucle = p.numero_boucle
                ordre = 1
            else:
                ordre += 1

            # Récupérer les infos de naissance
            info = infos_naissance.get(p.numero_boucle, {})
            date_naissance = info.get('date_naissance', '')
            poids_naissance = info.get('poids_naissance', '')
            gmq_ns = info.get('gmq_naissance_sevrage', '')

            self.table.setItem(i, 0, QTableWidgetItem(str(ordre)))
            self.table.setItem(i, 1, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 2, QTableWidgetItem(p.numero_boucle))
            self.table.setItem(i, 3, QTableWidgetItem(str(date_naissance) if date_naissance else ""))
            self.table.setItem(i, 4, QTableWidgetItem(str(poids_naissance) if poids_naissance else ""))
            self.table.setItem(i, 5, QTableWidgetItem(f"{gmq_ns:.1f}" if gmq_ns is not None else ""))
            self.table.setItem(i, 6, QTableWidgetItem(p.date_pesee))
            self.table.setItem(i, 7, QTableWidgetItem(str(p.poids) if p.poids else ""))
            gmq = p.gmq_post_sevrage
            self.table.setItem(i, 8, QTableWidgetItem(f"{gmq:.1f}" if gmq is not None else ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner une pesée.")
            return
        # Colonnes : 0=N°, 1=ID, 2=Boucle, 3=Date naiss., 4=Poids naiss., 5=GMQ N-S, 6=Date pesée, 7=Poids, 8=GMQ
        self.current_id = int(self.table.item(row, 1).text())
        boucle = self.table.item(row, 2).text()
        date_pesee = self.table.item(row, 6).text()
        poids = self.table.item(row, 7).text()

        # Charger l'animal correspondant dans la combo
        for i in range(self.animal_combo.count()):
            if self.animal_combo.itemText(i).startswith(boucle):
                self.animal_combo.setCurrentIndex(i)
                break
        self.date_pesee.setDate(QDate.fromString(date_pesee, "yyyy-MM-dd"))
        self.poids.setText(poids)
        self.update_gmq_preview()

    def annuler_edition(self):
        self.current_id = None
        self.animal_combo.setCurrentIndex(-1)
        self.date_pesee.setDate(QDate.currentDate())
        self.poids.clear()
        self.gmq_label.setText("GMQ (g/j) : ---")
        self.on_eleveur_changed()

    def update_gmq_preview(self):
        naissance_id = self.animal_combo.currentData()
        if not naissance_id:
            self.gmq_label.setText("GMQ (g/j) : ---")
            return
        poids_str = self.poids.text().strip()
        if not poids_str:
            self.gmq_label.setText("GMQ (g/j) : ---")
            return
        try:
            poids = float(poids_str)
        except:
            self.gmq_label.setText("GMQ : poids invalide")
            return
        date_pesee = self.date_pesee.date().toString("yyyy-MM-dd")

        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == naissance_id).first()
            if not naissance or not naissance.sevre:
                self.gmq_label.setText("GMQ : animal non sevré")
                return

            derniere = db.query(Croissance).filter(
                Croissance.code_elevage == naissance.code_elevage,
                Croissance.numero_boucle == naissance.numero_boucle,
                Croissance.date_pesee < date_pesee
            ).order_by(Croissance.date_pesee.desc()).first()

            if derniere:
                date_ref = derniere.date_pesee
                poids_ref = derniere.poids
            else:
                if not naissance.date_sevrage or not naissance.poids_sevrage:
                    self.gmq_label.setText("GMQ : données sevrage manquantes")
                    return
                date_ref = naissance.date_sevrage
                poids_ref = naissance.poids_sevrage

            date_ref_obj = datetime.strptime(date_ref, "%Y-%m-%d")
            date_pes_obj = datetime.strptime(date_pesee, "%Y-%m-%d")
            jours = (date_pes_obj - date_ref_obj).days
            if jours > 0:
                gmq = (poids - poids_ref) / jours * 1000
                self.gmq_label.setText(f"GMQ (g/j) : {gmq:.0f}")
            else:
                self.gmq_label.setText("GMQ : date antérieure à la référence")
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
            QMessageBox.warning(self, "Erreur", "Choisissez un animal sevré de moins d'un an.")
            return
        poids_str = self.poids.text().strip()
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
        date_pesee = self.date_pesee.date().toString("yyyy-MM-dd")

        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == naissance_id).first()
            if not naissance or not naissance.sevre:
                QMessageBox.warning(self, "Erreur", "Animal non sevré.")
                return

            date_naissance = naissance.date_naissance
            if isinstance(date_naissance, date):
                date_naissance_str = date_naissance.strftime("%Y-%m-%d")
            else:
                date_naissance_str = date_naissance

            if naissance.date_sevrage and date_pesee <= naissance.date_sevrage:
                QMessageBox.warning(self, "Erreur", "La date de pesée doit être postérieure au sevrage.")
                return

            if self.current_id is None:
                existing = db.query(Croissance).filter(
                    Croissance.code_elevage == code,
                    Croissance.numero_boucle == naissance.numero_boucle,
                    Croissance.date_pesee == date_pesee
                ).first()
                if existing:
                    QMessageBox.warning(self, "Erreur", "Une pesée existe déjà à cette date.")
                    return
            else:
                pesee = db.query(Croissance).filter(Croissance.id == self.current_id).first()
                if not pesee:
                    QMessageBox.warning(self, "Erreur", "Pesée introuvable.")
                    return
                if date_pesee != pesee.date_pesee:
                    existing = db.query(Croissance).filter(
                        Croissance.code_elevage == code,
                        Croissance.numero_boucle == naissance.numero_boucle,
                        Croissance.date_pesee == date_pesee,
                        Croissance.id != self.current_id
                    ).first()
                    if existing:
                        QMessageBox.warning(self, "Erreur", "Une autre pesée existe déjà à cette date.")
                        return

            derniere = db.query(Croissance).filter(
                Croissance.code_elevage == code,
                Croissance.numero_boucle == naissance.numero_boucle,
                Croissance.date_pesee < date_pesee
            ).order_by(Croissance.date_pesee.desc()).first()
            if derniere:
                poids_ref = derniere.poids
                date_ref = derniere.date_pesee
            else:
                if not naissance.poids_sevrage or not naissance.date_sevrage:
                    QMessageBox.warning(self, "Erreur", "Données de sevrage manquantes.")
                    return
                poids_ref = naissance.poids_sevrage
                date_ref = naissance.date_sevrage

            date_ref_obj = datetime.strptime(date_ref, "%Y-%m-%d")
            date_pes_obj = datetime.strptime(date_pesee, "%Y-%m-%d")
            jours = (date_pes_obj - date_ref_obj).days
            if jours > 0:
                gmq = (poids - poids_ref) / jours * 1000
            else:
                QMessageBox.warning(self, "Erreur", "La date de pesée doit être postérieure à la référence.")
                return

            if gmq > 2000:
                reply = QMessageBox.question(self, "GMQ élevé",
                                             f"GMQ = {gmq:.0f} g/j (>2000). Enregistrer ?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return

            if self.current_id is None:
                pesee = Croissance(
                    code_elevage=code,
                    numero_boucle=naissance.numero_boucle,
                    date_naissance=date_naissance_str,
                    date_pesee=date_pesee,
                    poids=poids,
                    gmq_post_sevrage=round(gmq, 1)
                )
                db.add(pesee)
            else:
                pesee = db.query(Croissance).filter(Croissance.id == self.current_id).first()
                if pesee:
                    pesee.date_pesee = date_pesee
                    pesee.poids = poids
                    pesee.gmq_post_sevrage = round(gmq, 1)

            db.commit()
            QMessageBox.information(self, "Succès", "Pesée enregistrée.")
            self.load_table()
            self.annuler_edition()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer_pesee(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une pesée.")
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette pesée ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                pesee = db.query(Croissance).filter(Croissance.id == self.current_id).first()
                if pesee:
                    db.delete(pesee)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Pesée supprimée.")
                    self.load_table()
                    self.annuler_edition()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erreur", str(e))
            finally:
                db.close()