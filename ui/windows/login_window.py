# ui/windows/login_window.py
import hashlib
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QApplication
from PySide6.QtCore import Qt, QTimer
from database.db_session import SessionLocal
from database.models.user import User

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GESTROZ - Connexion")
        self.setFixedSize(400, 350)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowTitleHint)

        self.setStyleSheet("""
            QDialog {
                background-color: #2c2c2c;
            }
            QFrame {
                background-color: #3a3a3a;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-family: "Segoe UI", "Microsoft Sans Serif", sans-serif;
                font-size: 14px;
                color: #f0f0f0;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #5a5a5a;
                border-radius: 5px;
                background-color: #555;
                color: white;
                selection-background-color: #27ae60;
            }
            QLineEdit:focus {
                border: 1px solid #27ae60;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QLabel#flash {
                color: #f39c12;
                font-size: 13px;
                font-weight: bold;
                font-style: italic;
            }
        """)

        main_frame = QFrame(self)
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        title = QLabel("🐄 GESTROZ")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur")
        main_layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        main_layout.addWidget(self.password)

        self.btn_login = QPushButton("Se connecter")
        self.btn_login.clicked.connect(self.login)
        main_layout.addWidget(self.btn_login)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.error_label)

        self.flash_label = QLabel("Patienter, le chargement de votre programme est en cours...")
        self.flash_label.setObjectName("flash")
        self.flash_label.setAlignment(Qt.AlignCenter)
        self.flash_label.setVisible(False)
        main_layout.addWidget(self.flash_label)

        main_layout.addStretch()

        central_layout = QVBoxLayout(self)
        central_layout.addWidget(main_frame)
        central_layout.setContentsMargins(0, 0, 0, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.blink_state = False

    def blink(self):
        self.blink_state = not self.blink_state
        self.flash_label.setVisible(self.blink_state)

    def login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        if not u or not p:
            self.error_label.setText("Veuillez saisir identifiant et mot de passe")
            return
        self.error_label.clear()

        self.flash_label.setText("Veuillez attendre le chargement du programme...")
        self.flash_label.setVisible(True)
        self.blink_state = True
        self.btn_login.setEnabled(False)
        self.timer.start(350)

        QApplication.processEvents()

        user = None
        try:
            hashed = hashlib.md5(p.encode()).hexdigest()
            db = SessionLocal()
            user = db.query(User).filter(User.username == u, User.password == hashed).first()
            db.close()
        except Exception as e:
            self.timer.stop()
            self.flash_label.setVisible(False)
            self.btn_login.setEnabled(True)
            self.error_label.setText("Erreur : Connexion à la base de données impossible.")
            print(f"Détail erreur démarrage : {e}")
            return

        self.timer.stop()
        self.flash_label.setVisible(False)
        self.btn_login.setEnabled(True)

        if user:
            self.user_role = user.role
            self.user_code = user.code_elevage
            self.accept()
        else:
            self.error_label.setText("Identifiants incorrects")