import sys
import os
from datetime import datetime
from PyPiUpdater import PyPiUpdater

from OptimaLab35 import __version__
from .const import (
    CONFIG_BASE_PATH
)

from .ui import resources_rc
from .utils.utility import Utilities
from .ui.settings_window import Ui_Settings_Window

from PySide6 import QtWidgets, QtCore

from PySide6.QtCore import (
    QRegularExpression,
    Qt,
    QTimer
)

from PySide6.QtWidgets import (
    QMessageBox,
    QApplication,
    QMainWindow
)

from PySide6.QtGui import QIcon

class SettingsWindow(QMainWindow, Ui_Settings_Window):
    # Mixture of code by me, code/functions refactored by ChatGPT and code directly from ChatGPT
    def __init__(self, optimalab35_localversion, optima35_localversion):
        super(SettingsWindow, self).__init__()
        self.ui = Ui_Settings_Window()
        self.ui.setupUi(self)
        self.u = Utilities(os.path.expanduser(CONFIG_BASE_PATH))
        self.app_settings = self.u.load_settings()
        self.dev_mode = True if optimalab35_localversion == "0.0.1" else False
        self.setWindowIcon(QIcon(":app-icon.png"))

        # Update log file location
        self.update_log_file = os.path.expanduser(f"{CONFIG_BASE_PATH}/update_log.json")
        # Store local versions
        self.optimalab35_localversion = optimalab35_localversion
        self.optima35_localversion = optima35_localversion
        # Create PyPiUpdater instances
        self.ppu_ol35 = PyPiUpdater("OptimaLab35", self.optimalab35_localversion, self.update_log_file)
        self.ppu_o35 = PyPiUpdater("optima35", self.optima35_localversion, self.update_log_file)
        self.ol35_last_state = self.ppu_ol35.get_last_state()
        self.o35_last_state = self.ppu_o35.get_last_state()
        # Track which packages need an update
        self.updates_available = {"OptimaLab35": False, "optima35": False}
        self.define_gui_interaction()

    def define_gui_interaction(self):
        """Setup UI interactions."""
        # Updater related
        self.ui.label_optimalab35_localversion.setText(self.optimalab35_localversion)
        self.ui.label_optima35_localversion.setText(self.optima35_localversion)

        self.ui.label_latest_version.setText("Latest version")
        self.ui.label_optimalab35_latestversion.setText("...")
        self.ui.label_optima35_latestversion.setText("...")

        self.ui.update_and_restart_Button.setEnabled(False)

        # Connect buttons to functions
        self.ui.check_for_update_Button.clicked.connect(self.check_for_updates)
        self.ui.update_and_restart_Button.clicked.connect(self.update_and_restart)
        self.ui.label_last_check.setText(f"Last check: {self.time_to_string(self.ol35_last_state[0])}")
        self.ui.dev_widget.setVisible(False)

        # Timer for long press detection
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.toggle_dev_ui)

        # Connect button press/release
        self.ui.check_for_update_Button.pressed.connect(self.start_long_press)
        self.ui.check_for_update_Button.released.connect(self.cancel_long_press)
        self.ui.label_5.setText('<li><a href="https://code.boxyfoxy.net/CodeByMrFinchum/OptimaLab35/src/branch/main/CHANGELOG.md">Changelog</a></li>')
        self.ui.label_5.setOpenExternalLinks(True)
        #settings related
        self.load_settings_into_ui()
        self.ui.reset_exif_Button.clicked.connect(self.ask_reset_exif)
        self.ui.save_and_close_Button.clicked.connect(self.save_and_close)
        self.ui.save_and_restart_Button.clicked.connect(self.save_and_restart)

        if os.name == "nt": # Disable restart app when windows.
            self.ui.save_and_restart_Button.setVisible(False)
            self.ui.restart_checkBox.setChecked(False)
            self.ui.restart_checkBox.setVisible(False)

