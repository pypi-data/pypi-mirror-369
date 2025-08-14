#!/bin/bash
echo "Update .ui files with pyside"
echo "Update main window."
pyside6-uic OptimaLab35/ui/main_window.ui -o OptimaLab35/ui/main_window.py
echo "Update preview window."
pyside6-uic OptimaLab35/ui/preview_window.ui -o OptimaLab35/ui/preview_window.py
echo "Update settings window."
pyside6-uic OptimaLab35/ui/settings_window.ui -o OptimaLab35/ui/settings_window.py
