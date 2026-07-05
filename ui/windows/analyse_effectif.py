from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QPushButton, QSplitter,
                               QFrame, QGridLayout)
from PySide6.QtCore import Qt
from database.db_session import SessionLocal
from database.models import Animal, Eleveur, Naissance
from sqlalchemy import func, literal
from collections import defaultdict
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class AnalyseEffectifWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Effectif par commune et catégorie - avec graphiques")
        self.resize(1200, 800)
        layout = QVBoxLayout(self)

        self.label = QLabel("Effectifs des animaux actifs par commune et catégorie")
        layout.addWidget(self.label)

        # Utilisation d'un splitter horizontal pour séparer tableau et graphiques
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Partie gauche : tableau
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.table = QTableWidget()
        left_layout.addWidget(self.table)
        splitter.addWidget(left_widget)

        # Partie droite : graphiques
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        # Graphique 1 : répartition par sexe
        self.sexe_chart_label = QLabel("Répartition par sexe")
        self.sexe_chart_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.sexe_chart_label)
        self.sexe_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        right_layout.addWidget(self.sexe_canvas)
        # Graphique 2 : répartition par commune (top 10)
        self.commune_chart_label = QLabel("Répartition par commune (10 principales)")
        self.commune_chart_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.commune_chart_label)
        self.commune_canvas = FigureCanvas(Figure(figsize=(4, 4)))
        right_layout.addWidget(self.commune_canvas)
        right_layout.addStretch()
        splitter.addWidget(right_widget)

        # Résumé statistique
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
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
        db = SessionLocal()
        data = defaultdict(lambda: defaultdict(int))
        totals_by_commune = defaultdict(int)
        # Compteur par sexe (en combinant Naissance et Animal)
        sexe_counts = {'M': 0, 'F': 0}

        # 1. Animaux adultes (table Animal)
        animaux = db.query(
            Eleveur.commune,
            Animal.categorie,
            Animal.sexe,
            func.count(Animal.id)
        ).join(Eleveur, Animal.code_elevage == Eleveur.code_elevage
        ).filter(Animal.actif == True
        ).group_by(Eleveur.commune, Animal.categorie, Animal.sexe).all()
        for commune, cat, sexe, cnt in animaux:
            data[commune][cat] += cnt
            totals_by_commune[commune] += cnt
            if sexe in ['M', 'F']:
                sexe_counts[sexe] += cnt

        # 2. Jeunes (table Naissance) – catégorie "Jeune"
        jeunes = db.query(
            Eleveur.commune,
            literal('Jeune').label('categorie'),
            Naissance.sexe,
            func.count(Naissance.id)
        ).join(Eleveur, Naissance.code_elevage == Eleveur.code_elevage
        ).filter(Naissance.actif == True
        ).group_by(Eleveur.commune, Naissance.sexe).all()
        for commune, cat, sexe, cnt in jeunes:
            data[commune][cat] += cnt
            totals_by_commune[commune] += cnt
            if sexe in ['M', 'F']:
                sexe_counts[sexe] += cnt

        if not data:
            self.table.setRowCount(0)
            self.label.setText("Aucune donnée")
            self.summary_label.setText("")
            db.close()
            return

        # Construction du tableau
        categories = sorted(set(c for d in data.values() for c in d.keys()))
        self.table.setRowCount(len(data))
        self.table.setColumnCount(1 + len(categories))
        self.table.setHorizontalHeaderLabels(["Commune"] + categories)

        for i, (commune, cats) in enumerate(data.items()):
            self.table.setItem(i, 0, QTableWidgetItem(commune))
            for j, cat in enumerate(categories):
                val = cats.get(cat, 0)
                self.table.setItem(i, j+1, QTableWidgetItem(str(val)))

        self.table.resizeColumnsToContents()

        # Statistiques
        if totals_by_commune:
            total_animaux = sum(totals_by_commune.values())
            nb_communes = len(totals_by_commune)
            moyenne = total_animaux / nb_communes
            commune_max = max(totals_by_commune, key=totals_by_commune.get)
            commune_min = min(totals_by_commune, key=totals_by_commune.get)
            self.summary_label.setText(
                f"📊 Statistiques : Total général {total_animaux} animaux | "
                f"Moyenne par commune : {moyenne:.1f} | "
                f"Commune avec le plus d'animaux : {commune_max} ({totals_by_commune[commune_max]}) | "
                f"Commune avec le moins d'animaux : {commune_min} ({totals_by_commune[commune_min]})"
            )
        else:
            self.summary_label.setText("Aucune donnée")

        # --- Graphique 1 : Répartition par sexe ---
        self.update_pie_chart_sexe(sexe_counts)

        # --- Graphique 2 : Répartition par commune (10 premières) ---
        communes_triees = sorted(totals_by_commune.items(), key=lambda x: x[1], reverse=True)[:10]
        self.update_pie_chart_commune(communes_triees)

        db.close()

    def update_pie_chart_sexe(self, counts):
        self.sexe_canvas.figure.clear()
        ax = self.sexe_canvas.figure.add_subplot(111)
        labels = []
        sizes = []
        for sexe, cnt in counts.items():
            if cnt > 0:
                labels.append('Mâles' if sexe == 'M' else 'Femelles')
                sizes.append(cnt)
        if not sizes:
            ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center')
        else:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        ax.set_title("Répartition par sexe")
        self.sexe_canvas.draw()

    def update_pie_chart_commune(self, communes):
        self.commune_canvas.figure.clear()
        ax = self.commune_canvas.figure.add_subplot(111)
        if not communes:
            ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center')
        else:
            labels = [c[0] for c in communes]
            sizes = [c[1] for c in communes]
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        ax.set_title("Répartition par commune (10 principales)")
        self.commune_canvas.draw()