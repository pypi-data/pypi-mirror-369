from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class SimpleDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set default properties
        self.setWindowTitle("Information")
        self.setGeometry(100, 100, 400, 100)  # Default size

        # Create the layout
        layout = QVBoxLayout()

        # Create the label for the message
        self.message_label = QLabel(self)
        self.message_label.setWordWrap(True)  # Enable word wrapping
        self.message_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Align text
        self.message_label.setMaximumWidth(400)  # Set max width so it wraps text
        self.message_label.setOpenExternalLinks(True)

        # Create the close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)

        # Add widgets to layout
        layout.addWidget(self.message_label)
        layout.addWidget(close_button)

        # Set layout for the dialog
        self.setLayout(layout)

    def show_dialog(self, title: str, message: str):
        self.setWindowTitle(title)  # Set the window title
        self.message_label.setText(message)  # Set the message text
        self.adjustSize()  # Adjust window height dynamically based on text content
        self.exec()  # Open the dialog as a modal window
