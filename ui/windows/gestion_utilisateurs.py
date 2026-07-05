import hashlib
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox, QFormLayout,
                               QLineEdit, QComboBox, QDialog, QDialogButtonBox)
from database.db_session import SessionLocal
from database.models.user import User
from database.models.eleveur import Eleveur

class AjoutUtilisateurDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un utilisateur")
        self.setModal(True)
        layout = QFormLayout(self)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.role = QComboBox()
        # Liste des rôles selon votre cahier des charges
        self.role.addItems(["admin", "technicien", "operateur", "chef_general", "eleveur"])
        self.code_elevage = QComboBox()
        self.code_elevage.addItem("", None)
        db = SessionLocal()
        eleveurs = db.query(Eleveur).all()
        for e in eleveurs:
            self.code_elevage.addItem(f"{e.code_elevage} - {e.nom}", e.code_elevage)
        db.close()
        self.role.currentTextChanged.connect(self.on_role_changed)
        self.on_role_changed("eleveur")
        layout.addRow("Nom d'utilisateur:", self.username)
        layout.addRow("Mot de passe:", self.password)
        layout.addRow("Rôle:", self.role)
        layout.addRow("Code élevage (pour eleveur):", self.code_elevage)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    def on_role_changed(self, role):
        self.code_elevage.setEnabled(role == "eleveur")
    def get_data(self):
        return {
            'username': self.username.text(),
            'password': hashlib.md5(self.password.text().encode()).hexdigest(),
            'role': self.role.currentText(),
            'code_elevage': self.code_elevage.currentData() if self.role.currentText() == "eleveur" else None
        }

class ModifierUtilisateurDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Modifier utilisateur")
        self.setModal(True)
        layout = QFormLayout(self)
        self.username = QLineEdit(user.username)
        self.password = QLineEdit()
        self.password.setPlaceholderText("Laisser vide pour ne pas changer")
        self.password.setEchoMode(QLineEdit.Password)
        self.role = QComboBox()
        self.role.addItems(["admin", "technicien", "operateur", "chef_general", "eleveur"])
        self.role.setCurrentText(user.role)
        self.code_elevage = QComboBox()
        self.code_elevage.addItem("", None)
        db = SessionLocal()
        eleveurs = db.query(Eleveur).all()
        for e in eleveurs:
            self.code_elevage.addItem(f"{e.code_elevage} - {e.nom}", e.code_elevage)
        db.close()
        if user.code_elevage:
            idx = self.code_elevage.findData(user.code_elevage)
            if idx >= 0:
                self.code_elevage.setCurrentIndex(idx)
        self.role.currentTextChanged.connect(self.on_role_changed)
        self.on_role_changed(user.role)
        layout.addRow("Nom d'utilisateur:", self.username)
        layout.addRow("Nouveau mot de passe:", self.password)
        layout.addRow("Rôle:", self.role)
        layout.addRow("Code élevage:", self.code_elevage)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    def on_role_changed(self, role):
        self.code_elevage.setEnabled(role == "eleveur")
    def get_data(self):
        data = {
            'username': self.username.text(),
            'role': self.role.currentText(),
            'code_elevage': self.code_elevage.currentData() if self.role.currentText() == "eleveur" else None
        }
        if self.password.text().strip():
            data['password'] = hashlib.md5(self.password.text().encode()).hexdigest()
        return data

class GestionUtilisateursWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des utilisateurs")
        self.resize(800, 500)
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Rôle", "Code élevage"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.clicked.connect(self.load_data)
        btn_ajouter = QPushButton("Ajouter")
        btn_ajouter.clicked.connect(self.ajouter)
        btn_modifier = QPushButton("Modifier")
        btn_modifier.clicked.connect(self.modifier)
        btn_supprimer = QPushButton("Supprimer")
        btn_supprimer.clicked.connect(self.supprimer)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_ajouter)
        btn_layout.addWidget(btn_modifier)
        btn_layout.addWidget(btn_supprimer)
        layout.addLayout(btn_layout)
        self.load_data()

    def load_data(self):
        db = SessionLocal()
        users = db.query(User).all()
        self.table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(str(u.id)))
            self.table.setItem(i, 1, QTableWidgetItem(u.username))
            self.table.setItem(i, 2, QTableWidgetItem(u.role))
            self.table.setItem(i, 3, QTableWidgetItem(u.code_elevage or ""))
        self.table.resizeColumnsToContents()
        db.close()

    def ajouter(self):
        dialog = AjoutUtilisateurDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            db = SessionLocal()
            if db.query(User).filter(User.username == data['username']).first():
                QMessageBox.warning(self, "Erreur", "Nom d'utilisateur déjà existant")
                db.close()
                return
            user = User(**data)
            db.add(user)
            db.commit()
            db.close()
            QMessageBox.information(self, "Succès", "Utilisateur ajouté")
            self.load_data()

    def modifier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un utilisateur")
            return
        user_id = int(self.table.item(row, 0).text())
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        if not user:
            return
        dialog = ModifierUtilisateurDialog(user, self)
        if dialog.exec():
            data = dialog.get_data()
            db = SessionLocal()
            if data['username'] != user.username:
                if db.query(User).filter(User.username == data['username']).first():
                    QMessageBox.warning(self, "Erreur", "Nom d'utilisateur déjà existant")
                    db.close()
                    return
            for key, value in data.items():
                setattr(user, key, value)
            db.commit()
            db.close()
            QMessageBox.information(self, "Succès", "Utilisateur modifié")
            self.load_data()

    def supprimer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un utilisateur")
            return
        user_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet utilisateur ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
            db.close()
            self.load_data()