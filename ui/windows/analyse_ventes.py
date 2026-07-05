from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QPushButton, QDateEdit,
                               QFormLayout)
from PySide6.QtCore import QDate
from database.db_session import SessionLocal
from database.models import Vente, Eleveur, Animal, Naissance
from collections import defaultdict

class AnalyseVentesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyse des ventes par commune")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        # Filtres période
        filter_layout = QFormLayout()
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate(2026, 1, 1))
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        filter_layout.addRow("Date début:", self.date_debut)
        filter_layout.addRow("Date fin:", self.date_fin)

        self.btn_filter = QPushButton("Filtrer")
        self.btn_filter.clicked.connect(self.load_data)
        filter_layout.addRow(self.btn_filter)

        layout.addLayout(filter_layout)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Commune", "Catégorie", "Nombre ventes", "Prix moyen (DH)", "Poids moyen (kg)"])
        layout.addWidget(self.table)

        # Résumé
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        # Bouton Fermer
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.load_data()

    def load_data(self):
        debut = self.date_debut.date().toString("yyyy-MM-dd")
        fin = self.date_fin.date().toString("yyyy-MM-dd")

        db = SessionLocal()
        ventes = db.query(
            Eleveur.commune,
            Vente.code_elevage,
            Vente.numero_boucle,
            Vente.prix_vente,
            Vente.poids_vente,
            Animal.categorie,
            Naissance.id.label('naissance_id')
        ).join(Eleveur, Vente.code_elevage == Eleveur.code_elevage
        ).outerjoin(Animal, (Animal.code_elevage == Vente.code_elevage) & (Animal.numero_boucle == Vente.numero_boucle)
        ).outerjoin(Naissance, (Naissance.code_elevage == Vente.code_elevage) & (Naissance.numero_boucle == Vente.numero_boucle)
        ).filter(Vente.date_vente.between(debut, fin)).all()

        data = defaultdict(lambda: {'count': 0, 'sum_prix': 0, 'sum_poids': 0, 'count_poids': 0})

        for v in ventes:
            if v.categorie:
                cat = v.categorie
            elif v.naissance_id:
                cat = "Jeune"
            else:
                cat = "Indéterminé"
            key = (v.commune, cat)
            data[key]['count'] += 1
            data[key]['sum_prix'] += v.prix_vente
            if v.poids_vente:
                data[key]['sum_poids'] += v.poids_vente
                data[key]['count_poids'] += 1

        if not data:
            self.table.setRowCount(0)
            self.summary_label.setText("Aucune vente dans la période sélectionnée")
            db.close()
            return

        self.table.setRowCount(len(data))
        for i, ((commune, cat), vals) in enumerate(data.items()):
            self.table.setItem(i, 0, QTableWidgetItem(commune))
            self.table.setItem(i, 1, QTableWidgetItem(cat))
            self.table.setItem(i, 2, QTableWidgetItem(str(vals['count'])))
            prix_moy = vals['sum_prix'] / vals['count']
            self.table.setItem(i, 3, QTableWidgetItem(f"{prix_moy:.2f}"))
            if vals['count_poids'] > 0:
                poids_moy = vals['sum_poids'] / vals['count_poids']
                self.table.setItem(i, 4, QTableWidgetItem(f"{poids_moy:.1f}"))
            else:
                self.table.setItem(i, 4, QTableWidgetItem(""))

        self.table.resizeColumnsToContents()

        total_ventes = sum(v['count'] for v in data.values())
        total_prix = sum(v['sum_prix'] for v in data.values())
        prix_moyen_global = total_prix / total_ventes if total_ventes else 0
        self.summary_label.setText(f"📊 Total ventes : {total_ventes} | Prix total : {total_prix:.2f} DH | Prix moyen : {prix_moyen_global:.2f} DH")

        db.close()