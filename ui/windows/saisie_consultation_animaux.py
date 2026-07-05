# ui/windows/saisie_consultation_animaux.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Animal, Eleveur
from datetime import date

class SaisieConsultationAnimauxWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des animaux")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        # === Formulaire ===
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.setPlaceholderText("Sélectionnez ou tapez un code élevage")
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_code_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.eleveur_info_label = QLabel()
        self.eleveur_info_label.setStyleSheet("color: #d4af37; font-style: italic;")
        form_layout.addRow(QLabel("Éleveur :"), self.eleveur_info_label)

        self.numero_edit = QLineEdit()
        form_layout.addRow(QLabel("Numéro de boucle :"), self.numero_edit)

        self.sexe_combo = QComboBox()
        self.sexe_combo.addItems(["M", "F"])
        self.sexe_combo.currentTextChanged.connect(self.mettre_a_jour_categorie)
        form_layout.addRow(QLabel("Sexe :"), self.sexe_combo)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.mettre_a_jour_categorie)
        form_layout.addRow(QLabel("Date de naissance :"), self.date_edit)

        self.categorie_edit = QLineEdit()
        self.categorie_edit.setReadOnly(True)
        form_layout.addRow(QLabel("Catégorie :"), self.categorie_edit)

        self.poids_edit = QLineEdit()
        self.poids_edit.setPlaceholderText("kg")
        form_layout.addRow(QLabel("Poids naissance (kg) :"), self.poids_edit)

        # === Boutons du formulaire ===
        form_btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.nouveau)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.annuler_edition)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer_animal)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)

        form_btn_layout.addWidget(self.btn_new)
        form_btn_layout.addWidget(self.btn_save)
        form_btn_layout.addWidget(self.btn_cancel)
        form_btn_layout.addWidget(self.btn_delete)
        form_btn_layout.addStretch()
        form_btn_layout.addWidget(self.btn_close)
        form_layout.addRow(form_btn_layout)

        layout.addWidget(form_group)

        # === Séparateur ===
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # === Tableau ===
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Numéro", "Catégorie", "Sexe", "Date naissance", "Poids naiss."])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.charger_selection)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        layout.addWidget(self.table)

        # === Variables de contrôle ===
        self.current_id = None
        self.data = []
        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder

        # 🔒 Verrou pour éviter les boucles récursives
        self._loading = False

        self.on_code_changed()  # charge le premier élevage

    # --- Méthodes de gestion des listes ---
    def get_all_codes(self):
        db = SessionLocal()
        codes = [e.code_elevage for e in db.query(Eleveur).all()]
        db.close()
        return codes

    def on_code_changed(self):
        """Appelé quand le code élevage change. Chargement des animaux."""
        if self._loading:
            return
        self._loading = True
        try:
            code = self.code_combo.currentText().strip()
            if code:
                db = SessionLocal()
                eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
                if eleveur:
                    self.eleveur_info_label.setText(f"{eleveur.nom} {eleveur.prenom}")
                else:
                    self.eleveur_info_label.setText("Éleveur inconnu")
                db.close()
            else:
                self.eleveur_info_label.setText("")
            self.load_data()
        finally:
            self._loading = False

    def mettre_a_jour_categorie(self):
        sexe = self.sexe_combo.currentText()
        naissance = self.date_edit.date().toPython()
        today = date.today()
        if naissance > today:
            age_mois = 0
        else:
            age_mois = (today.year - naissance.year) * 12 + (today.month - naissance.month)
        age_ans = age_mois / 12.0

        if sexe == "F":
            if age_ans >= 2:
                categorie = "Vache"
            elif age_ans >= 1:
                categorie = "Génisse"
            else:
                categorie = "Velle"
        else:
            if age_ans >= 2:
                categorie = "Géniteur"
            elif age_ans >= 1:
                categorie = "Taurillon"
            else:
                categorie = "Veau"
        self.categorie_edit.setText(categorie)

    def load_data(self):
        code = self.code_combo.currentText().strip()
        if not code:
            self.data = []
            self.table.setRowCount(0)
            return
        db = SessionLocal()
        try:
            # 🔍 Ajout d'un ordre pour stabiliser
            animaux = db.query(Animal).filter(Animal.code_elevage == code).order_by(Animal.numero_boucle).all()
            self.data = []
            for a in animaux:
                self.data.append({
                    'numero': a.numero_boucle,
                    'categorie': a.categorie or '',
                    'sexe': a.sexe or '',
                    'date_naissance': a.date_naissance or '',
                    'poids': a.poids_naissance
                })
        finally:
            db.close()
        self.apply_sort()

    def apply_sort(self):
        reverse = (self.sort_order == Qt.DescendingOrder)
        if self.sort_column == 0:
            self.data.sort(key=lambda x: x['numero'], reverse=reverse)
        elif self.sort_column == 1:
            self.data.sort(key=lambda x: x['categorie'], reverse=reverse)
        elif self.sort_column == 2:
            self.data.sort(key=lambda x: x['sexe'], reverse=reverse)
        elif self.sort_column == 3:
            self.data.sort(key=lambda x: x['date_naissance'], reverse=reverse)
        elif self.sort_column == 4:
            self.data.sort(key=lambda x: x['poids'] if x['poids'] is not None else -1, reverse=reverse)

        self.table.setRowCount(len(self.data))
        for i, row in enumerate(self.data):
            self.table.setItem(i, 0, QTableWidgetItem(row['numero']))
            self.table.setItem(i, 1, QTableWidgetItem(row['categorie']))
            self.table.setItem(i, 2, QTableWidgetItem(row['sexe']))
            self.table.setItem(i, 3, QTableWidgetItem(row['date_naissance']))
            poids_str = str(row['poids']) if row['poids'] is not None else ""
            self.table.setItem(i, 4, QTableWidgetItem(poids_str))
        self.table.resizeColumnsToContents()

    def on_header_clicked(self, logicalIndex):
        if self.sort_column == logicalIndex:
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.sort_column = logicalIndex
            self.sort_order = Qt.AscendingOrder
        self.apply_sort()

    # --- Nouvelle méthode "Nouveau" ---
    def nouveau(self):
        self.current_id = None
        self.numero_edit.clear()
        self.sexe_combo.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())
        self.poids_edit.clear()
        self.mettre_a_jour_categorie()

    # --- Chargement d'un animal pour modification (double-clic) ---
    def charger_selection(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un animal.")
            return
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord sélectionner un élevage.")
            return
        numero = self.table.item(row, 0).text()
        db = SessionLocal()
        animal = db.query(Animal).filter(Animal.code_elevage == code, Animal.numero_boucle == numero).first()
        db.close()
        if not animal:
            QMessageBox.warning(self, "Erreur", "Animal introuvable.")
            return
        self.current_id = animal.numero_boucle
        self.numero_edit.setText(animal.numero_boucle)
        self.sexe_combo.setCurrentText(animal.sexe)
        if animal.date_naissance:
            self.date_edit.setDate(QDate.fromString(animal.date_naissance, "yyyy-MM-dd"))
        self.poids_edit.setText(str(animal.poids_naissance) if animal.poids_naissance else "")
        self.mettre_a_jour_categorie()

    def annuler_edition(self):
        self.nouveau()
        self.load_data()

    def enregistrer(self):
        code = self.code_combo.currentText().strip()
        num = self.numero_edit.text().strip()
        sexe = self.sexe_combo.currentText()
        date_naiss = self.date_edit.date().toString("yyyy-MM-dd")
        categorie = self.categorie_edit.text()
        poids_str = self.poids_edit.text().strip()
        poids = float(poids_str) if poids_str else None

        if not code or not num:
            QMessageBox.warning(self, "Erreur", "Le code élevage et le numéro de boucle sont obligatoires.")
            return

        db = SessionLocal()
        eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
        if not eleveur:
            db.close()
            QMessageBox.warning(self, "Erreur", f"Le code élevage '{code}' n'existe pas.")
            return

        # Vérification des doublons
        if self.current_id:
            other = db.query(Animal).filter(Animal.code_elevage == code, Animal.numero_boucle == num, Animal.numero_boucle != self.current_id).first()
        else:
            other = db.query(Animal).filter(Animal.code_elevage == code, Animal.numero_boucle == num).first()

        if other:
            reply = QMessageBox.question(self, "Doublon détecté",
                                         f"Le numéro '{num}' existe déjà.\nVoulez-vous l'enregistrer avec un suffixe 'A' ?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                num = num + "A"
            else:
                db.close()
                return

        try:
            if self.current_id:
                animal = db.query(Animal).filter(Animal.code_elevage == code, Animal.numero_boucle == self.current_id).first()
                if animal:
                    animal.code_elevage = code
                    animal.numero_boucle = num
                    animal.sexe = sexe
                    animal.date_naissance = date_naiss
                    animal.categorie = categorie
                    animal.poids_naissance = poids
            else:
                animal = Animal(
                    code_elevage=code,
                    numero_boucle=num,
                    sexe=sexe,
                    date_naissance=date_naiss,
                    categorie=categorie,
                    poids_naissance=poids,
                    actif=True
                )
                db.add(animal)
            db.commit()
            QMessageBox.information(self, "Succès", "Animal enregistré.")
            self.load_data()
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer_animal(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un animal.")
            return
        code = self.code_combo.currentText().strip()
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer l'animal {self.current_id} ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            animal = db.query(Animal).filter(Animal.code_elevage == code, Animal.numero_boucle == self.current_id).first()
            if animal:
                try:
                    db.delete(animal)
                    db.commit()
                    QMessageBox.information(self, "Succès", "Animal supprimé.")
                    self.load_data()
                    self.nouveau()
                except Exception as e:
                    db.rollback()
                    QMessageBox.critical(self, "Erreur", str(e))
            db.close()