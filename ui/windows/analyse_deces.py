from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QPushButton, QDateEdit,
                               QFormLayout)
from PySide6.QtCore import QDate
from database.db_session import SessionLocal
from database.models import Mortalite, Eleveur, Animal, Naissance
from collections import defaultdict

class AnalyseDecesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyse des décès par commune")
        self.resize(900, 700)
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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Commune", "Catégorie", "Nombre décès", "Causes principales"])
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
        deces = db.query(
            Eleveur.commune,
            Mortalite.code_elevage,
            Mortalite.numero_boucle,
            Mortalite.cause_deces,
            Animal.categorie,
            Naissance.id.label('naissance_id')
        ).join(Eleveur, Mortalite.code_elevage == Eleveur.code_elevage
        ).outerjoin(Animal, (Animal.code_elevage == Mortalite.code_elevage) & (Animal.numero_boucle == Mortalite.numero_boucle)
        ).outerjoin(Naissance, (Naissance.code_elevage == Mortalite.code_elevage) & (Naissance.numero_boucle == Mortalite.numero_boucle)
        ).filter(Mortalite.date_deces.between(debut, fin)).all()

        data = defaultdict(lambda: {'count': 0, 'causes': defaultdict(int)})

        for d in deces:
            if d.categorie:
                cat = d.categorie
            elif d.naissance_id:
                cat = "Jeune"
            else:
                cat = "Indéterminé"
            key = (d.commune, cat)
            data[key]['count'] += 1
            if d.cause_deces:
                data[key]['causes'][d.cause_deces] += 1

        if not data:
            self.table.setRowCount(0)
            self.summary_label.setText("Aucun décès dans la période sélectionnée")
            db.close()
            return

        self.table.setRowCount(len(data))
        for i, ((commune, cat), vals) in enumerate(data.items()):
            self.table.setItem(i, 0, QTableWidgetItem(commune))
            self.table.setItem(i, 1, QTableWidgetItem(cat))
            self.table.setItem(i, 2, QTableWidgetItem(str(vals['count'])))
            causes_sorted = sorted(vals['causes'].items(), key=lambda x: x[1], reverse=True)
            causes_str = ", ".join([f"{cause} ({nb})" for cause, nb in causes_sorted[:2]])
            self.table.setItem(i, 3, QTableWidgetItem(causes_str))

        self.table.resizeColumnsToContents()

        total_deces = sum(v['count'] for v in data.values())
        self.summary_label.setText(f"📊 Total décès : {total_deces}")

        db.close()