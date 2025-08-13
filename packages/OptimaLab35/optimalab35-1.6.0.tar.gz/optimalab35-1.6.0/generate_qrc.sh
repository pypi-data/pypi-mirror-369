#!/bin/bash
echo "Updating resources.qrc file and placing in ui folder..."
pyside6-rcc app_resources/resources.qrc -o OptimaLab35/ui/resources_rc.py
