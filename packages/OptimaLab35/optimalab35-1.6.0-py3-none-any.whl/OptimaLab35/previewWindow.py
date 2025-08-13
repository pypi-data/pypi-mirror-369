import os
from optima35.core import OptimaManager

from OptimaLab35 import __version__

from .ui import resources_rc
from .ui.preview_window import Ui_Preview_Window

from PySide6 import QtWidgets, QtCore

from PySide6.QtCore import (
    QRunnable,
    QThreadPool,
    Signal,
    QObject,
    QRegularExpression,
    Qt,
    QTimer,
    Slot
)

from PySide6.QtWidgets import (
    QMessageBox,
    QApplication,
    QMainWindow,
    QFileDialog
)

from PySide6.QtGui import QPixmap, QRegularExpressionValidator, QIcon

class PreviewWindow(QMainWindow, Ui_Preview_Window):
    values_selected = Signal(int, int, bool)
    # Large ChatGPT with rewrite and bug fixes from me.

    def __init__(self):
        super(PreviewWindow, self).__init__()
        self.ui = Ui_Preview_Window()
        self.ui.setupUi(self)
        self.o = OptimaManager()
        self.threadpool = QThreadPool()  # Thread pool for managing worker threads
        self.setWindowIcon(QIcon(":app-icon.png"))
        self.ui.QLabel.setAlignment(Qt.AlignCenter)

        # UI interactions
        self.ui.load_Button.clicked.connect(self.browse_file)
        self.ui.update_Button.clicked.connect(self.update_preview)
        self.ui.close_Button.clicked.connect(self.close_window)

        self.ui.reset_brightness_Button.clicked.connect(lambda: self.ui.brightness_spinBox.setValue(0))
        self.ui.reset_contrast_Button.clicked.connect(lambda: self.ui.contrast_spinBox.setValue(0))

        # Connect UI elements to `on_ui_change`
        self.ui.brightness_spinBox.valueChanged.connect(self.on_ui_change) # brightness slider changes spinbox value, do not need an event for the slider
        self.ui.contrast_spinBox.valueChanged.connect(self.on_ui_change) # contrast slider changes spinbox value, do not need an event for the slider
        self.ui.grayscale_checkBox.stateChanged.connect(self.on_ui_change)
        self.ui_elements(False)
        self.ui.show_OG_Button.pressed.connect(self.show_OG_image)
        self.ui.show_OG_Button.released.connect(self.update_preview)

    def on_ui_change(self):
        """Triggers update only if live update is enabled."""
        if self.ui.live_update.isChecked():
            self.update_preview()

    def browse_file(self):
        file = QFileDialog.getOpenFileName(self, caption="Select File", filter="Images (*.png *.webp *.jpg *.jpeg)")
        if file[0]:
            self.ui.image_path_lineEdit.setText(file[0])
            self.update_preview()
            self.ui_elements(True)

    def show_OG_image(self):
        """Handles loading and displaying the image in a separate thread."""
        path = self.ui.image_path_lineEdit.text()

        worker = ImageProcessorWorker(
            path = path,
            optima_manager = self.o,
            brightness = 0,
            contrast = 0,
            grayscale = False,
            resize = self.ui.scale_Slider.value(),
            callback = self.display_image  # Callback to update UI
        )
        self.threadpool.start(worker)

    def ui_elements(self, state):
        self.ui.groupBox_2.setEnabled(state)
        self.ui.groupBox.setEnabled(state)
        self.ui.groupBox_5.setEnabled(state)
        self.ui.show_OG_Button.setEnabled(state)

    def update_preview(self):
        """Handles loading and displaying the image in a separate thread."""
        path = self.ui.image_path_lineEdit.text()

        worker = ImageProcessorWorker(
            path = path,
            optima_manager = self.o,
            brightness = int(self.ui.brightness_spinBox.text()),
            contrast = int(self.ui.contrast_spinBox.text()),
            grayscale = self.ui.grayscale_checkBox.isChecked(),
            resize = self.ui.scale_Slider.value(),
            callback = self.display_image  # Callback to update UI
        )
        self.threadpool.start(worker)  # Run worker in a thread

    def display_image(self, pixmap):
        """Adjusts the image to fit within the QLabel."""
        if pixmap is None:
            QMessageBox.warning(self, "Warning", "Error processing image...")
            return

        max_size = self.ui.QLabel.size()
        scaled_pixmap = pixmap.scaled(max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.QLabel.setPixmap(scaled_pixmap)
        self.ui.QLabel.resize(scaled_pixmap.size())

    def resizeEvent(self, event):
        """Triggered when the preview window is resized."""
        file_path = self.ui.image_path_lineEdit.text()
        if os.path.exists(file_path):
            self.update_preview()  # Re-process and display the image
            super().resizeEvent(event)  # Keep the default behavior

    def close_window(self):
        """Emits signal and closes the window."""
        if self.ui.checkBox.isChecked():
            self.values_selected.emit(self.ui.brightness_spinBox.value(), self.ui.contrast_spinBox.value(), self.ui.grayscale_checkBox.isChecked())
        self.close()

class ImageProcessorWorker(QRunnable):
    """Worker class to load and process the image in a separate thread."""
    # ChatGPT
    def __init__(self, path, optima_manager, brightness, contrast, grayscale, resize, callback):
        super().__init__()
        self.path = path
        self.optima_manager = optima_manager
        self.brightness = brightness
        self.contrast = contrast
        self.grayscale = grayscale
        self.resize = resize
        self.callback = callback  # Function to call when processing is done

    @Slot()
    def run(self):
        """Runs the image processing in a separate thread."""
        if not os.path.isfile(self.path):
            self.callback(None)
            return

        try:
            img = self.optima_manager.process_image_object(
                image_input_file = self.path,
                watermark = f"PREVIEW B:{self.brightness} C:{self.contrast}",
                font_size = 1,
                resize = self.resize,
                grayscale = self.grayscale,
                brightness = self.brightness,
                contrast = self.contrast
            )
            pixmap = QPixmap.fromImage(img)
            self.callback(pixmap)
        except Exception as e:
            print(f"Error processing image: {e}")
            self.callback(None)
