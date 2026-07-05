# main.py
import sys
import os
from PySide6.QtWidgets import QApplication, QDialog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.windows.main_window import MainWindow
from ui.windows.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)

    login = LoginWindow()
    if login.exec() == QDialog.Accepted:
        role = getattr(login, 'user_role', 'admin')
        code_elevage = getattr(login, 'user_code', '0000')
        window = MainWindow(role=role, code_elevage=code_elevage)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()

if __name__ == "__main__":
    main()