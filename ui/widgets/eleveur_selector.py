from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox, QCompleter
from PySide6.QtCore import Qt
from database.db_session import SessionLocal
from database.models.eleveur import Eleveur

class EleveurSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Tapez code ou nom...")
        layout.addWidget(self.line_edit)
        self.combo_cache = QComboBox()
        self.combo_cache.hide()
        self.load_eleveurs()
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setModel(self.combo_cache.model())
        self.line_edit.setCompleter(completer)
        self._current_code = None

    def load_eleveurs(self):
        db = SessionLocal()
        eleveurs = db.query(Eleveur).all()
        for e in eleveurs:
            self.combo_cache.addItem(f"{e.code_elevage} - {e.nom} {e.prenom}", e.code_elevage)
        db.close()

    def get_code(self):
        text = self.line_edit.text().strip()
        for i in range(self.combo_cache.count()):
            if self.combo_cache.itemText(i).startswith(text):
                return self.combo_cache.itemData(i)
        return None

    def set_code(self, code):
        for i in range(self.combo_cache.count()):
            if self.combo_cache.itemData(i) == code:
                self.line_edit.setText(self.combo_cache.itemText(i))
                self._current_code = code
                return
        self.line_edit.clear()
        self._current_code = None

    def text(self):
        return self.line_edit.text()

    def clear(self):
        self.line_edit.clear()
        self._current_code = None