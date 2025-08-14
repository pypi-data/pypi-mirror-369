from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QComboBox, QListWidget,
    QLineEdit, QHBoxLayout, QPushButton, QMessageBox
)
# By ChatGPT
class ExifEditor(QMainWindow):
    # Signal to emit the updated EXIF data
    exif_data_updated = Signal(dict)

    def __init__(self, exif_data):
        super().__init__()
        self.exif_data = exif_data
        self.current_key = None

        self.setWindowTitle("EXIF Editor")
        self.resize(400, 300)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # ComboBox to select lists
        self.combo_box = QComboBox()
        self.combo_box.addItems(self.exif_data.keys())
        self.combo_box.currentTextChanged.connect(self.load_list)
        main_layout.addWidget(self.combo_box)

        # List widget to display items
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # Line edit for adding items
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.add_item)
        self.line_edit.setPlaceholderText("Enter new item...")
        main_layout.addWidget(self.line_edit)

        # Buttons: Add, Delete, Cancel
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_item)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_item)
        self.cancel_button = QPushButton("Close")
        self.cancel_button.clicked.connect(self.close_editor)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # Load the first list by default
        self.load_list(self.combo_box.currentText())

    def load_list(self, key):
        """Load the selected list into the list widget."""
        self.current_key = key
        self.list_widget.clear()
        if key in self.exif_data:
            self.list_widget.addItems(self.exif_data[key])

    def add_item(self):
        """Add a new item to the selected list."""
        new_item = self.line_edit.text().strip()
        if new_item:
            self.exif_data[self.current_key].append(new_item)
            self.list_widget.addItem(new_item)
            self.line_edit.clear()
        else:
            QMessageBox.warning(self, "Warning", f"Cannot add an empty item.\nDelete {self.exif_file}...")

    def delete_item(self):
        """Delete the selected item from the list."""
        selected_item = self.list_widget.currentItem()
        if selected_item:
            item_text = selected_item.text()
            self.exif_data[self.current_key].remove(item_text)
            self.list_widget.takeItem(self.list_widget.row(selected_item))
        else:
            QMessageBox.warning(self, "Warning", "No item selected to delete.")

    def close_editor(self):
        """Emit the updated exif_data and close the editor."""
        self.exif_data_updated.emit(self.exif_data)
        self.close()
