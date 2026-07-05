from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aide - GESTROZ")
        self.setFixedSize(600, 500)
        layout = QVBoxLayout(self)
        
        title = QLabel("📖 Aide de GESTROZ")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setHtml(self.get_help_content())
        layout.addWidget(self.text_browser)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)
    
    def get_help_content(self):
        return """
        <h2>Bienvenue dans GESTROZ</h2>
        <p>Application de gestion d'élevage bovin (race Oulmès-Zaïr).</p>
        
        <h3>Menu Exploitation</h3>
        <ul>
            <li><b>Ajouter un éleveur</b> : saisie avec génération automatique du code (OLM/AIT/BOK).</li>
            <li><b>Gérer les éleveurs</b> : modifier, supprimer, consulter.</li>
            <li><b>Ajouter un animal</b> : saisie avec catégorie automatique (âge/sexe).</li>
            <li><b>Gérer les animaux</b> : modifier, supprimer, consulter.</li>
        </ul>
        
        <h3>Suivi technique et sanitaire</h3>
        <ul>
            <li><b>Naissances</b> : enregistrement d'une naissance, création de l'animal.</li>
            <li><b>Sevrages</b> : calcul du GMQ.</li>
            <li><b>Croissance</b> : pesées post-sevrage avec GMQ.</li>
            <li><b>Mortalité</b> : déclaration d'un décès.</li>
            <li><b>Ventes</b> : enregistrement d'une vente, désactivation de l'animal.</li>
        </ul>
        
        <h3>Alimentation</h3>
        <ul>
            <li><b>Stocks</b> : ajout de lots d'aliments (bibliothèque avec UFL/PDI).</li>
        </ul>
        
        <h3>Outils</h3>
        <ul>
            <li><b>Import/Export Excel</b> : à venir.</li>
            <li><b>Sauvegarde</b> : copie de la base de données.</li>
            <li><b>À propos</b> : informations sur le logiciel.</li>
        </ul>
        
        <h3>Raccourcis clavier</h3>
        <ul>
            <li><b>F1</b> : ouvrir l'aide</li>
            <li><b>Ctrl+Q</b> : quitter l'application (dans le menu)</li>
        </ul>
        
        <hr>
        <p>© 2026 Idriss MOUMEN - PCM Consulting<br>Email : moumen.idriss@gmail.com</p>
        """