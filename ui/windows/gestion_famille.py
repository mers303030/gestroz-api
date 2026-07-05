# ui/windows/gestion_famille.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from database.models import Eleveur  # <-- CORRECTION

class GestionFamilleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion de la famille")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Fenêtre Gestion de la famille en cours de développement..."))