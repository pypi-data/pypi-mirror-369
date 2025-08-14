import os
from datetime import datetime
from optima35.core import OptimaManager

from OptimaLab35 import __version__
from .const import (
    APPLICATION_NAME,
    CONFIG_BASE_PATH
)

from .ui import resources_rc
from .previewWindow import PreviewWindow
from .settingsWindow import SettingsWindow

from .utils.utility import Utilities
from .ui.main_window import Ui_MainWindow
from .ui.exif_handler_window import ExifEditor
from .ui.simple_dialog import SimpleDialog  # Import the SimpleDialog class

from PySide6 import QtWidgets, QtCore

from PySide6.QtCore import (
    QRunnable,
    QThreadPool,
    Signal,
    QObject,
    QRegularExpression,
    Qt,
    QDate
)

from PySide6.QtWidgets import (
    QMessageBox,
    QApplication,
    QMainWindow,
    QFileDialog
)

from PySide6.QtGui import QRegularExpressionValidator, QIcon

class OptimaLab35(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(OptimaLab35, self).__init__()
        self.name = APPLICATION_NAME
        self.version = __version__
        self.o = OptimaManager()
        self.u = Utilities(os.path.expanduser(CONFIG_BASE_PATH))
        self.app_settings = self.u.load_settings()
        self.thread_pool = QThreadPool() # multi thread ChatGPT
        # Initiate internal object
        self.exif_file = os.path.expanduser(f"{CONFIG_BASE_PATH}/exif.yaml")
        self.available_exif_data = None
        self.settings = {}
        # UI elements
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.sd = SimpleDialog()

        # Change UI elements
        self.change_statusbar(f"{self.name} v{self.version}", 10000)
        self.set_title()
        self.default_ui_layout()
        self.define_gui_interaction()
        self.setWindowIcon(QIcon(":app-icon.png"))

    # Init function
    def default_ui_layout(self):
        self.ui.png_quality_spinBox.setVisible(False)
        self.ui.png_quality_Slider.setVisible(False)
        self.ui.quality_label_2.setVisible(False)

    def set_title(self):
        if self.version == "0.0.1":
            title = f"{self.name} DEV MODE"
        else:
            title = self.name
        self.setWindowTitle(title)

    def define_gui_interaction(self):
        self.ui.input_folder_button.clicked.connect(self.browse_input_folder)
        self.ui.output_folder_button.clicked.connect(self.browse_output_folder)
        self.ui.start_button.clicked.connect(self.start_process)
        self.ui.insert_exif_Button.clicked.connect(self.startinsert_exif)
        self.ui.image_type.currentIndexChanged.connect(self.update_quality_options)

        self.ui.exif_checkbox.stateChanged.connect(
            lambda state: self.handle_checkbox_state(state, 2, self.populate_exif)
        )
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.ui.edit_exif_button.clicked.connect(self.open_exif_editor)

        self.ui.actionAbout.triggered.connect(self.info_window)
        self.ui.preview_Button.clicked.connect(self.open_preview_window)
        self.ui.actionSettings.triggered.connect(self.open_updater_window)

        regex = QRegularExpression(r"^\d{1,2}\.\d{1,6}$")
        validator = QRegularExpressionValidator(regex)
        self.ui.lat_lineEdit.setValidator(validator)
        self.ui.long_lineEdit.setValidator(validator)
        self.ui.dateEdit.setDate(QDate.currentDate())
    # UI related function, changing parts, open, etc.
    def open_preview_window(self):
        self.preview_window = PreviewWindow()
        self.preview_window.values_selected.connect(self.update_values)
        self.preview_window.showMaximized()

    def open_updater_window(self):
        self.updater_window = SettingsWindow(self.version, self.o.version)
        self.updater_window.show()

    def update_values(self, value1, value2, checkbox_state):
        # Update main window's widgets with the received values
        # ChatGPT
        self.ui.brightness_spinBox.setValue(value1)
        self.ui.contrast_spinBox.setValue(value2)
        self.ui.grayscale_checkBox.setChecked(checkbox_state)

    def info_window(self):
        info_text = f"""
        <h3>{self.name} v{self.version}</h3>
        <p>(C) 2024-2025 Mr Finchum aka CodeByMrFinchum</p>
        <p>{self.name} is a GUI for {self.o.name} (v{self.o.version}), enhancing its functionality with a user-friendly interface for efficient image and metadata management.</p>

        <h4>Features:</h4>
        <ul>
            <li>Image processing: resize, grayscale, brightness/contrast adjustments</li>
            <li>Live image preview: see changes before applying</li>
            <li>EXIF management: add, copy, remove metadata, GPS support</li>
            <li>Watermarking: add custom text-based watermarks</li>
        </ul>

        <p>For more details, visit:</p>
        <ul>
            <li><a href="https://code.boxyfoxy.net/CodeByMrFinchum/OptimaLab35/src/branch/main/CHANGELOG.md">Changelog</a></li>
            <li><a href="https://gitlab.com/CodeByMrFinchum/OptimaLab35">OptimaLab35 GitLab</a></li>
            <li><a href="https://gitlab.com/CodeByMrFinchum/optima35">optima35 GitLab</a></li>
        </ul>
        """

        self.sd.show_dialog(f"{self.name} v{self.version}", info_text)

    def handle_qprogressbar(self, value):
        self.ui.progressBar.setValue(value)

    def toggle_buttons(self, state):
        self.ui.start_button.setEnabled(state)
        if self.ui.exif_checkbox.isChecked():
            self.ui.insert_exif_Button.setEnabled(state)

    def handle_checkbox_state(self, state, desired_state, action):
        """Perform an action based on the checkbox state and a desired state. Have to use lambda when calling."""
        if state == desired_state:
            action()

    def on_tab_changed(self, index):
        """Handle tab changes."""
        # chatgpt
        if index == 1:  # EXIF Tab
            self.handle_exif_file("read")
        elif index == 0:  # Main Tab
            self.handle_exif_file("write")

    def parse_time(self, s):
        # Modified ChatGPT code
        """Return total seconds if valid mm:ss, otherwise None."""
        try:
            mm, ss = s.split(":")
            return int(mm) * 60 + int(ss)
        except (ValueError, AttributeError):
            return None

    def sort_times(self, times):
        # Keep only mm:ss or NA
        # Modified ChatGPT code
        filtered = []
        for t in times:
            if t is None:
                filtered.append(None)
            elif isinstance(t, str):
                stripped = t.strip()
                if stripped.upper() in {"NA"}:
                    filtered.append(stripped)
                elif self.parse_time(stripped) is not None:
                    filtered.append(stripped)
            # ignore anything else
        # Sort: NA first, then valid times ascending
        return sorted(filtered, key=lambda x: (0, 0) if (x is None or str(x).strip().upper() in {"NA"})
                    else (1, self.parse_time(x)))

    def sort_dict_of_lists(self, input_dict):
        # Partily ChatGPT
        sorted_dict = {}
        for key, lst in input_dict.items():
            # Sort alphabetically for strings, numerically for numbers
            if key == "iso":
                lst = [int(x) for x in lst]
                lst = sorted(lst)
                lst = [str(x) for x in lst]
                sorted_dict["iso"] = lst
            elif key == "time":
                lst = self.sort_times(lst)
                sorted_dict["time"] = lst
            elif all(isinstance(x, str) for x in lst):
                sorted_dict[key] = sorted(
                    lst,
                    key=lambda x: (0, x.lower()) if str(x).lower() == "na" else (1, str(x).lower())
                )

        return sorted_dict

    def populate_comboboxes(self, combo_mapping):
        """Populate comboboxes with EXIF data."""
        # ChatGPT
        for field, comboBox in combo_mapping.items():
            comboBox.clear()  # Clear existing items
            comboBox.addItems(map(str, self.available_exif_data.get(field, [])))

    def open_exif_editor(self):
        """Open the EXIF Editor."""
        self.exif_editor = ExifEditor(self.available_exif_data)
        self.exif_editor.exif_data_updated.connect(self.update_exif_data)
        self.exif_editor.show()

    def update_exif_data(self, updated_exif_data):
        """Update the EXIF data."""
        self.exif_data = updated_exif_data
        self.populate_exif()

    def populate_exif(self):
        # partly chatGPT
        # Mapping of EXIF fields to comboboxes in the UI
        combo_mapping = {
            "make": self.ui.make_comboBox,
            "model": self.ui.model_comboBox,
            "lens": self.ui.lens_comboBox,
            "iso": self.ui.iso_comboBox,
            "image_description": self.ui.image_description_comboBox,
            "user_comment": self.ui.user_comment_comboBox,
            "artist": self.ui.artist_comboBox,
            "copyright_info": self.ui.copyright_info_comboBox,
            "developer": self.ui.dev_comboBox,
            "time": self.ui.time_comboBox,
        }

        self.populate_comboboxes(combo_mapping)

    def update_quality_options(self):
            """Update visibility of quality settings based on selected format."""
            # Partly ChatGPT
            selected_format = self.ui.image_type.currentText()
            # Hide all quality settings
            self.ui.png_quality_spinBox.setVisible(False)
            self.ui.jpg_quality_spinBox.setVisible(False)
            self.ui.jpg_quality_Slider.setVisible(False)
            self.ui.png_quality_Slider.setVisible(False)
            self.ui.quality_label_1.setVisible(False)
            self.ui.quality_label_2.setVisible(False)
            # Show relevant settings
            if selected_format == "jpg":
                self.ui.jpg_quality_spinBox.setVisible(True)
                self.ui.jpg_quality_Slider.setVisible(True)
                self.ui.quality_label_1.setVisible(True)
            elif selected_format == "webp":
                self.ui.jpg_quality_spinBox.setVisible(True)
                self.ui.jpg_quality_Slider.setVisible(True)
                self.ui.quality_label_1.setVisible(True)
            elif selected_format == "png":
                self.ui.png_quality_spinBox.setVisible(True)
                self.ui.png_quality_Slider.setVisible(True)
                self.ui.quality_label_2.setVisible(True)

    def browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.ui.input_path.setText(folder)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.ui.output_path.setText(folder)

    def change_statusbar(self, msg, timeout = 500):
        self.ui.statusBar.showMessage(msg, timeout)

    # Core functions
    def on_processing_finished(self):
        self.toggle_buttons(True)
        self.handle_qprogressbar(0)
        QMessageBox.information(self, "Information", "Finished!")

    def image_list_from_folder(self, path):
        image_files = [
            f for f in os.listdir(path) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]
        image_files.sort()
        return image_files

    def control_before_start(self, process):
        input_folder = self.settings["input_folder"]
        output_folder = self.settings["output_folder"]
        image_list = self.image_list_from_folder(input_folder)
        input_folder_valid = os.path.exists(input_folder)

        if isinstance(output_folder, str):
            output_folder_valid = os.path.exists(output_folder)

        if process == "image":
            if not input_folder or not output_folder:
                QMessageBox.warning(self, "Warning", "Input or output folder not selected")
                return False

            if not input_folder_valid or not output_folder_valid:
                QMessageBox.warning(self, "Warning", f"Input location {input_folder_valid}\nOutput folder {output_folder_valid}...")
                return False

            if len(self.image_list_from_folder(output_folder)) != 0:
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    "Output folder containes images, which might get overritten, continue?",
                    QMessageBox.Yes | QMessageBox.No,
                )

                if reply == QMessageBox.No:
                    return False

        elif process == "exif":

            if not input_folder:
                QMessageBox.warning(self, "Warning", "Input not selected")
                return False

            if output_folder:
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    "Output folder selected, but insert exif is done to images in input folder, Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                )

                if reply == QMessageBox.No:
                    return False

            if not input_folder_valid :
                QMessageBox.warning(self, "Warning", f"Input location {input_folder_valid}")
                return False

        else:
            print("Something went wrong")

        if len(image_list) == 0:
            QMessageBox.warning(self, "Warning", "Selected folder has no supported files.")
            return False

        return True

    def start_process(self):
        self.toggle_buttons(False)
        u = self.update_settings()
        if u != None:  # Get all user selected data
            QMessageBox.warning(self, "Warning", f"Error: {u}")
            self.toggle_buttons(True)
            return

        if self.control_before_start("image") == False:
            self.toggle_buttons(True)
            return

        image_list = self.image_list_from_folder(self.settings["input_folder"])
        # Create a worker ChatGPT
        worker = ImageProcessorRunnable(image_list, self.settings, self.handle_qprogressbar)
        worker.signals.finished.connect(self.on_processing_finished)
        # Start worker in thread pool ChatGPT
        self.thread_pool.start(worker)

    def control_ending(self, name_lst):
        for item in name_lst:
            try:
                int(item[-5])
            except ValueError:
                return False
        return True

    def insert_exif(self, image_files):
        input_folder = self.settings["input_folder"]

        i = 1
        for image_file in image_files:

            input_path = os.path.join(input_folder, image_file)

            self.o.insert_exif_to_image(
                exif_dict = self.settings["user_selected_exif"],
                image_path = input_path,
                gps = self.settings["gps"])
            self.change_statusbar(image_file, 100)
            self.handle_qprogressbar(int((i / len(image_files)) * 100))
            i += 1

        self.ui.progressBar.setValue(0)

    def startinsert_exif(self):
        self.toggle_buttons(False)
        u = self.update_settings()
        if u != None:  # Get all user selected data
            QMessageBox.warning(self, "Warning", f"Error: {u}")
            self.toggle_buttons(True)
            return

        if self.control_before_start("exif") == False:
            self.toggle_buttons(True)
            return

        image_list = self.image_list_from_folder(self.settings["input_folder"])
        print(image_list)
        if not self.control_ending(image_list):
            QMessageBox.warning(self, "Warning", f"Error: one or more filenames do not end on a number.\nCan not adjust time")
            self.toggle_buttons(True)
            return

        self.insert_exif(image_list)

        self.toggle_buttons(True)
        QMessageBox.information(self, "Information", "Finished")

    def get_checkbox_value(self, checkbox, default = None):
        """Helper function to get the value of a checkbox or a default value."""
        return checkbox.isChecked() if checkbox else default

    def get_spinbox_value(self, spinbox, default = None):
        """Helper function to get the value of a spinbox and handle empty input."""
        return int(spinbox.text()) if spinbox.text() else default

    def get_combobox_value(self, combobox, default = None):
        """Helper function to get the value of a combobox."""
        return combobox.currentIndex() + 1 if combobox.currentIndex() != -1 else default

    def get_text_value(self, lineedit, default = None):
        """Helper function to get the value of a text input field."""
        return lineedit.text() if lineedit.text() else default

    def get_date(self):
        date_input = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        new_date = datetime.strptime(date_input, "%Y-%m-%d")
        return new_date.strftime("%Y:%m:%d 00:00:00")

    def add_laboratory_info(self):
        lab_info_str = ""
        dev_text = self.ui.dev_comboBox.currentText()
        time_text = self.ui.time_comboBox.currentText()
        if dev_text != "NA":
            lab_info_str += f", {dev_text}"

            if time_text != "NA":
                lab_info_str += f", {time_text}"

        return lab_info_str

    def collect_selected_exif(self):
        user_data = {}
        user_data["make"] = self.ui.make_comboBox.currentText()
        user_data["model"] = self.ui.model_comboBox.currentText()
        user_data["lens"] = self.ui.lens_comboBox.currentText()
        user_data["iso"] = self.ui.iso_comboBox.currentText()
        lab_info = self.add_laboratory_info()
        user_data["image_description"] = f"{self.ui.image_description_comboBox.currentText()} {lab_info}"
        user_data["artist"] = self.ui.artist_comboBox.currentText()
        user_data["copyright_info"] = self.ui.copyright_info_comboBox.currentText()
        user_data["software"] = f"{self.name} {self.version} with {self.o.name} {self.o.version}"
        if int(self.ui.contrast_spinBox.text()) != 0 or int(self.ui.brightness_spinBox.text()) != 0:
            user_data["user_comment"] = f"{self.ui.user_comment_comboBox.currentText()}, contrast: {self.ui.contrast_spinBox.text()}, brightness: {self.ui.brightness_spinBox.text()}"
        else:
            user_data["user_comment"] = self.ui.user_comment_comboBox.currentText()

        return user_data

    def get_selected_exif(self):
        """Collect selected EXIF data and handle date and GPS if necessary."""
        selected_exif = self.collect_selected_exif() if self.ui.exif_checkbox.isChecked() else None
        if selected_exif:
            if self.ui.add_date_checkBox.isChecked():
                selected_exif["date_time_original"] = self.get_date()
        if self.ui.gps_checkBox.isChecked():
            try:
                self.settings["gps"] = [float(self.ui.lat_lineEdit.text()), float(self.ui.long_lineEdit.text())]
            except ValueError as e:
                self.settings["gps"] = "Wrong gps data"
        else:
            self.settings["gps"] = None
        return selected_exif

    def check_selected_exif(self, exif):
        for key in exif:
            if len(exif[key]) == 0:
                return f"{key} is empty"
        return True

    def update_settings(self):
        """Update .settings from all GUI elements."""
        # Basic
        self.settings["input_folder"] = self.get_text_value(self.ui.input_path)
        self.settings["output_folder"] = self.get_text_value(self.ui.output_path)
        self.settings["file_format"] = self.ui.image_type.currentText()
        # Quality
        self.settings["jpg_quality"] = self.get_spinbox_value(self.ui.jpg_quality_spinBox)
        self.settings["png_compression"] = self.get_spinbox_value(self.ui.png_quality_spinBox)
        self.settings["resize"] = int(self.ui.resize_spinBox.text()) if self.ui.resize_spinBox.text() != "100" else None
        self.settings["optimize"] = self.get_checkbox_value(self.ui.optimize_checkBox)
        # Changes for image
        self.settings["brightness"] = int(self.ui.brightness_spinBox.text()) if self.ui.brightness_spinBox.text() != "0" else None
        self.settings["contrast"] = int(self.ui.contrast_spinBox.text()) if self.ui.contrast_spinBox.text() != "0" else None
        self.settings["grayscale"] = self.get_checkbox_value(self.ui.grayscale_checkBox)
        # Watermark
        self.settings["font_size"] = self.get_combobox_value(self.ui.font_size_comboBox)
        self.settings["watermark"] = self.get_text_value(self.ui.watermark_lineEdit)
        # Naming
        new_name = self.get_text_value(self.ui.filename, False) if self.ui.rename_checkbox.isChecked() else False
        if isinstance(new_name, str): new_name = new_name.replace(" ", "_")
        self.settings["new_file_names"] = new_name
        self.settings["invert_image_order"] = self.get_checkbox_value(self.ui.revert_checkbox) if new_name is not False else None
        # Handle EXIF data selection
        self.settings["copy_exif"] = self.get_checkbox_value(self.ui.exif_copy_checkBox)
        self.settings["own_exif"] = self.get_checkbox_value(self.ui.exif_checkbox)
        self.settings["own_date"] = self.get_checkbox_value(self.ui.add_date_checkBox)
        if self.settings["own_exif"]:
            self.settings["user_selected_exif"] = self.get_selected_exif()
            if self.settings["gps"] is not None:
                if len(self.settings["gps"]) != 2:
                    return self.settings["gps"]
        else:
            self.settings["user_selected_exif"] = None
            self.settings["gps"] = None

        if self.settings["user_selected_exif"] is not None:
            u = self.check_selected_exif(self.settings["user_selected_exif"])
            if u != True:
                return u

    # Helper functions, low level
    def handle_exif_file(self, do):
        # TODO: add check if data is missing.
        if do == "read":
            file_dict = self.u.read_yaml(self.exif_file)
            self.available_exif_data = self.sort_dict_of_lists(file_dict)
        elif do == "write":
            self.u.write_yaml(self.exif_file, self.available_exif_data)

    def closeEvent(self, event):
        QApplication.closeAllWindows()
        event.accept()

