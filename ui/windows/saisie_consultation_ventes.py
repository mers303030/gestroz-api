# ui/windows/saisie_consultation_ventes.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Naissance, Vente
from datetime import datetime

class SaisieConsultationVentesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des ventes")
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

        # Animal (uniquement actifs)
        self.animal_combo = QComboBox()
        self.animal_combo.setEditable(True)
        self.animal_combo.setPlaceholderText("Choisissez ou tapez un numéro")
        self.animal_combo.setEnabled(False)
        form_layout.addRow(QLabel("Animal (numéro boucle) :"), self.animal_combo)

        # Date de vente
        self.date_vente = QDateEdit()
        self.date_vente.setCalendarPopup(True)
        self.date_vente.setDate(QDate.currentDate())
        self.date_vente.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Date de vente :"), self.date_vente)

        # Prix
        self.prix_vente = QLineEdit()
        self.prix_vente.setPlaceholderText("DH")
        form_layout.addRow(QLabel("Prix (DH) :"), self.prix_vente)

        # Lieu
        self.lieu_vente = QLineEdit()
        self.lieu_vente.setPlaceholderText("Lieu de vente")
        form_layout.addRow(QLabel("Lieu :"), self.lieu_vente)

        # Poids à la vente
        self.poids_vente = QLineEdit()
        self.poids_vente.setPlaceholderText("Optionnel (kg)")
        form_layout.addRow(QLabel("Poids à la vente (kg) :"), self.poids_vente)

        # Remarque
        self.remarque = QLineEdit()
        self.remarque.setPlaceholderText("Optionnel")
        form_layout.addRow(QLabel("Remarque :"), self.remarque)

        # Boutons
        form_btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.annuler)
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self.enregistrer)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.supprimer)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.annuler)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        form_btn_layout.addWidget(self.btn_new)
        form_btn_layout.addWidget(self.btn_save)
        form_btn_layout.addWidget(self.btn_delete)
        form_btn_layout.addWidget(self.btn_cancel)
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
            "ID", "Boucle", "Date vente", "Prix (DH)", "Lieu", "Poids (kg)", "Remarque"
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
        """Remplit la combo des animaux actifs pour l'élevage sélectionné."""
        code = self.code_combo.currentText().strip()
        self.animal_combo.clear()
        if not code:
            self.animal_combo.setEnabled(False)
            self.load_table()
            return

        db = SessionLocal()
        try:
            animaux = db.query(Naissance).filter(
                Naissance.code_elevage == code,
                Naissance.actif == True
            ).all()
            for a in animaux:
                self.animal_combo.addItem(
                    f"{a.numero_boucle} (né le {a.date_naissance})",
                    a.numero_boucle
                )
            self.animal_combo.setEnabled(len(animaux) > 0)
        finally:
            db.close()
        self.load_table()

    def load_table(self):
        """Charge les ventes de l'élevage sélectionné."""
        code = self.code_combo.currentText().strip()
        if not code:
            self.table.setRowCount(0)
            return

        db = SessionLocal()
        try:
            ventes = db.query(Vente).filter(
                Vente.code_elevage == code
            ).order_by(Vente.date_vente.desc()).all()
        finally:
            db.close()

        self.table.setRowCount(len(ventes))
        for i, v in enumerate(ventes):
            self.table.setItem(i, 0, QTableWidgetItem(str(v.id)))
            self.table.setItem(i, 1, QTableWidgetItem(v.numero_boucle))
            self.table.setItem(i, 2, QTableWidgetItem(v.date_vente))
            self.table.setItem(i, 3, QTableWidgetItem(str(v.prix_vente)))
            self.table.setItem(i, 4, QTableWidgetItem(v.lieu_vente))
            self.table.setItem(i, 5, QTableWidgetItem(str(v.poids_vente) if v.poids_vente else ""))
            self.table.setItem(i, 6, QTableWidgetItem(v.remarque or ""))
        self.table.resizeColumnsToContents()

    def charger_selection(self):
        """Double-clic : charge la vente sélectionnée dans le formulaire."""
        row = self.table.currentRow()
        if row < 0:
            return
        self.current_id = int(self.table.item(row, 0).text())
        boucle = self.table.item(row, 1).text()
        date_vente = self.table.item(row, 2).text()
        prix = self.table.item(row, 3).text()
        lieu = self.table.item(row, 4).text()
        poids = self.table.item(row, 5).text()
        remarque = self.table.item(row, 6).text()

        # Charger l'animal dans la combo
        for i in range(self.animal_combo.count()):
            if self.animal_combo.itemText(i).startswith(boucle):
                self.animal_combo.setCurrentIndex(i)
                break
        self.date_vente.setDate(QDate.fromString(date_vente, "yyyy-MM-dd"))
        self.prix_vente.setText(prix)
        self.lieu_vente.setText(lieu)
        self.poids_vente.setText(poids)
        self.remarque.setText(remarque)
        self.btn_save.setText("Mettre à jour")

    def annuler(self):
        """Réinitialise le formulaire."""
        self.current_id = None
        self.animal_combo.setCurrentIndex(-1)
        self.date_vente.setDate(QDate.currentDate())
        self.prix_vente.clear()
        self.lieu_vente.clear()
        self.poids_vente.clear()
        self.remarque.clear()
        self.btn_save.setText("Sauvegarder")
        self.on_eleveur_changed()

    def enregistrer(self):
        """Enregistre ou met à jour une vente."""
        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        # Récupérer l'animal
        numero_boucle = self.animal_combo.currentData()
        if not numero_boucle:
            texte = self.animal_combo.currentText().strip()
            if texte:
                numero_boucle = texte
            else:
                QMessageBox.warning(self, "Erreur", "Choisissez ou saisissez un animal.")
                return

        # Valider les champs obligatoires
        if not self.prix_vente.text().strip():
            QMessageBox.warning(self, "Erreur", "Le prix est obligatoire.")
            return
        if not self.lieu_vente.text().strip():
            QMessageBox.warning(self, "Erreur", "Le lieu est obligatoire.")
            return

        try:
            prix = float(self.prix_vente.text())
            if prix <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Erreur", "Prix invalide.")
            return

        poids = None
        if self.poids_vente.text().strip():
            try:
                poids = float(self.poids_vente.text())
                if poids <= 0:
                    raise ValueError
            except:
                QMessageBox.warning(self, "Erreur", "Poids invalide.")
                return

        date_vente = self.date_vente.date().toString("yyyy-MM-dd")
        lieu = self.lieu_vente.text().strip()
        remarque = self.remarque.text().strip() or None

        db = SessionLocal()
        try:
            # Vérifier que l'animal existe et est actif
            naissance = db.query(Naissance).filter(
                Naissance.code_elevage == code,
                Naissance.numero_boucle == numero_boucle
            ).first()
            if not naissance:
                QMessageBox.warning(self, "Erreur", "Animal introuvable dans cet élevage.")
                return
            if not naissance.actif:
                QMessageBox.warning(self, "Erreur", "Cet animal n'est plus actif.")
                return

            if self.current_id is None:
                # Création
                vente = Vente(
                    code_elevage=code,
                    numero_boucle=numero_boucle,
                    date_vente=date_vente,
                    prix_vente=prix,
                    lieu_vente=lieu,
                    poids_vente=poids,
                    remarque=remarque
                )
                db.add(vente)
                # Marquer l'animal comme inactif
                naissance.actif = False
            else:
                # Modification
                vente = db.query(Vente).filter(Vente.id == self.current_id).first()
                if not vente:
                    QMessageBox.warning(self, "Erreur", "Vente introuvable.")
                    return
                ancien_boucle = vente.numero_boucle
                if numero_boucle != ancien_boucle:
                    # Réactiver l'ancien
                    ancien = db.query(Naissance).filter(
                        Naissance.code_elevage == code,
                        Naissance.numero_boucle == ancien_boucle
                    ).first()
                    if ancien:
                        ancien.actif = True
                    # Désactiver le nouveau
                    nouveau = db.query(Naissance).filter(
                        Naissance.code_elevage == code,
                        Naissance.numero_boucle == numero_boucle
                    ).first()
                    if nouveau:
                        nouveau.actif = False
                # Mettre à jour les champs
                vente.numero_boucle = numero_boucle
                vente.date_vente = date_vente
                vente.prix_vente = prix
                vente.lieu_vente = lieu
                vente.poids_vente = poids
                vente.remarque = remarque

            db.commit()
            QMessageBox.information(self, "Succès", "Vente enregistrée.")
            self.load_table()
            self.annuler()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()

    def supprimer(self):
        """Supprime la vente et réactive l'animal."""
        if self.current_id is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une vente à supprimer.")
            return
        reply = QMessageBox.question(self, "Confirmation",
                                     "Supprimer cette vente ? L'animal sera réactivé.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        db = SessionLocal()
        try:
            vente = db.query(Vente).filter(Vente.id == self.current_id).first()
            if not vente:
                QMessageBox.warning(self, "Erreur", "Vente introuvable.")
                return
            # Réactiver l'animal
            naissance = db.query(Naissance).filter(
                Naissance.code_elevage == vente.code_elevage,
                Naissance.numero_boucle == vente.numero_boucle
            ).first()
            if naissance:
                naissance.actif = True
            db.delete(vente)
            db.commit()
            QMessageBox.information(self, "Succès", "Vente supprimée.")
            self.load_table()
            self.annuler()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()