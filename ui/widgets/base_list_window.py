from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QHeaderView, QLabel, QLineEdit,
                               QPushButton, QMessageBox, QFrame)
from PySide6.QtCore import Qt

class BaseListWindow(QWidget):
    def __init__(self, title="Gestion", search_column_index=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1000, 650)
        self.all_data = []
        self.headers = []
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder
        self.id_column_index = 0
        self.search_column_index = search_column_index

        self.setStyleSheet("background-color: #f0f2f5;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000; margin-bottom: 10px;")
        main_layout.addWidget(self.title_label)

        # Barre d'outils avec bouton Fermer
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Ajouter")
        self.btn_add.clicked.connect(self.add_item)
        self.btn_edit = QPushButton("✏️ Modifier")
        self.btn_edit.clicked.connect(self.edit_item)
        self.btn_delete = QPushButton("🗑️ Supprimer")
        self.btn_delete.clicked.connect(self.delete_item)
        self.btn_refresh = QPushButton("🔄 Rafraîchir")
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_close = QPushButton("❌ Fermer")
        self.btn_close.clicked.connect(self.close)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_close)
        main_layout.addLayout(toolbar)

        # Recherche
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Rechercher :"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Code élevage...")
        self.search_edit.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        # Cadre blanc arrondi
        self.table_frame = QFrame()
        self.table_frame.setObjectName("table_frame")
        self.table_frame.setStyleSheet("""
            #table_frame {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #dddddd;
            }
        """)
        frame_layout = QVBoxLayout(self.table_frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)

        # Tableau
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                gridline-color: #dddddd;
                border: none;
                font-size: 12px;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #8B3A3A;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
            QTableWidget::item {
                padding: 4px;
                color: #000000;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #1E3A8A;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3B5DB0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #f0f0f0;
                height: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #1E3A8A;
                min-width: 20px;
                border-radius: 7px;
            }
        """)
        self.table.doubleClicked.connect(self.edit_item)
        frame_layout.addWidget(self.table)

        main_layout.addWidget(self.table_frame)
        self.load_data()

    # ----- Méthodes à surcharger -----
    def load_data(self):
        raise NotImplementedError

    def add_item(self):
        raise NotImplementedError

    def edit_item_with_id(self, id_value):
        raise NotImplementedError

    def delete_item_with_id(self, id_value):
        raise NotImplementedError

    # ----- Méthodes génériques -----
    def get_selected_id(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        item = self.table.item(current_row, self.id_column_index)
        return item.text() if item else None

    def edit_item(self):
        id_value = self.get_selected_id()
        if id_value is None:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner une ligne.")
            return
        self.edit_item_with_id(id_value)
        self.load_data()

    def delete_item(self):
        id_value = self.get_selected_id()
        if id_value is None:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner une ligne.")
            return
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer {id_value} ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_item_with_id(id_value)
            self.load_data()

    def display_data(self, data):
        self.table.setRowCount(0)
        if not data:
            return
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setForeground(Qt.black)
                self.table.setItem(i, j, item)
        self.table.resizeRowsToContents()

    def filter_data(self):
        text = self.search_edit.text().strip().lower()
        if not text:
            self.display_data(self.all_data)
        else:
            filtered = [row for row in self.all_data if text in str(row[self.search_column_index]).lower()]
            self.display_data(filtered)

    def on_header_clicked(self, col):
        if col == self.current_sort_column:
            self.current_sort_order = Qt.DescendingOrder if self.current_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.current_sort_column = col
            self.current_sort_order = Qt.AscendingOrder
        self.all_data.sort(key=lambda x: x[col] if x[col] is not None else "", reverse=(self.current_sort_order == Qt.DescendingOrder))
        self.filter_data()