# setting related
    def load_settings_into_ui(self):
        """Loads the settings into the UI elements."""
        settings = self.app_settings
        theme_mode = settings["theme"]["mode"]
        use_custom_theme = settings["theme"]["use_custom_theme"]
        pkg_available = settings["theme"]["theme_pkg"]

        if pkg_available:
            index = self.ui.theme_selection_comboBox.findText(theme_mode, QtCore.Qt.MatchFlag.MatchExactly)
            if index != -1:
                self.ui.theme_selection_comboBox.setCurrentIndex(index)
            self.ui.enable_theme_checkBox.setChecked(use_custom_theme)
            self.ui.install_pkg_Button.setVisible(False)
            self.ui.enable_theme_checkBox.setEnabled(True)
        else:
            self.ui.enable_theme_checkBox.setEnabled(False)
            self.ui.install_pkg_Button.clicked.connect(self.install_theme_pkg)

    def install_theme_pkg(self):
        a = self.ppu_ol35.install_package("PyQtDarkTheme-fork")
        self.ui.install_pkg_Button.setEnabled(False)
        self.ui.install_pkg_Button.setText("Please wait...")

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Message")
        msg_box.setText(a[1])
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        if a[0]:
            self.app_settings["theme"]["theme_pkg"] = True
            self.load_settings_into_ui()
        else:
            self.ui.install_pkg_Button.setEnabled(True)
            self.ui.install_pkg_Button.setText("Try again?")

    def save_settings(self):
        self.app_settings["theme"]["mode"] = self.ui.theme_selection_comboBox.currentText()
        self.app_settings["theme"]["use_custom_theme"] = self.ui.enable_theme_checkBox.isChecked()
        self.u.save_settings(self.app_settings)

    def save_and_close(self):
        self.save_settings()
        self.close()

    def save_and_restart(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Reset")
        msg.setText("Are you sure you want to restart the app?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        # Show the message box and wait for the user's response
        response = msg.exec()

        # Check response and perform action
        if response == QMessageBox.StandardButton.Yes:
            self.save_settings()
            self.restart_program()
        else:
            pass  # Do nothing if "No" is selected

    def ask_reset_exif(self):
        """Shows a dialog to ask the user if they are sure about resetting EXIF options to default."""
        # Create a QMessageBox with a Yes/No question
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Reset")
        msg.setText("Are you sure you want to reset the EXIF options to default?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        # Show the message box and wait for the user's response
        response = msg.exec()

        # Check response and perform action
        if response == QMessageBox.StandardButton.Yes:
            self.u.default_exif()  # Reset EXIF options to default
        else:
            pass  # Do nothing if "No" is selected

# update related parts
    def start_long_press(self):
        """Start the timer when button is pressed."""
        # brave AI
        self.timer.start(1000)  # 1-second long press

    def cancel_long_press(self):
        """Cancel long press if released early."""
        # brave AI
        self.timer.stop()

    def toggle_dev_ui(self):
        """Show or hide the hidden UI when long press is detected."""
        self.ui.dev_widget.setVisible(True)

        self.ui.check_local_Button.clicked.connect(self.local_check_for_updates)
        self.ui.update_local_Button.clicked.connect(self.local_update)

    def local_check_for_updates(self):
        dist_folder = os.path.expanduser("~/.config/OptimaLab35/dist/")
        self.ui.label_optimalab35_latestversion.setText("Checking...")
        self.ui.label_optima35_latestversion.setText("Checking...")

        # Check OptimaLab35 update
        ol35_pkg_info = self.ppu_ol35.check_update_local(dist_folder)
        if ol35_pkg_info[0] is None:
            self.ui.label_optimalab35_latestversion.setText(ol35_pkg_info[1][0:13])
        else:
            self.ui.label_optimalab35_latestversion.setText(ol35_pkg_info[1])
            self.updates_available["OptimaLab35"] = ol35_pkg_info[0]

        # Check optima35 update
        o35_pkg_info = self.ppu_o35.check_update_local(dist_folder)
        if o35_pkg_info[0] is None:
            self.ui.label_optima35_latestversion.setText(o35_pkg_info[1][0:13])
        else:
            self.ui.label_optima35_latestversion.setText(o35_pkg_info[1])
            self.updates_available["optima35"] = o35_pkg_info[0]

    def local_update(self):
        dist_folder = os.path.expanduser("~/.config/OptimaLab35/dist/")
        packages_to_update = [pkg for pkg, update in self.updates_available.items() if update]

        if not packages_to_update:
            QMessageBox.information(self, "Update", "No updates available.")
            return

        # Confirm update
        msg = QMessageBox()
        msg.setWindowTitle("Update Available")
        message = f"Updating: {', '.join(packages_to_update)}\nUpdate "

        if self.ui.restart_checkBox.isChecked():
            message = message + "and restart app?"
        else:
            message = message + "app?"

        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec()

        if result == QMessageBox.Yes:
            update_results = []  # Store results

            for package in packages_to_update:
                if package == "OptimaLab35":
                    pkg_info = self.ppu_ol35.update_from_local(dist_folder)
                elif package == "optima35":
                    pkg_info = self.ppu_o35.update_from_local(dist_folder)

                update_results.append(f"{package}: {'Success' if pkg_info[0] else 'Failed'}\n{pkg_info[1]}")

            # Show summary of updates
            # Show update completion message
            msg = QMessageBox()
            msg.setWindowTitle("Update Complete")
            msg.setText("\n\n".join(update_results))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

            # Restart the application after user clicks "OK"
            if self.ui.restart_checkBox.isChecked():
                self.restart_program()

    def time_to_string(self, time_time):
        try:
            dt_obj = datetime.fromtimestamp(time_time)
            date_string = dt_obj.strftime("%d %h %H:%M")
            return date_string
        except TypeError:
            return "Missing information"

    def check_for_updates(self):
        """Check for updates and update the UI."""
        self.ui.check_for_update_Button.setEnabled(False)
        self.ui.label_optimalab35_latestversion.setText("Checking...")
        self.ui.label_optima35_latestversion.setText("Checking...")

        # Check OptimaLab35 update
        ol35_pkg_info = self.ppu_ol35.check_for_update()
        if ol35_pkg_info[0] is None:
            self.ui.label_optimalab35_latestversion.setText(ol35_pkg_info[1][0:13])
        else:
            self.ui.label_optimalab35_latestversion.setText(ol35_pkg_info[1])
            self.updates_available["OptimaLab35"] = ol35_pkg_info[0]

        # Check optima35 update
        o35_pkg_info = self.ppu_o35.check_for_update()
        if o35_pkg_info[0] is None:
            self.ui.label_optima35_latestversion.setText(o35_pkg_info[1][0:13])
        else:
            self.ui.label_optima35_latestversion.setText(o35_pkg_info[1])
            self.updates_available["optima35"] = o35_pkg_info[0]

        # Enable update button if any update is available
        if any(self.updates_available.values()):
            if self.dev_mode:
                self.ui.update_and_restart_Button.setEnabled(False)
                self.ui.update_and_restart_Button.setText("Update disabled")
            else:
                self.ui.update_and_restart_Button.setEnabled(True)

        last_date = self.time_to_string(self.ppu_ol35.get_last_state()[0])
        self.ui.label_last_check.setText(f"Last check: {last_date}")
        self.ui.label_latest_version.setText("Online version")
        self.ui.check_for_update_Button.setEnabled(True)

    def update_and_restart(self):
        """Update selected packages and restart the application."""
        packages_to_update = [pkg for pkg, update in self.updates_available.items() if update]

        if not packages_to_update:
            QMessageBox.information(self, "Update", "No updates available.")
            return

        # Confirm update
        msg = QMessageBox()
        msg.setWindowTitle("Update Available")
        message = f"Updating: {', '.join(packages_to_update)}\nUpdate "

        if self.ui.restart_checkBox.isChecked():
            message = message + "and restart app?"
        else:
            message = message + "app?"

        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec()

        if result == QMessageBox.Yes:
            update_results = []  # Store results

            for package in packages_to_update:
                if package == "OptimaLab35":
                    pkg_info = self.ppu_ol35.update_package()
                elif package == "optima35":
                    pkg_info = self.ppu_o35.update_package()

                update_results.append(f"{package}: {'Success' if pkg_info[0] else 'Failed'}\n{pkg_info[1]}")

            # Show summary of updates
            # Show update completion message
            msg = QMessageBox()
            msg.setWindowTitle("Update Complete")
            msg.setText("\n\n".join(update_results))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

            # Restart the application after user clicks "OK"
            if self.ui.restart_checkBox.isChecked():
                self.restart_program()

    def restart_program(self):
        """Restart the Python program after an update."""
        print("Restarting the application...")
        # Close all running Qt windows before restarting
        app = QApplication.instance()
        if app:
            app.quit()

        python = sys.executable
        os.execl(python, python, *sys.argv)
