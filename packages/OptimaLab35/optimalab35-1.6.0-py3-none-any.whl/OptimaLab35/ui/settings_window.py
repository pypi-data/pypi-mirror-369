# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_Settings_Window(object):
    def setupUi(self, Settings_Window):
        if not Settings_Window.objectName():
            Settings_Window.setObjectName(u"Settings_Window")
        Settings_Window.setEnabled(True)
        Settings_Window.resize(400, 325)
        Settings_Window.setMinimumSize(QSize(400, 300))
        Settings_Window.setMaximumSize(QSize(450, 350))
        self.centralwidget = QWidget(Settings_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMaximumSize(QSize(500, 500))
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMaximumSize(QSize(500, 500))
        self.tabWidgetPage2 = QWidget()
        self.tabWidgetPage2.setObjectName(u"tabWidgetPage2")
        self.gridLayout_2 = QGridLayout(self.tabWidgetPage2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pkg_info_groupBox = QGroupBox(self.tabWidgetPage2)
        self.pkg_info_groupBox.setObjectName(u"pkg_info_groupBox")
        self.gridLayout = QGridLayout(self.pkg_info_groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_optima35_latestversion = QLabel(self.pkg_info_groupBox)
        self.label_optima35_latestversion.setObjectName(u"label_optima35_latestversion")
        self.label_optima35_latestversion.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_optima35_latestversion, 2, 2, 1, 1)

        self.label_latest_version = QLabel(self.pkg_info_groupBox)
        self.label_latest_version.setObjectName(u"label_latest_version")
        self.label_latest_version.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_latest_version, 0, 2, 1, 1)

        self.label = QLabel(self.pkg_info_groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.label_optimalab35_latestversion = QLabel(self.pkg_info_groupBox)
        self.label_optimalab35_latestversion.setObjectName(u"label_optimalab35_latestversion")
        self.label_optimalab35_latestversion.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_optimalab35_latestversion, 1, 2, 1, 1)

        self.label_9 = QLabel(self.pkg_info_groupBox)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 1)

        self.label_optimalab35_localversion = QLabel(self.pkg_info_groupBox)
        self.label_optimalab35_localversion.setObjectName(u"label_optimalab35_localversion")
        self.label_optimalab35_localversion.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_optimalab35_localversion, 1, 1, 1, 1)

        self.label_6 = QLabel(self.pkg_info_groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_6, 0, 1, 1, 1)

        self.label_2 = QLabel(self.pkg_info_groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.label_optima35_localversion = QLabel(self.pkg_info_groupBox)
        self.label_optima35_localversion.setObjectName(u"label_optima35_localversion")
        self.label_optima35_localversion.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_optima35_localversion, 2, 1, 1, 1)


        self.gridLayout_2.addWidget(self.pkg_info_groupBox, 0, 0, 1, 2)

        self.dev_widget = QWidget(self.tabWidgetPage2)
        self.dev_widget.setObjectName(u"dev_widget")
        self.horizontalLayout_2 = QHBoxLayout(self.dev_widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.check_local_Button = QPushButton(self.dev_widget)
        self.check_local_Button.setObjectName(u"check_local_Button")

        self.horizontalLayout_2.addWidget(self.check_local_Button)

        self.update_local_Button = QPushButton(self.dev_widget)
        self.update_local_Button.setObjectName(u"update_local_Button")

        self.horizontalLayout_2.addWidget(self.update_local_Button)


        self.gridLayout_2.addWidget(self.dev_widget, 1, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.label_5 = QLabel(self.tabWidgetPage2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 3, 0, 1, 1)

        self.label_last_check = QLabel(self.tabWidgetPage2)
        self.label_last_check.setObjectName(u"label_last_check")
        self.label_last_check.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_last_check, 3, 1, 2, 1)

        self.widget = QWidget(self.tabWidgetPage2)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.check_for_update_Button = QPushButton(self.widget)
        self.check_for_update_Button.setObjectName(u"check_for_update_Button")

        self.horizontalLayout.addWidget(self.check_for_update_Button)

        self.update_and_restart_Button = QPushButton(self.widget)
        self.update_and_restart_Button.setObjectName(u"update_and_restart_Button")

        self.horizontalLayout.addWidget(self.update_and_restart_Button)

        self.restart_checkBox = QCheckBox(self.widget)
        self.restart_checkBox.setObjectName(u"restart_checkBox")
        self.restart_checkBox.setChecked(True)

        self.horizontalLayout.addWidget(self.restart_checkBox)


        self.gridLayout_2.addWidget(self.widget, 5, 0, 1, 2)

        self.tabWidget.addTab(self.tabWidgetPage2, "")
        self.tabWidgetPage1 = QWidget()
        self.tabWidgetPage1.setObjectName(u"tabWidgetPage1")
        self.verticalLayout_2 = QVBoxLayout(self.tabWidgetPage1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_4 = QGroupBox(self.tabWidgetPage1)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_4 = QLabel(self.groupBox_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setWordWrap(True)

        self.horizontalLayout_3.addWidget(self.label_4)

        self.reset_exif_Button = QPushButton(self.groupBox_4)
        self.reset_exif_Button.setObjectName(u"reset_exif_Button")
        self.reset_exif_Button.setMinimumSize(QSize(100, 0))
        self.reset_exif_Button.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_3.addWidget(self.reset_exif_Button)


        self.verticalLayout_2.addWidget(self.groupBox_4)

        self.groupBox_3 = QGroupBox(self.tabWidgetPage1)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_3 = QLabel(self.groupBox_3)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 3)

        self.enable_theme_checkBox = QCheckBox(self.groupBox_3)
        self.enable_theme_checkBox.setObjectName(u"enable_theme_checkBox")
        self.enable_theme_checkBox.setChecked(False)

        self.gridLayout_3.addWidget(self.enable_theme_checkBox, 1, 0, 1, 1)

        self.theme_selection_comboBox = QComboBox(self.groupBox_3)
        self.theme_selection_comboBox.addItem("")
        self.theme_selection_comboBox.addItem("")
        self.theme_selection_comboBox.addItem("")
        self.theme_selection_comboBox.setObjectName(u"theme_selection_comboBox")
        self.theme_selection_comboBox.setEnabled(False)
        self.theme_selection_comboBox.setMinimumSize(QSize(100, 0))
        self.theme_selection_comboBox.setMaximumSize(QSize(100, 16777215))

        self.gridLayout_3.addWidget(self.theme_selection_comboBox, 1, 2, 1, 1)

        self.save_and_close_Button = QPushButton(self.groupBox_3)
        self.save_and_close_Button.setObjectName(u"save_and_close_Button")

        self.gridLayout_3.addWidget(self.save_and_close_Button, 3, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(98, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_2, 1, 1, 1, 1)

        self.install_pkg_Button = QPushButton(self.groupBox_3)
        self.install_pkg_Button.setObjectName(u"install_pkg_Button")

        self.gridLayout_3.addWidget(self.install_pkg_Button, 2, 0, 1, 3)

        self.save_and_restart_Button = QPushButton(self.groupBox_3)
        self.save_and_restart_Button.setObjectName(u"save_and_restart_Button")

        self.gridLayout_3.addWidget(self.save_and_restart_Button, 3, 1, 1, 2)


        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.tabWidget.addTab(self.tabWidgetPage1, "")

        self.verticalLayout.addWidget(self.tabWidget)

        Settings_Window.setCentralWidget(self.centralwidget)

        self.retranslateUi(Settings_Window)
        self.enable_theme_checkBox.toggled.connect(self.theme_selection_comboBox.setEnabled)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Settings_Window)
    # setupUi

    def retranslateUi(self, Settings_Window):
        Settings_Window.setWindowTitle(QCoreApplication.translate("Settings_Window", u"Settings", None))
        self.pkg_info_groupBox.setTitle(QCoreApplication.translate("Settings_Window", u"Package information", None))
        self.label_optima35_latestversion.setText(QCoreApplication.translate("Settings_Window", u"unknown", None))
        self.label_latest_version.setText(QCoreApplication.translate("Settings_Window", u"Latest version", None))
        self.label.setText(QCoreApplication.translate("Settings_Window", u"OptimaLab35", None))
        self.label_optimalab35_latestversion.setText(QCoreApplication.translate("Settings_Window", u"unknown", None))
        self.label_9.setText(QCoreApplication.translate("Settings_Window", u"Package", None))
        self.label_optimalab35_localversion.setText(QCoreApplication.translate("Settings_Window", u"0.0.0", None))
        self.label_6.setText(QCoreApplication.translate("Settings_Window", u"Local Version", None))
        self.label_2.setText(QCoreApplication.translate("Settings_Window", u"optima35", None))
        self.label_optima35_localversion.setText(QCoreApplication.translate("Settings_Window", u"0.0.0", None))
#if QT_CONFIG(tooltip)
        self.check_local_Button.setToolTip(QCoreApplication.translate("Settings_Window", u"FOR DEVELOPER", None))
#endif // QT_CONFIG(tooltip)
        self.check_local_Button.setText(QCoreApplication.translate("Settings_Window", u"Check local", None))
#if QT_CONFIG(tooltip)
        self.update_local_Button.setToolTip(QCoreApplication.translate("Settings_Window", u"FOR DEVELOPER", None))
#endif // QT_CONFIG(tooltip)
        self.update_local_Button.setText(QCoreApplication.translate("Settings_Window", u"Update local", None))
        self.label_5.setText(QCoreApplication.translate("Settings_Window", u"TextLabel", None))
        self.label_last_check.setText(QCoreApplication.translate("Settings_Window", u"TextLabel", None))
        self.check_for_update_Button.setText(QCoreApplication.translate("Settings_Window", u"Check for update", None))
        self.update_and_restart_Button.setText(QCoreApplication.translate("Settings_Window", u"Update", None))
#if QT_CONFIG(tooltip)
        self.restart_checkBox.setToolTip(QCoreApplication.translate("Settings_Window", u"Restarts the app after update.", None))
#endif // QT_CONFIG(tooltip)
        self.restart_checkBox.setText(QCoreApplication.translate("Settings_Window", u"Restart", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage2), QCoreApplication.translate("Settings_Window", u"Updater", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Settings_Window", u"EXIF", None))
        self.label_4.setText(QCoreApplication.translate("Settings_Window", u"Reset selectable EXIF data to default", None))
        self.reset_exif_Button.setText(QCoreApplication.translate("Settings_Window", u"Reset", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Settings_Window", u"Theme", None))
        self.label_3.setText(QCoreApplication.translate("Settings_Window", u"Change theme from OS to PyQT Dark or Light", None))
#if QT_CONFIG(tooltip)
        self.enable_theme_checkBox.setToolTip(QCoreApplication.translate("Settings_Window", u"Changes will take effect after restarting the application.", None))
#endif // QT_CONFIG(tooltip)
        self.enable_theme_checkBox.setText(QCoreApplication.translate("Settings_Window", u"Custom theme", None))
        self.theme_selection_comboBox.setItemText(0, QCoreApplication.translate("Settings_Window", u"Auto", None))
        self.theme_selection_comboBox.setItemText(1, QCoreApplication.translate("Settings_Window", u"Dark", None))
        self.theme_selection_comboBox.setItemText(2, QCoreApplication.translate("Settings_Window", u"Light", None))

#if QT_CONFIG(tooltip)
        self.theme_selection_comboBox.setToolTip(QCoreApplication.translate("Settings_Window", u"Changes will take effect after restarting the application.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.save_and_close_Button.setToolTip(QCoreApplication.translate("Settings_Window", u"Changes will take effect after restarting the application.", None))
#endif // QT_CONFIG(tooltip)
        self.save_and_close_Button.setText(QCoreApplication.translate("Settings_Window", u"Apply theme", None))
        self.install_pkg_Button.setText(QCoreApplication.translate("Settings_Window", u"Install package for custom theme", None))
        self.save_and_restart_Button.setText(QCoreApplication.translate("Settings_Window", u"Apply and restart", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage1), QCoreApplication.translate("Settings_Window", u"Preferences", None))
    # retranslateUi

