from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QPushButton, QDateEdit,
                               QFormLayout)
from PySide6.QtCore import QDate
from database.db_session import SessionLocal
from database.models import Naissance, Eleveur
from collections import defaultdict
from math import sqrt

class AnalyseCroissanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyse de la croissance (GMQ) par commune et sexe")
        self.resize(1000, 700)
        layout = QVBoxLayout(self)

        # Filtres période (optionnel, basé sur la date de naissance)
        filter_layout = QFormLayout()
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate(2026, 1, 1))
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        filter_layout.addRow("Période (naissance entre) :", self.date_debut)
        filter_layout.addRow("et", self.date_fin)

        self.btn_filter = QPushButton("Filtrer")
        self.btn_filter.clicked.connect(self.load_data)
        filter_layout.addRow(self.btn_filter)

        layout.addLayout(filter_layout)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Commune", "Sexe", "Effectif",
            "GMQ Moyen (g/j)", "GMQ Min (g/j)", "GMQ Max (g/j)", "Écart-type"
        ])
        layout.addWidget(self.table)

        # Résumé global
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
        # Récupérer tous les GMQ individuels par commune et sexe
        rows = db.query(
            Eleveur.commune,
            Naissance.sexe,
            Naissance.gmq_naissance_sevrage
        ).join(Eleveur, Naissance.code_elevage == Eleveur.code_elevage
        ).filter(
            Naissance.sevre == True,
            Naissance.gmq_naissance_sevrage != None,
            Naissance.date_naissance.between(debut, fin)
        ).all()

        if not rows:
            self.table.setRowCount(0)
            self.summary_label.setText("Aucune donnée de GMQ dans la période sélectionnée")
            db.close()
            return

        # Agrégation manuelle
        data = defaultdict(lambda: {
            'values': [],
            'sum': 0.0,
            'count': 0,
            'min': None,
            'max': None
        })

        for commune, sexe, gmq in rows:
            key = (commune, sexe)
            data[key]['values'].append(gmq)
            data[key]['sum'] += gmq
            data[key]['count'] += 1
            if data[key]['min'] is None or gmq < data[key]['min']:
                data[key]['min'] = gmq
            if data[key]['max'] is None or gmq > data[key]['max']:
                data[key]['max'] = gmq

        self.table.setRowCount(len(data))
        total_animaux = 0
        sum_gmq = 0.0

        for i, ((commune, sexe), stats) in enumerate(data.items()):
            count = stats['count']
            avg = stats['sum'] / count
            # Calcul de l'écart-type (population)
            variance = sum((x - avg) ** 2 for x in stats['values']) / count
            stddev = sqrt(variance)

            self.table.setItem(i, 0, QTableWidgetItem(commune))
            self.table.setItem(i, 1, QTableWidgetItem(sexe))
            self.table.setItem(i, 2, QTableWidgetItem(str(count)))
            self.table.setItem(i, 3, QTableWidgetItem(f"{avg:.1f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{stats['min']:.1f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{stats['max']:.1f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{stddev:.1f}"))

            total_animaux += count
            sum_gmq += avg * count

        self.table.resizeColumnsToContents()

        moyenne_globale = sum_gmq / total_animaux if total_animaux else 0
        self.summary_label.setText(
            f"📊 Total animaux dans l'analyse : {total_animaux} | "
            f"GMQ moyen général : {moyenne_globale:.1f} g/j"
        )
        db.close()