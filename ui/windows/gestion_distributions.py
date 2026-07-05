from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox, QComboBox, QLabel)
from database.db_session import SessionLocal
from database.models.eleveur import Eleveur
from database.models.distribution import Distribution
from controllers.distribution_controller import DistributionController

class GestionDistributionsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des distributions")
        self.resize(1000, 500)
        layout = QVBoxLayout(self)

        # Filtre par éleveur
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Éleveur:"))
        self.combo_filtre = QComboBox()
        self.combo_filtre.addItem("Tous", None)
        db = SessionLocal()
        eleveurs = db.query(Eleveur).all()
        for e in eleveurs:
            self.combo_filtre.addItem(f"{e.code_elevage} - {e.nom} {e.prenom}", e.code_elevage)
        db.close()
        self.combo_filtre.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.combo_filtre)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Éleveur", "Date", "Aliment", "Quantité (kg)", "Catégorie", "UFL", "UFV", "PDI"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.clicked.connect(self.load_data)
        btn_supprimer = QPushButton("Supprimer")
        btn_supprimer.clicked.connect(self.supprimer)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_supprimer)
        layout.addLayout(btn_layout)

        self.load_data()

    def load_data(self):
        code_filtre = self.combo_filtre.currentData()
        distributions = DistributionController.get_distributions_par_eleveur(code_filtre)
        self.table.setRowCount(len(distributions))
        db = SessionLocal()
        for i, d in enumerate(distributions):
            aliment = db.query(Aliment).filter(Aliment.id == d.aliment_id).first()
            nom_aliment = aliment.nom if aliment else "?"
            self.table.setItem(i, 0, QTableWidgetItem(str(d.id)))
            self.table.setItem(i, 1, QTableWidgetItem(d.code_elevage))
            self.table.setItem(i, 2, QTableWidgetItem(d.date_distribution))
            self.table.setItem(i, 3, QTableWidgetItem(nom_aliment))
            self.table.setItem(i, 4, QTableWidgetItem(str(d.quantite_kg)))
            self.table.setItem(i, 5, QTableWidgetItem(d.categorie_animale or ""))
            self.table.setItem(i, 6, QTableWidgetItem(f"{d.ufl_apport:.2f}" if d.ufl_apport else ""))
            self.table.setItem(i, 7, QTableWidgetItem(f"{d.ufv_apport:.2f}" if d.ufv_apport else ""))
            self.table.setItem(i, 8, QTableWidgetItem(f"{d.pdi_apport:.0f}" if d.pdi_apport else ""))
        self.table.resizeColumnsToContents()
        db.close()

    def supprimer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez une distribution")
            return
        dist_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cette distribution ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = DistributionController.supprimer_distribution(dist_id)
            if ok:
                QMessageBox.information(self, "Succès", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", msg)