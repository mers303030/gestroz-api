# ui/windows/gestion_economique.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from database.models import Eleveur  # <-- CORRECTION

class GestionEconomiqueWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion économique")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Fenêtre Gestion économique en cours de développement..."))