# ui/windows/export_onssa_window.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QPushButton,
                               QDateEdit, QLabel, QMessageBox, QFileDialog)
from PySide6.QtCore import QDate
from controllers.export_onssa_controller import ExportONSSAController

class ExportONSSAWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export ONSSA")
        self.setFixedSize(500, 300)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate(2024, 1, 1))
        self.date_debut.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Date début (optionnelle) :", self.date_debut)

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Date fin (optionnelle) :", self.date_fin)

        layout.addLayout(form)

        self.btn_export = QPushButton("Choisir le fichier de destination et exporter")
        self.btn_export.clicked.connect(self.exporter)
        layout.addWidget(self.btn_export)

        self.label_info = QLabel("L'export génère un fichier CSV au format ONSSA.\n"
                                 "Les dates permettent de filtrer les événements.\n"
                                 "Laissez vides pour tout exporter.")
        self.label_info.setWordWrap(True)
        layout.addWidget(self.label_info)

    def exporter(self):
        debut = self.date_debut.date().toString("yyyy-MM-dd")
        fin = self.date_fin.date().toString("yyyy-MM-dd")
        if debut == "2024-01-01":
            debut = None
        if fin == QDate.currentDate().toString("yyyy-MM-dd"):
            fin = None

        chemin, _ = QFileDialog.getSaveFileName(self, "Enregistrer l'export ONSSA", "export_onssa.csv", "CSV (*.csv)")
        if not chemin:
            return

        nb, err = ExportONSSAController.exporter_animaux(chemin, debut, fin)
        if err:
            QMessageBox.critical(self, "Erreur", f"L'export a échoué : {err}")
        else:
            QMessageBox.information(self, "Export réussi", f"{nb} animaux exportés vers {chemin}")
            self.close()