# ui/windows/saisie_consultation_naissances.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Animal, Naissance
from datetime import datetime, date, timedelta

class SaisieConsultationNaissancesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des naissances")
        self.resize(1200, 800)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE ====================
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        self.code_combo = QComboBox()
        self.code_combo.setEditable(True)
        self.code_combo.setPlaceholderText("Sélectionnez ou tapez un code élevage")
        self.code_combo.addItems(self.get_all_codes())
        self.code_combo.currentTextChanged.connect(self.on_eleveur_changed)
        form_layout.addRow(QLabel("Code élevage :"), self.code_combo)

        self.combo_mere = QComboBox()
        self.combo_mere.setEditable(True)
        self.combo_mere.setPlaceholderText("Choisissez ou tapez le numéro")
        form_layout.addRow(QLabel("Mère (numéro boucle) :"), self.combo_mere)

        self.numero_boucle = QLineEdit()
        self.numero_boucle.setPlaceholderText("Laissez vide pour auto-génération")
        form_layout.addRow(QLabel("Numéro boucle du veau :"), self.numero_boucle)

        self.date_naissance = QDateEdit()
        self.date_naissance.setCalendarPopup(True)
        self.date_naissance.setDate(QDate.currentDate())
        self.date_naissance.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date naissance :"), self.date_naissance)

        self.sexe = QComboBox()
        self.sexe.addItems(["M", "F"])
        form_layout.addRow(QLabel("Sexe :"), self.sexe)

        self.race = QComboBox()
        self.race.addItems(["ROZ", "CRO", "AME"])
        form_layout.addRow(QLabel("Race :"), self.race)

        self.poids_naissance = QLineEdit()
        self.poids_naissance.setPlaceholderText("12-30 kg")
        form_layout.addRow(QLabel("Poids naissance (kg) :"), self.poids_naissance)

        self.pere_combo = QComboBox()
        self.pere_combo.setEditable(True)
        self.pere_combo.setPlaceholderText("Sélectionnez ou tapez un numéro")
        form_layout.addRow(QLabel("Père (numéro boucle) :"), self.pere_combo)

        self.type_velage = QComboBox()
        self.type_velage.addItems(["Césarienne", "Assisté", "Normal"])
        self.type_velage.setCurrentIndex(-1)
        form_layout.addRow(QLabel("Type de vêlage :"), self.type_velage)

        self.observations = QLineEdit()
        self.observations.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Observations :"), self.observations)

        self.categorie = QLineEdit()
        self.categorie.setReadOnly(True)
        self.categorie.setPlaceholderText("Calculée automatiquement")
        form_layout.addRow(QLabel("Catégorie :"), self.categorie)

        # --- Boutons (Nouveau, Sauvegarder, Annuler, Supprimer, Fermer) ---
        form_btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.nouveau)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.annuler_edition)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer_naissance)
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

        # ==================== SÉPARATEUR ====================
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # ==================== BOUTON RAFRAÎCHIR ====================
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        self.btn_refresh = QPushButton("Rafraîchir la liste")
        self.btn_refresh.clicked.connect(self.load_table)
        refresh_layout.addWidget(self.btn_refresh)
        layout.addLayout(refresh_layout)

        # ==================== TABLEAU ====================
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Code élevage", "Boucle veau", "Mère", "Naissance",
            "Sexe", "Race", "Poids (kg)", "Type vêlage", "Observations"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.charger_selection)
        layout.addWidget(self.table)

        self.current_id = None
        self.load_table()
        self.sexe.currentTextChanged.connect(self.update_categorie)
        self.date_naissance.dateChanged.connect(self.update_categorie)
        self.update_categorie()

    # ==================== MÉTHODES ====================
    def get_all_codes(self):
        db = SessionLocal()
        try:
            return [e.code_elevage for e in db.query(Eleveur).all()]
        finally:
            db.close()

    def on_eleveur_changed(self):
        """Remplit les listes des mères/pères pour le formulaire et recharge le tableau."""
        code = self.code_combo.currentText().strip()
        self.combo_mere.clear()
        self.pere_combo.clear()
        self.load_table()
        if not code:
            self.combo_mere.setEnabled(False)
            return

        db = SessionLocal()
        try:
            eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
            if not eleveur:
                self.combo_mere.setEnabled(False)
                return

            today = date.today()
            limite = today - timedelta(days=330)
            toutes_meres = db.query(Animal).filter(
                Animal.code_elevage == code,
                Animal.categorie.in_(['Vache', 'Génisse']),
                Animal.actif == True
            ).all()

            meres_filtrees = []
            for mere in toutes_meres:
                dernier_velage = db.query(Naissance).filter(
                    Naissance.code_elevage == code,
                    Naissance.mere_boucle == mere.numero_boucle
                ).order_by(Naissance.date_naissance.desc()).first()
                if dernier_velage:
                    derniere_date = dernier_velage.date_naissance
                    if isinstance(derniere_date, str):
                        derniere_date = datetime.strptime(derniere_date, "%Y-%m-%d").date()
                    if derniere_date > limite:
                        continue
                meres_filtrees.append(mere)

            for mere in meres_filtrees:
                self.combo_mere.addItem(f"{mere.numero_boucle} - {mere.categorie}", mere.numero_boucle)
            self.combo_mere.setEnabled(len(meres_filtrees) > 0)

            # Pères dans l'élevage
            peres = db.query(Animal).filter(
                Animal.code_elevage == code,
                Animal.categorie.in_(['Géniteur', 'Taurillon']),
                Animal.actif == True
            ).all()

            # Pères dans la même commune (géniteurs)
            peres_commune = db.query(Animal).join(Eleveur, Animal.code_elevage == Eleveur.code_elevage).filter(
                Eleveur.commune == eleveur.commune,
                Animal.categorie == 'Géniteur',
                Animal.actif == True
            ).all()

            all_codes = {p.numero_boucle for p in peres}
            for p in peres_commune:
                if p.numero_boucle not in all_codes:
                    peres.append(p)
                    all_codes.add(p.numero_boucle)

            for p in peres:
                self.pere_combo.addItem(f"{p.numero_boucle} - {p.categorie}", p.numero_boucle)
        finally:
            db.close()

    def update_categorie(self):
        """Calcule et affiche la catégorie en fonction du sexe et de la date de naissance."""
        sexe = self.sexe.currentText()
        qdate = self.date_naissance.date()
        naissance = qdate.toPython()
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
        self.categorie.setText(categorie)

    def load_table(self):
        """Charge le tableau avec les naissances de moins d'un an pour le code élevage sélectionné."""
        code_elevage = self.code_combo.currentText().strip()
        db = SessionLocal()
        try:
            query = db.query(Naissance)
            if code_elevage:
                query = query.filter(Naissance.code_elevage == code_elevage)

            naissances = query.order_by(Naissance.date_naissance.desc()).all()
            aujourd_hui = date.today()
            naissances_filtrees = []
            for n in naissances:
                if n.date_naissance:
                    if isinstance(n.date_naissance, str):
                        try:
                            date_naiss = datetime.strptime(n.date_naissance, "%Y-%m-%d").date()
                        except:
                            continue
                    else:
                        date_naiss = n.date_naissance
                    if (aujourd_hui - date_naiss).days < 365:
                        naissances_filtrees.append(n)
                else:
                    naissances_filtrees.append(n)

            self.table.setRowCount(len(naissances_filtrees))
            for i, n in enumerate(naissances_filtrees):
                self.table.setItem(i, 0, QTableWidgetItem(str(n.id)))
                self.table.setItem(i, 1, QTableWidgetItem(n.code_elevage))
                self.table.setItem(i, 2, QTableWidgetItem(n.numero_boucle or ""))
                self.table.setItem(i, 3, QTableWidgetItem(n.mere_boucle or ""))
                self.table.setItem(i, 4, QTableWidgetItem(str(n.date_naissance) if n.date_naissance else ""))
                self.table.setItem(i, 5, QTableWidgetItem(n.sexe or ""))
                self.table.setItem(i, 6, QTableWidgetItem(n.race or ""))
                self.table.setItem(i, 7, QTableWidgetItem(str(n.poids_naissance) if n.poids_naissance else ""))
                self.table.setItem(i, 8, QTableWidgetItem(n.type_velage or ""))
                self.table.setItem(i, 9, QTableWidgetItem(n.observations or ""))
            self.table.resizeColumnsToContents()
        finally:
            db.close()

    def nouveau(self):
        """Prépare le formulaire pour une nouvelle saisie (conserve le code élevage)."""
        self.current_id = None
        self.combo_mere.clear()
        self.pere_combo.clear()
        self.numero_boucle.clear()
        self.date_naissance.setDate(QDate.currentDate())
        self.sexe.setCurrentIndex(0)
        self.race.setCurrentIndex(0)
        self.poids_naissance.clear()
        self.type_velage.setCurrentIndex(-1)
        self.observations.clear()
        self.update_categorie()
        self.on_eleveur_changed()

    def charger_selection(self):
        """Charge la naissance sélectionnée dans le formulaire (double-clic)."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner une naissance.")
            return

        self.current_id = int(self.table.item(row, 0).text())
        code = self.table.item(row, 1).text()
        boucle_veau = self.table.item(row, 2).text()
        mere = self.table.item(row, 3).text()
        date_naiss = self.table.item(row, 4).text()
        sexe = self.table.item(row, 5).text()
        race = self.table.item(row, 6).text()
        poids = self.table.item(row, 7).text()
        type_vel = self.table.item(row, 8).text()
        obs = self.table.item(row, 9).text()

        # Bloquer les signaux pendant le remplissage
        self.sexe.blockSignals(True)
        self.date_naissance.blockSignals(True)

        self.code_combo.setCurrentText(code)
        self.on_eleveur_changed()
        QApplication.processEvents()

        idx = self.combo_mere.findData(mere)
        if idx >= 0:
            self.combo_mere.setCurrentIndex(idx)
        else:
            self.combo_mere.setEditText(mere)

        self.numero_boucle.setText(boucle_veau)
        self.date_naissance.setDate(QDate.fromString(date_naiss, "yyyy-MM-dd"))
        self.sexe.setCurrentText(sexe)
        self.race.setCurrentText(race)
        self.poids_naissance.setText(poids)
        self.type_velage.setCurrentText(type_vel if type_vel else "")
        self.observations.setText(obs)

        # Père
        db = SessionLocal()
        try:
            n = db.query(Naissance).filter(Naissance.id == self.current_id).first()
            if n and n.pere_boucle:
                pere_boucle = n.pere_boucle
                idx_pere = self.pere_combo.findData(pere_boucle)
                if idx_pere >= 0:
                    self.pere_combo.setCurrentIndex(idx_pere)
                else:
                    self.pere_combo.setEditText(pere_boucle)
        finally:
            db.close()

        # Réactiver les signaux et mettre à jour la catégorie
        self.sexe.blockSignals(False)
        self.date_naissance.blockSignals(False)
        self.update_categorie()

    def annuler_edition(self):
        self.current_id = None
        self.code_combo.setCurrentIndex(-1)
        self.code_combo.setEditText("")
        self.combo_mere.clear()
        self.pere_combo.clear()
        self.numero_boucle.clear()
        self.date_naissance.setDate(QDate.currentDate())
        self.sexe.setCurrentIndex(0)
        self.race.setCurrentIndex(0)
        self.poids_naissance.clear()
        self.type_velage.setCurrentIndex(-1)
        self.observations.clear()
        self.update_categorie()
        self.load_table()

    # ==================== VÉRIFICATION DE LA MÈRE ====================
    def verifier_mere(self, db, code_elevage, mere_boucle):
        """Vérifie que la mère existe, est Vache/Génisse, et que son dernier vêlage date de +330 jours."""
        if not mere_boucle:
            return True, ""
        mere = db.query(Animal).filter(
            Animal.code_elevage == code_elevage,
            Animal.numero_boucle == mere_boucle
        ).first()
        if not mere:
            return False, f"L'animal '{mere_boucle}' n'existe pas dans cet élevage."
        if mere.categorie not in ['Vache', 'Génisse']:
            return False, f"L'animal '{mere_boucle}' n'est pas une vache ou génisse (catégorie : {mere.categorie})."

        dernier = db.query(Naissance).filter(
            Naissance.code_elevage == code_elevage,
            Naissance.mere_boucle == mere_boucle
        ).order_by(Naissance.date_naissance.desc()).first()
        if dernier:
            derniere_date = dernier.date_naissance
            if isinstance(derniere_date, str):
                derniere_date = datetime.strptime(derniere_date, "%Y-%m-%d").date()
            # 🔥 En modification, on exclut l'ID courant pour ne pas bloquer la correction
            if self.current_id and dernier.id == self.current_id:
                # C'est la naissance qu'on est en train de modifier, on ne vérifie pas
                pass
            elif (date.today() - derniere_date).days < 330:
                return False, f"La mère a déjà vêlé le {derniere_date} (moins de 330 jours)."
        return True, ""

    # ==================== ENREGISTREMENT ====================
    def enregistrer(self):
        code_elevage = self.code_combo.currentText().strip()
        if not code_elevage:
            QMessageBox.warning(self, "Erreur", "Le code élevage est obligatoire.")
            return

        mere_boucle = self.combo_mere.currentData()
        if not mere_boucle:
            mere_text = self.combo_mere.currentText().strip()
            mere_boucle = mere_text if mere_text else None

        # 🔥 Vérification de la mère UNIQUEMENT en nouvelle saisie
        if self.current_id is None:
            if not mere_boucle:
                QMessageBox.warning(self, "Erreur", "La mère est obligatoire pour une nouvelle naissance.")
                return
            if mere_boucle:
                db = SessionLocal()
                try:
                    ok, msg = self.verifier_mere(db, code_elevage, mere_boucle)
                    if not ok:
                        QMessageBox.warning(self, "Mère invalide", msg)
                        return
                finally:
                    db.close()
        # En modification, on ignore la vérification de la mère
        # On ne bloque pas même si la mère a déjà vêlé car on peut modifier d'autres champs

        pere_boucle = self.pere_combo.currentData()
        if not pere_boucle:
            pere_text = self.pere_combo.currentText().strip()
            pere_boucle = pere_text if pere_text else None

        date_naiss = self.date_naissance.date().toString("yyyy-MM-dd")
        sexe = self.sexe.currentText()
        race = self.race.currentText()
        poids_str = self.poids_naissance.text().strip()
        poids_naissance = None

        if poids_str:
            try:
                poids_naissance = float(poids_str)
                if poids_naissance < 12 or poids_naissance > 30:
                    reply = QMessageBox.question(
                        self,
                        "Poids inhabituel",
                        f"Le poids saisi ({poids_naissance} kg) est en dehors de la plage habituelle (12-30 kg).\n"
                        "Voulez-vous continuer ?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply != QMessageBox.Yes:
                        return
            except ValueError:
                QMessageBox.warning(self, "Erreur", "Le poids doit être un nombre.")
                return
        else:
            poids_naissance = None

        type_velage = self.type_velage.currentText() if self.type_velage.currentIndex() >= 0 else None
        observations = self.observations.text().strip() or None
        numero_boucle_veau = self.numero_boucle.text().strip() or None

        db = SessionLocal()
        try:
            if numero_boucle_veau:
                existing = db.query(Naissance).filter(
                    Naissance.code_elevage == code_elevage,
                    Naissance.numero_boucle == numero_boucle_veau
                )
                if self.current_id is not None:
                    existing = existing.filter(Naissance.id != self.current_id)
                if existing.first():
                    reply = QMessageBox.question(
                        self,
                        "Doublon détecté",
                        f"Le numéro de boucle '{numero_boucle_veau}' est déjà utilisé.\n"
                        "Voulez-vous ajouter un suffixe 'A' ?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        numero_boucle_veau = numero_boucle_veau + "A"
                    else:
                        return

            if self.current_id is None:
                naissance = Naissance(
                    code_elevage=code_elevage,
                    mere_boucle=mere_boucle,
                    pere_boucle=pere_boucle,
                    numero_boucle=numero_boucle_veau,
                    date_naissance=date_naiss,
                    sexe=sexe,
                    race=race,
                    poids_naissance=poids_naissance,
                    type_velage=type_velage,
                    observations=observations
                )
                db.add(naissance)
                db.commit()
                QMessageBox.information(self, "Succès", "Naissance enregistrée.")
            else:
                naissance = db.query(Naissance).filter(Naissance.id == self.current_id).first()
                if naissance:
                    # On met à jour tous les champs sauf la mère ? Non, on laisse l'utilisateur modifier la mère si il veut
                    # mais sans vérification
                    naissance.code_elevage = code_elevage
                    naissance.mere_boucle = mere_boucle if mere_boucle else naissance.mere_boucle
                    naissance.pere_boucle = pere_boucle
                    naissance.numero_boucle = numero_boucle_veau
                    naissance.date_naissance = date_naiss
                    naissance.sexe = sexe
                    naissance.race = race
                    naissance.poids_naissance = poids_naissance
                    naissance.type_velage = type_velage
                    naissance.observations = observations
                    db.commit()
                    QMessageBox.information(self, "Succès", "Naissance modifiée.")
                else:
                    QMessageBox.warning(self, "Erreur", "Naissance introuvable.")
            self.nouveau()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer : {str(e)}")
        finally:
            db.close()

    def supprimer_naissance(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Suppression", "Aucune naissance sélectionnée.")
            return
        reply = QMessageBox.question(self, "Confirmation",
                                     "Voulez-vous vraiment supprimer cette naissance ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        db = SessionLocal()
        try:
            naissance = db.query(Naissance).filter(Naissance.id == self.current_id).first()
            if naissance:
                db.delete(naissance)
                db.commit()
                QMessageBox.information(self, "Succès", "Naissance supprimée.")
                self.annuler_edition()
            else:
                QMessageBox.warning(self, "Erreur", "Naissance introuvable.")
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {str(e)}")
        finally:
            db.close()