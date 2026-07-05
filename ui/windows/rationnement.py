# ui/windows/rationnement.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QComboBox, QLineEdit, QPushButton, QDateEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                               QApplication, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt
from database.db_session import SessionLocal
from database.models import Eleveur, Aliment, Ration, CompositionRation, MouvementStock
from database.models import BesoinNutritionnel, BibliothequeAliment
from datetime import date

class RationnementWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie et consultation des rations")
        self.resize(1200, 700)
        layout = QVBoxLayout(self)

        # ==================== FORMULAIRE (HAUT) ====================
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

        # Race (pour la bibliothèque des besoins)
        self.race_combo = QComboBox()
        self.race_combo.setEditable(True)
        self.race_combo.addItems(self.get_all_races())
        self.race_combo.setPlaceholderText("Race (ex: Oulmès-Zaer)")
        form_layout.addRow(QLabel("Race :"), self.race_combo)

        # Catégorie
        self.categorie_combo = QComboBox()
        self.categorie_combo.addItems(["Veau", "Velle", "Génisse", "Taurillon", "Vache", "Géniteur"])
        form_layout.addRow(QLabel("Catégorie :"), self.categorie_combo)

        # Poids actuel
        self.poids_edit = QDoubleSpinBox()
        self.poids_edit.setRange(0, 2000)
        self.poids_edit.setSingleStep(1)
        self.poids_edit.setSuffix(" kg")
        form_layout.addRow(QLabel("Poids actuel :"), self.poids_edit)

        # Production laitière (kg/j)
        self.lait_edit = QDoubleSpinBox()
        self.lait_edit.setRange(0, 80)
        self.lait_edit.setSingleStep(0.5)
        self.lait_edit.setSuffix(" kg/j")
        self.lait_edit.setValue(0)
        form_layout.addRow(QLabel("Production laitière (kg/j) :"), self.lait_edit)

        # Production de viande (g/j)
        self.viande_edit = QDoubleSpinBox()
        self.viande_edit.setRange(0, 5000)
        self.viande_edit.setSingleStep(10)
        self.viande_edit.setSuffix(" g/j")
        self.viande_edit.setValue(0)
        form_layout.addRow(QLabel("Gain de viande (g/j) :"), self.viande_edit)

        # ==================== BOUTONS ====================
        btn_layout = QHBoxLayout()
        self.btn_calculer = QPushButton("Calculer la ration")
        self.btn_calculer.clicked.connect(self.calculer_ration)
        self.btn_save = QPushButton("Sauvegarder la ration")
        self.btn_save.clicked.connect(self.sauvegarder_ration)
        self.btn_new = QPushButton("Nouveau")
        self.btn_new.clicked.connect(self.nouveau)
        self.btn_close = QPushButton("Fermer")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_calculer)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        form_layout.addRow(btn_layout)

        layout.addWidget(form_group)

        # ==================== SÉPARATEUR ====================
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        layout.addWidget(sep)

        # ==================== TABLEAU DES ALIMENTS (BAS) ====================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Aliment", "Stock (kg)", "Quantité proposée (kg)",
            "UFV", "UFL", "PDI (g)", "Coût (DH)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # ==================== RÉCAPITULATIF ====================
        self.recap_label = QLabel("Besoins : UFV=0.00 | UFL=0.00 | PDI=0.0 g | Apports : UFV=0.00 | UFL=0.00 | PDI=0.0 g")
        self.recap_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.recap_label)

        self.current_id = None
        self.aliments_disponibles = []
        self.on_eleveur_changed()

    # ==================== MÉTHODES ====================
    def get_all_codes(self):
        db = SessionLocal()
        try:
            return [e.code_elevage for e in db.query(Eleveur).all()]
        finally:
            db.close()

    def get_all_races(self):
        db = SessionLocal()
        try:
            races = db.query(BesoinNutritionnel.race).distinct().all()
            return [r[0] for r in races]
        except:
            return ["Oulmès-Zaer"]
        finally:
            db.close()

    def on_eleveur_changed(self):
        code = self.code_combo.currentText().strip()
        self.aliments_disponibles = []
        if not code:
            return

        db = SessionLocal()
        try:
            aliments = db.query(Aliment).filter(Aliment.code_elevage == code).all()
            for a in aliments:
                # Calcul du stock actuel
                entrees = db.query(MouvementStock).filter(
                    MouvementStock.aliment_id == a.id,
                    MouvementStock.type == "entree"
                )
                sorties = db.query(MouvementStock).filter(
                    MouvementStock.aliment_id == a.id,
                    MouvementStock.type == "sortie"
                )
                total_entrees = sum([m.quantite for m in entrees]) if entrees else 0
                total_sorties = sum([m.quantite for m in sorties]) if sorties else 0
                stock_actuel = a.stock_initial + total_entrees - total_sorties
                if stock_actuel > 0:
                    # Récupérer les valeurs nutritionnelles depuis la bibliothèque des aliments
                    biblio = db.query(BibliothequeAliment).filter(BibliothequeAliment.nom == a.nom).first()
                    ufl = biblio.ufl if biblio else a.ufl  # fallback sur les valeurs de Aliment
                    ufv = biblio.ufv if biblio else a.ufv
                    pdi = biblio.pdi if biblio else a.pdi
                    prix = biblio.prix_kg if biblio else a.prix_kg or 0
                    self.aliments_disponibles.append({
                        'id': a.id,
                        'nom': a.nom,
                        'ufl': ufl or 0,
                        'ufv': ufv or 0,
                        'pdi': pdi or 0,
                        'prix': prix or 0,
                        'stock': stock_actuel
                    })
        finally:
            db.close()

    def get_besoins_from_library(self):
        """Récupère les besoins depuis la bibliothèque des besoins."""
        race = self.race_combo.currentText().strip()
        categorie = self.categorie_combo.currentText()
        poids = self.poids_edit.value()
        lait = self.lait_edit.value()

        db = SessionLocal()
        try:
            # Rechercher un besoin correspondant (race, catégorie, poids)
            besoin = db.query(BesoinNutritionnel).filter(
                BesoinNutritionnel.race == race,
                BesoinNutritionnel.categorie == categorie,
                BesoinNutritionnel.poids_min <= poids,
                BesoinNutritionnel.poids_max >= poids
            ).first()
            if not besoin:
                # Essayer avec catégorie seulement (sans race)
                besoin = db.query(BesoinNutritionnel).filter(
                    BesoinNutritionnel.categorie == categorie,
                    BesoinNutritionnel.poids_min <= poids,
                    BesoinNutritionnel.poids_max >= poids
                ).first()
        finally:
            db.close()

        if besoin:
            # Besoins trouvés dans la bibliothèque
            ufl = besoin.ufl
            ufv = besoin.ufv
            pdi = besoin.pdi
            # Ajout de la production (lait ou viande) si spécifiée
            if lait > 0:
                ufl += lait * 0.03
                ufv += lait * 0.03
                pdi += lait * 6
            # Majoration de 5.5% pour la marche
            ufl *= 1.055
            ufv *= 1.055
            pdi *= 1.055
            return {'ufl': round(ufl, 2), 'ufv': round(ufv, 2), 'pdi': round(pdi, 1)}
        else:
            # Fallback : calcul approximatif (comme avant)
            ufl = 0.0
            ufv = 0.0
            pdi = 0.0
            if categorie in ["Veau", "Velle"]:
                ufl = 0.4 + poids * 0.001
                ufv = 0.4 + poids * 0.001
                pdi = 40 + poids * 0.5
            elif categorie in ["Génisse", "Taurillon"]:
                ufl = 0.5 + poids * 0.0015
                ufv = 0.5 + poids * 0.0015
                pdi = 50 + poids * 0.6
                if self.viande_edit.value() > 0:
                    ufl += self.viande_edit.value() * 0.0003
                    ufv += self.viande_edit.value() * 0.0003
                    pdi += self.viande_edit.value() * 0.05
            elif categorie == "Vache":
                if lait > 0:
                    ufl = 0.6 + poids * 0.001 + lait * 0.03
                    ufv = 0.6 + poids * 0.001 + lait * 0.03
                    pdi = 60 + poids * 0.4 + lait * 6
                else:
                    ufl = 0.5 + poids * 0.0008
                    ufv = 0.5 + poids * 0.0008
                    pdi = 50 + poids * 0.3
            elif categorie == "Géniteur":
                ufl = 0.5 + poids * 0.0008
                ufv = 0.5 + poids * 0.0008
                pdi = 50 + poids * 0.3
            ufl *= 1.055
            ufv *= 1.055
            pdi *= 1.055
            return {'ufl': round(ufl, 2), 'ufv': round(ufv, 2), 'pdi': round(pdi, 1)}

    def calculer_besoins(self):
        """Appelle la méthode de recherche dans la bibliothèque."""
        return self.get_besoins_from_library()

    def calculer_ration(self):
        """Calcule la ration optimale à partir du stock disponible."""
        besoins = self.calculer_besoins()
        self.table.setRowCount(0)

        if not self.aliments_disponibles:
            QMessageBox.warning(self, "Erreur", "Aucun aliment disponible dans le stock.")
            return

        # Trier les aliments par UFV décroissant (priorité aux plus énergétiques)
        aliments_tries = sorted(self.aliments_disponibles, key=lambda x: x['ufv'], reverse=True)

        total_ufl = 0
        total_ufv = 0
        total_pdi = 0
        total_cout = 0
        lignes = []

        for a in aliments_tries:
            if total_ufv >= besoins['ufv'] and total_ufl >= besoins['ufl'] and total_pdi >= besoins['pdi']:
                break

            besoin_restant_ufv = max(0, besoins['ufv'] - total_ufv)
            besoin_restant_ufl = max(0, besoins['ufl'] - total_ufl)
            besoin_restant_pdi = max(0, besoins['pdi'] - total_pdi)

            qte_ufv = besoin_restant_ufv / max(a['ufv'], 0.001)
            qte_ufl = besoin_restant_ufl / max(a['ufl'], 0.001)
            qte_pdi = besoin_restant_pdi / max(a['pdi'], 0.001)

            qte = max(qte_ufv, qte_ufl, qte_pdi)
            qte = min(qte, a['stock'])

            if qte > 0:
                lignes.append({
                    'nom': a['nom'],
                    'quantite': qte,
                    'stock': a['stock'],
                    'ufl': a['ufl'],
                    'ufv': a['ufv'],
                    'pdi': a['pdi'],
                    'prix': a['prix']
                })
                total_ufl += qte * a['ufl']
                total_ufv += qte * a['ufv']
                total_pdi += qte * a['pdi']
                total_cout += qte * a['prix']

        self.table.setRowCount(len(lignes))
        for i, ligne in enumerate(lignes):
            self.table.setItem(i, 0, QTableWidgetItem(ligne['nom']))
            self.table.setItem(i, 1, QTableWidgetItem(f"{ligne['stock']:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{ligne['quantite']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{ligne['ufv']:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{ligne['ufl']:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{ligne['pdi']:.1f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{ligne['prix'] * ligne['quantite']:.2f}"))

        self.recap_label.setText(
            f"Besoins : UFV={besoins['ufv']:.2f} | UFL={besoins['ufl']:.2f} | PDI={besoins['pdi']:.1f} g   |   "
            f"Apports : UFV={total_ufv:.2f} | UFL={total_ufl:.2f} | PDI={total_pdi:.1f} g   |   "
            f"Coût total : {total_cout:.2f} DH"
        )
        self.table.resizeColumnsToContents()
        QMessageBox.information(self, "Info", "Ration calculée avec succès.\nLes besoins ont été majorés de 5.5% pour la marche.")

    def nouveau(self):
        """Réinitialise le formulaire."""
        self.code_combo.setCurrentIndex(-1)
        self.code_combo.setEditText("")
        self.race_combo.setCurrentIndex(0)
        self.categorie_combo.setCurrentIndex(0)
        self.poids_edit.setValue(0)
        self.lait_edit.setValue(0)
        self.viande_edit.setValue(0)
        self.table.setRowCount(0)
        self.recap_label.setText("Besoins : UFV=0.00 | UFL=0.00 | PDI=0.0 g | Apports : UFV=0.00 | UFL=0.00 | PDI=0.0 g")
        self.current_id = None
        self.on_eleveur_changed()

    def sauvegarder_ration(self):
        """Sauvegarde la ration calculée."""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Erreur", "Calculez d'abord une ration.")
            return

        code = self.code_combo.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Erreur", "Choisissez un élevage.")
            return

        besoins = self.calculer_besoins()

        db = SessionLocal()
        try:
            ration = Ration(
                code_elevage=code,
                nom="Ration du " + date.today().strftime("%Y-%m-%d"),
                date_creation=date.today().strftime("%Y-%m-%d"),
                poids_vif=self.poids_edit.value(),
                production_lait=self.lait_edit.value(),
                stade=self.categorie_combo.currentText(),
                observations=f"Besoin majore 5.5% | UFL={besoins['ufl']} | UFV={besoins['ufv']} | PDI={besoins['pdi']}"
            )
            db.add(ration)
            db.flush()

            for row in range(self.table.rowCount()):
                nom_aliment = self.table.item(row, 0).text()
                quantite = float(self.table.item(row, 2).text())
                aliment = db.query(Aliment).filter(Aliment.nom == nom_aliment, Aliment.code_elevage == code).first()
                if aliment:
                    comp = CompositionRation(
                        ration_id=ration.id,
                        aliment_id=aliment.id,
                        quantite=quantite
                    )
                    db.add(comp)

            db.commit()
            QMessageBox.information(self, "Succès", "Ration sauvegardée.")
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            db.close()