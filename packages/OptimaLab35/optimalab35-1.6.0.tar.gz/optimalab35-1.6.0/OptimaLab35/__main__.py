import sys
from PySide6 import QtWidgets
from .utils.utility import Utilities
from .mainWindow import OptimaLab35
from .const import (
    CONFIG_BASE_PATH
)

def main():
    u = Utilities(CONFIG_BASE_PATH)
    app_settings = u.load_settings()
    app = QtWidgets.QApplication(sys.argv)

    try:
        import qdarktheme
        app_settings["theme"]["theme_pkg"] = True
    except ImportError:
        app_settings["theme"]["theme_pkg"] = False

    if app_settings["theme"]["use_custom_theme"] and app_settings["theme"]["theme_pkg"]:
        qdarktheme.setup_theme(app_settings["theme"]["mode"].lower())

    u.save_settings(app_settings)

    window = OptimaLab35()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