class WorkerSignals(QObject):
    # ChatGPT
    progress = Signal(int)
    finished = Signal()

class ImageProcessorRunnable(QRunnable):
    # ChatGPT gave rough function layout
    def __init__(self, image_files, settings, progress_callback):
        super().__init__()
        self.image_files = image_files
        self.settings = settings
        self.signals = WorkerSignals()
        self.signals.progress.connect(progress_callback)
        self.o = OptimaManager()
        self.u = Utilities(os.path.expanduser(CONFIG_BASE_PATH))

    def run(self):
        input_folder = self.settings["input_folder"]
        output_folder = self.settings["output_folder"]

        for i, image_file in enumerate(self.image_files, start=1):
            input_path = os.path.join(input_folder, image_file)
            if self.settings["new_file_names"] != False:
                image_name = self.u.append_number_to_name(self.settings["new_file_names"], i, len(self.image_files), self.settings["invert_image_order"])
            else:
                image_name = os.path.splitext(image_file)[0]
            output_path = os.path.join(output_folder, image_name)

            self.o.process_and_save_image(
                image_input_file = input_path,
                image_output_file = output_path,
                file_type = self.settings["file_format"],
                quality = self.settings["jpg_quality"],
                compressing = self.settings["png_compression"],
                optimize = self.settings["optimize"],
                resize = self.settings["resize"],
                watermark = self.settings["watermark"],
                font_size = self.settings["font_size"],
                grayscale = self.settings["grayscale"],
                brightness = self.settings["brightness"],
                contrast = self.settings["contrast"],
                dict_for_exif = self.settings["user_selected_exif"],
                gps = self.settings["gps"],
                copy_exif = self.settings["copy_exif"]
            )
            self.signals.progress.emit(int((i / len(self.image_files)) * 100))

        self.signals.finished.emit()
