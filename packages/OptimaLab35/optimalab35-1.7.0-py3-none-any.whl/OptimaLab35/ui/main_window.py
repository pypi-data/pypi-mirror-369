# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QProgressBar, QPushButton, QSizePolicy, QSlider,
    QSpinBox, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.NonModal)
        MainWindow.resize(450, 696)
        MainWindow.setMinimumSize(QSize(350, 677))
        MainWindow.setMaximumSize(QSize(450, 1000))
        self.actionInfo = QAction(MainWindow)
        self.actionInfo.setObjectName(u"actionInfo")
        self.actionPreview = QAction(MainWindow)
        self.actionPreview.setObjectName(u"actionPreview")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMaximumSize(QSize(420, 16777215))
        self.tab_1 = QWidget()
        self.tab_1.setObjectName(u"tab_1")
        self.verticalLayout_10 = QVBoxLayout(self.tab_1)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.folder_group = QGroupBox(self.tab_1)
        self.folder_group.setObjectName(u"folder_group")
        self.folder_group.setMaximumSize(QSize(400, 16777215))
        self.gridLayout_5 = QGridLayout(self.folder_group)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.input_folder_button = QPushButton(self.folder_group)
        self.input_folder_button.setObjectName(u"input_folder_button")
        self.input_folder_button.setMinimumSize(QSize(70, 0))
        self.input_folder_button.setFlat(False)

        self.gridLayout_5.addWidget(self.input_folder_button, 0, 1, 1, 1)

        self.output_path = QLineEdit(self.folder_group)
        self.output_path.setObjectName(u"output_path")

        self.gridLayout_5.addWidget(self.output_path, 0, 2, 1, 1)

        self.input_path = QLineEdit(self.folder_group)
        self.input_path.setObjectName(u"input_path")

        self.gridLayout_5.addWidget(self.input_path, 0, 0, 1, 1)

        self.output_folder_button = QPushButton(self.folder_group)
        self.output_folder_button.setObjectName(u"output_folder_button")
        self.output_folder_button.setMinimumSize(QSize(70, 0))

        self.gridLayout_5.addWidget(self.output_folder_button, 0, 3, 1, 1)


        self.verticalLayout_10.addWidget(self.folder_group)

        self.groupBox = QGroupBox(self.tab_1)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMaximumSize(QSize(400, 16777215))
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.quality_label_2 = QLabel(self.groupBox)
        self.quality_label_2.setObjectName(u"quality_label_2")

        self.gridLayout_4.addWidget(self.quality_label_2, 4, 0, 1, 1)

        self.jpg_quality_spinBox = QSpinBox(self.groupBox)
        self.jpg_quality_spinBox.setObjectName(u"jpg_quality_spinBox")
        self.jpg_quality_spinBox.setMinimum(1)
        self.jpg_quality_spinBox.setMaximum(100)
        self.jpg_quality_spinBox.setValue(90)

        self.gridLayout_4.addWidget(self.jpg_quality_spinBox, 3, 3, 1, 1)

        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_4.addWidget(self.label_11, 0, 0, 1, 1)

        self.optimize_checkBox = QCheckBox(self.groupBox)
        self.optimize_checkBox.setObjectName(u"optimize_checkBox")

        self.gridLayout_4.addWidget(self.optimize_checkBox, 0, 3, 1, 1)

        self.png_quality_Slider = QSlider(self.groupBox)
        self.png_quality_Slider.setObjectName(u"png_quality_Slider")
        self.png_quality_Slider.setMinimum(1)
        self.png_quality_Slider.setMaximum(9)
        self.png_quality_Slider.setPageStep(1)
        self.png_quality_Slider.setSliderPosition(6)
        self.png_quality_Slider.setOrientation(Qt.Orientation.Horizontal)
        self.png_quality_Slider.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.gridLayout_4.addWidget(self.png_quality_Slider, 4, 2, 1, 1)

        self.png_quality_spinBox = QSpinBox(self.groupBox)
        self.png_quality_spinBox.setObjectName(u"png_quality_spinBox")
        self.png_quality_spinBox.setEnabled(True)
        self.png_quality_spinBox.setMinimum(1)
        self.png_quality_spinBox.setMaximum(9)
        self.png_quality_spinBox.setValue(6)

        self.gridLayout_4.addWidget(self.png_quality_spinBox, 4, 3, 1, 1)

        self.quality_label_1 = QLabel(self.groupBox)
        self.quality_label_1.setObjectName(u"quality_label_1")

        self.gridLayout_4.addWidget(self.quality_label_1, 3, 0, 1, 1)

        self.image_type = QComboBox(self.groupBox)
        self.image_type.addItem(u"jpg")
        self.image_type.addItem(u"png")
        self.image_type.addItem(u"webp")
        self.image_type.setObjectName(u"image_type")

        self.gridLayout_4.addWidget(self.image_type, 0, 2, 1, 1)

        self.jpg_quality_Slider = QSlider(self.groupBox)
        self.jpg_quality_Slider.setObjectName(u"jpg_quality_Slider")
        self.jpg_quality_Slider.setMinimum(1)
        self.jpg_quality_Slider.setMaximum(100)
        self.jpg_quality_Slider.setSliderPosition(90)
        self.jpg_quality_Slider.setOrientation(Qt.Orientation.Horizontal)
        self.jpg_quality_Slider.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.gridLayout_4.addWidget(self.jpg_quality_Slider, 3, 2, 1, 1)

        self.label_13 = QLabel(self.groupBox)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_4.addWidget(self.label_13, 5, 0, 1, 1)

        self.resize_Slider = QSlider(self.groupBox)
        self.resize_Slider.setObjectName(u"resize_Slider")
        self.resize_Slider.setMinimum(1)
        self.resize_Slider.setMaximum(200)
        self.resize_Slider.setValue(100)
        self.resize_Slider.setOrientation(Qt.Orientation.Horizontal)
        self.resize_Slider.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.gridLayout_4.addWidget(self.resize_Slider, 5, 2, 1, 1)

        self.resize_spinBox = QSpinBox(self.groupBox)
        self.resize_spinBox.setObjectName(u"resize_spinBox")
        self.resize_spinBox.setEnabled(True)
        self.resize_spinBox.setMinimum(1)
        self.resize_spinBox.setMaximum(200)
        self.resize_spinBox.setSingleStep(1)
        self.resize_spinBox.setValue(100)

        self.gridLayout_4.addWidget(self.resize_spinBox, 5, 3, 1, 1)


        self.verticalLayout_10.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.tab_1)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMaximumSize(QSize(400, 16777215))
        self.groupBox_2.setMouseTracking(False)
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_3.addWidget(self.label_9, 1, 0, 1, 1)

        self.brightness_horizontalSlider = QSlider(self.groupBox_2)
        self.brightness_horizontalSlider.setObjectName(u"brightness_horizontalSlider")
        self.brightness_horizontalSlider.setMinimum(-100)
        self.brightness_horizontalSlider.setMaximum(100)
        self.brightness_horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.brightness_horizontalSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.gridLayout_3.addWidget(self.brightness_horizontalSlider, 1, 1, 1, 1)

        self.brightness_spinBox = QSpinBox(self.groupBox_2)
        self.brightness_spinBox.setObjectName(u"brightness_spinBox")
        self.brightness_spinBox.setEnabled(True)
        self.brightness_spinBox.setMinimum(-100)
        self.brightness_spinBox.setMaximum(100)
        self.brightness_spinBox.setValue(0)

        self.gridLayout_3.addWidget(self.brightness_spinBox, 1, 2, 1, 1)

        self.contrast_spinBox = QSpinBox(self.groupBox_2)
        self.contrast_spinBox.setObjectName(u"contrast_spinBox")
        self.contrast_spinBox.setEnabled(True)
        self.contrast_spinBox.setMinimum(-100)
        self.contrast_spinBox.setMaximum(100)
        self.contrast_spinBox.setValue(0)

        self.gridLayout_3.addWidget(self.contrast_spinBox, 4, 2, 1, 1)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_3.addWidget(self.label_10, 4, 0, 1, 1)

        self.contrast_horizontalSlider = QSlider(self.groupBox_2)
        self.contrast_horizontalSlider.setObjectName(u"contrast_horizontalSlider")
        self.contrast_horizontalSlider.setMinimum(-100)
        self.contrast_horizontalSlider.setMaximum(100)
        self.contrast_horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.contrast_horizontalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)

        self.gridLayout_3.addWidget(self.contrast_horizontalSlider, 4, 1, 1, 1)

        self.grayscale_checkBox = QCheckBox(self.groupBox_2)
        self.grayscale_checkBox.setObjectName(u"grayscale_checkBox")

        self.gridLayout_3.addWidget(self.grayscale_checkBox, 5, 0, 1, 2)

        self.preview_Button = QPushButton(self.groupBox_2)
        self.preview_Button.setObjectName(u"preview_Button")

        self.gridLayout_3.addWidget(self.preview_Button, 5, 2, 1, 1)


        self.verticalLayout_10.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.tab_1)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setEnabled(True)
        self.groupBox_3.setMaximumSize(QSize(400, 16777215))
        self.groupBox_3.setFlat(False)
        self.groupBox_3.setCheckable(False)
        self.groupBox_3.setChecked(False)
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.watermark_lineEdit = QLineEdit(self.groupBox_3)
        self.watermark_lineEdit.setObjectName(u"watermark_lineEdit")
        self.watermark_lineEdit.setEnabled(True)

        self.horizontalLayout_5.addWidget(self.watermark_lineEdit)

        self.label_12 = QLabel(self.groupBox_3)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_5.addWidget(self.label_12)

        self.font_size_comboBox = QComboBox(self.groupBox_3)
        self.font_size_comboBox.addItem("")
        self.font_size_comboBox.addItem("")
        self.font_size_comboBox.addItem("")
        self.font_size_comboBox.addItem("")
        self.font_size_comboBox.addItem("")
        self.font_size_comboBox.setObjectName(u"font_size_comboBox")

        self.horizontalLayout_5.addWidget(self.font_size_comboBox)


        self.verticalLayout_10.addWidget(self.groupBox_3)

        self.rename_group = QGroupBox(self.tab_1)
        self.rename_group.setObjectName(u"rename_group")
        self.rename_group.setMaximumSize(QSize(400, 16777215))
        self.gridLayout_6 = QGridLayout(self.rename_group)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.rename_checkbox = QCheckBox(self.rename_group)
        self.rename_checkbox.setObjectName(u"rename_checkbox")

        self.gridLayout_6.addWidget(self.rename_checkbox, 0, 0, 1, 1)

        self.revert_checkbox = QCheckBox(self.rename_group)
        self.revert_checkbox.setObjectName(u"revert_checkbox")
        self.revert_checkbox.setEnabled(False)

        self.gridLayout_6.addWidget(self.revert_checkbox, 0, 1, 1, 1)

        self.filename = QLineEdit(self.rename_group)
        self.filename.setObjectName(u"filename")
        self.filename.setEnabled(False)

        self.gridLayout_6.addWidget(self.filename, 1, 0, 1, 2)


        self.verticalLayout_10.addWidget(self.rename_group)

        self.widget_9 = QWidget(self.tab_1)
        self.widget_9.setObjectName(u"widget_9")
        self.widget_9.setMaximumSize(QSize(400, 50))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_9)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.progressBar = QProgressBar(self.widget_9)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(0)

        self.horizontalLayout_3.addWidget(self.progressBar)

        self.start_button = QPushButton(self.widget_9)
        self.start_button.setObjectName(u"start_button")
        self.start_button.setEnabled(True)

        self.horizontalLayout_3.addWidget(self.start_button)

        self.insert_exif_Button = QPushButton(self.widget_9)
        self.insert_exif_Button.setObjectName(u"insert_exif_Button")
        self.insert_exif_Button.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.insert_exif_Button)


        self.verticalLayout_10.addWidget(self.widget_9)

        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_9 = QVBoxLayout(self.tab_2)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.exif_group = QGroupBox(self.tab_2)
        self.exif_group.setObjectName(u"exif_group")
        self.horizontalLayout = QHBoxLayout(self.exif_group)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.exif_checkbox = QCheckBox(self.exif_group)
        self.exif_checkbox.setObjectName(u"exif_checkbox")
        self.exif_checkbox.setEnabled(True)

        self.horizontalLayout.addWidget(self.exif_checkbox)

        self.exif_copy_checkBox = QCheckBox(self.exif_group)
        self.exif_copy_checkBox.setObjectName(u"exif_copy_checkBox")

        self.horizontalLayout.addWidget(self.exif_copy_checkBox)

        self.edit_exif_button = QPushButton(self.exif_group)
        self.edit_exif_button.setObjectName(u"edit_exif_button")
        self.edit_exif_button.setEnabled(True)

        self.horizontalLayout.addWidget(self.edit_exif_button)


        self.verticalLayout_9.addWidget(self.exif_group)

        self.exif_options_group = QGroupBox(self.tab_2)
        self.exif_options_group.setObjectName(u"exif_options_group")
        self.exif_options_group.setEnabled(False)
        self.gridLayout_7 = QGridLayout(self.exif_options_group)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_7 = QLabel(self.exif_options_group)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_7.addWidget(self.label_7, 6, 0, 1, 1)

        self.label = QLabel(self.exif_options_group)
        self.label.setObjectName(u"label")

        self.gridLayout_7.addWidget(self.label, 0, 0, 1, 1)

        self.image_description_comboBox = QComboBox(self.exif_options_group)
        self.image_description_comboBox.setObjectName(u"image_description_comboBox")

        self.gridLayout_7.addWidget(self.image_description_comboBox, 5, 0, 1, 1)

        self.label_4 = QLabel(self.exif_options_group)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_7.addWidget(self.label_4, 2, 1, 1, 1)

        self.time_comboBox = QComboBox(self.exif_options_group)
        self.time_comboBox.setObjectName(u"time_comboBox")

        self.gridLayout_7.addWidget(self.time_comboBox, 9, 1, 1, 1)

        self.dev_comboBox = QComboBox(self.exif_options_group)
        self.dev_comboBox.setObjectName(u"dev_comboBox")

        self.gridLayout_7.addWidget(self.dev_comboBox, 9, 0, 1, 1)

        self.label_5 = QLabel(self.exif_options_group)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_7.addWidget(self.label_5, 4, 0, 1, 1)

        self.model_comboBox = QComboBox(self.exif_options_group)
        self.model_comboBox.setObjectName(u"model_comboBox")

        self.gridLayout_7.addWidget(self.model_comboBox, 1, 1, 1, 1)

        self.lens_comboBox = QComboBox(self.exif_options_group)
        self.lens_comboBox.setObjectName(u"lens_comboBox")

        self.gridLayout_7.addWidget(self.lens_comboBox, 3, 0, 1, 1)

        self.user_comment_comboBox = QComboBox(self.exif_options_group)
        self.user_comment_comboBox.setObjectName(u"user_comment_comboBox")

        self.gridLayout_7.addWidget(self.user_comment_comboBox, 5, 1, 1, 1)

        self.make_comboBox = QComboBox(self.exif_options_group)
        self.make_comboBox.setObjectName(u"make_comboBox")

        self.gridLayout_7.addWidget(self.make_comboBox, 1, 0, 1, 1)

        self.label_14 = QLabel(self.exif_options_group)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_7.addWidget(self.label_14, 8, 0, 1, 1)

        self.label_8 = QLabel(self.exif_options_group)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_7.addWidget(self.label_8, 6, 1, 1, 1)

        self.label_3 = QLabel(self.exif_options_group)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_7.addWidget(self.label_3, 0, 1, 1, 1)

        self.label_6 = QLabel(self.exif_options_group)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_7.addWidget(self.label_6, 4, 1, 1, 1)

        self.copyright_info_comboBox = QComboBox(self.exif_options_group)
        self.copyright_info_comboBox.setObjectName(u"copyright_info_comboBox")

        self.gridLayout_7.addWidget(self.copyright_info_comboBox, 7, 1, 1, 1)

        self.iso_comboBox = QComboBox(self.exif_options_group)
        self.iso_comboBox.setObjectName(u"iso_comboBox")

        self.gridLayout_7.addWidget(self.iso_comboBox, 3, 1, 1, 1)

        self.label_15 = QLabel(self.exif_options_group)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_7.addWidget(self.label_15, 8, 1, 1, 1)

        self.label_2 = QLabel(self.exif_options_group)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_7.addWidget(self.label_2, 2, 0, 1, 1)

        self.artist_comboBox = QComboBox(self.exif_options_group)
        self.artist_comboBox.setObjectName(u"artist_comboBox")

        self.gridLayout_7.addWidget(self.artist_comboBox, 7, 0, 1, 1)


        self.verticalLayout_9.addWidget(self.exif_options_group)

        self.gps_groupBox = QGroupBox(self.tab_2)
        self.gps_groupBox.setObjectName(u"gps_groupBox")
        self.gps_groupBox.setEnabled(False)
        self.horizontalLayout_4 = QHBoxLayout(self.gps_groupBox)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.gps_checkBox = QCheckBox(self.gps_groupBox)
        self.gps_checkBox.setObjectName(u"gps_checkBox")

        self.horizontalLayout_4.addWidget(self.gps_checkBox)

        self.lat_lineEdit = QLineEdit(self.gps_groupBox)
        self.lat_lineEdit.setObjectName(u"lat_lineEdit")
        self.lat_lineEdit.setEnabled(False)
        self.lat_lineEdit.setMaxLength(8)

        self.horizontalLayout_4.addWidget(self.lat_lineEdit)

        self.long_lineEdit = QLineEdit(self.gps_groupBox)
        self.long_lineEdit.setObjectName(u"long_lineEdit")
        self.long_lineEdit.setEnabled(False)
        self.long_lineEdit.setMaxLength(8)

        self.horizontalLayout_4.addWidget(self.long_lineEdit)


        self.verticalLayout_9.addWidget(self.gps_groupBox)

        self.date_groupBox = QGroupBox(self.tab_2)
        self.date_groupBox.setObjectName(u"date_groupBox")
        self.date_groupBox.setEnabled(False)
        self.horizontalLayout_2 = QHBoxLayout(self.date_groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.add_date_checkBox = QCheckBox(self.date_groupBox)
        self.add_date_checkBox.setObjectName(u"add_date_checkBox")

        self.horizontalLayout_2.addWidget(self.add_date_checkBox)

        self.dateEdit = QDateEdit(self.date_groupBox)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setEnabled(False)
        self.dateEdit.setDateTime(QDateTime(QDate(2024, 12, 31), QTime(20, 0, 0)))
        self.dateEdit.setMaximumDate(QDate(2038, 12, 31))
        self.dateEdit.setMinimumDate(QDate(1970, 1, 1))
        self.dateEdit.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateEdit)


        self.verticalLayout_9.addWidget(self.date_groupBox)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 450, 26))
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuSettings = QMenu(self.menuBar)
        self.menuSettings.setObjectName(u"menuSettings")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuSettings.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addAction(self.actionAbout)
        self.menuSettings.addAction(self.actionSettings)

        self.retranslateUi(MainWindow)
        self.rename_checkbox.toggled.connect(self.filename.setEnabled)
        self.exif_checkbox.toggled.connect(self.exif_options_group.setEnabled)
        self.jpg_quality_Slider.valueChanged.connect(self.jpg_quality_spinBox.setValue)
        self.exif_copy_checkBox.toggled.connect(self.exif_checkbox.setDisabled)
        self.exif_checkbox.toggled.connect(self.exif_copy_checkBox.setDisabled)
        self.resize_spinBox.valueChanged.connect(self.resize_Slider.setValue)
        self.png_quality_spinBox.valueChanged.connect(self.png_quality_Slider.setValue)
        self.contrast_horizontalSlider.valueChanged.connect(self.contrast_spinBox.setValue)
        self.resize_Slider.valueChanged.connect(self.resize_spinBox.setValue)
        self.brightness_horizontalSlider.valueChanged.connect(self.brightness_spinBox.setValue)
        self.exif_checkbox.toggled.connect(self.date_groupBox.setEnabled)
        self.png_quality_Slider.valueChanged.connect(self.png_quality_spinBox.setValue)
        self.gps_checkBox.toggled.connect(self.lat_lineEdit.setEnabled)
        self.exif_checkbox.toggled.connect(self.insert_exif_Button.setEnabled)
        self.gps_checkBox.toggled.connect(self.long_lineEdit.setEnabled)
        self.brightness_spinBox.valueChanged.connect(self.brightness_horizontalSlider.setValue)
        self.resize_Slider.valueChanged.connect(self.resize_spinBox.setValue)
        self.exif_checkbox.toggled.connect(self.gps_groupBox.setEnabled)
        self.contrast_spinBox.valueChanged.connect(self.contrast_horizontalSlider.setValue)
        self.add_date_checkBox.toggled.connect(self.dateEdit.setEnabled)
        self.jpg_quality_spinBox.valueChanged.connect(self.jpg_quality_Slider.setValue)
        self.rename_checkbox.toggled.connect(self.revert_checkbox.setEnabled)

        self.tabWidget.setCurrentIndex(0)
        self.font_size_comboBox.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"OptimaLab35", None))
        self.actionInfo.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionPreview.setText(QCoreApplication.translate("MainWindow", u"Preview image", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"Preferences...", None))
        self.folder_group.setTitle(QCoreApplication.translate("MainWindow", u"File selection", None))
#if QT_CONFIG(tooltip)
        self.input_folder_button.setToolTip(QCoreApplication.translate("MainWindow", u"Open a file browser to select a folder for loading images.", None))
#endif // QT_CONFIG(tooltip)
        self.input_folder_button.setText(QCoreApplication.translate("MainWindow", u"Input", None))
        self.output_path.setText("")
        self.output_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Output folder", None))
#if QT_CONFIG(tooltip)
        self.input_path.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.input_path.setText("")
        self.input_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Input folder", None))
#if QT_CONFIG(tooltip)
        self.output_folder_button.setToolTip(QCoreApplication.translate("MainWindow", u"Open a file browser to select a folder for saving images.", None))
#endif // QT_CONFIG(tooltip)
        self.output_folder_button.setText(QCoreApplication.translate("MainWindow", u"Output", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Export Settings", None))
        self.quality_label_2.setText(QCoreApplication.translate("MainWindow", u"Quality", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Format     ", None))
#if QT_CONFIG(tooltip)
        self.optimize_checkBox.setToolTip(QCoreApplication.translate("MainWindow", u"Recommended for web use. Enables PIL optimization to slightly reduce file size without visible quality loss. ", None))
#endif // QT_CONFIG(tooltip)
        self.optimize_checkBox.setText(QCoreApplication.translate("MainWindow", u"Optimize", None))
#if QT_CONFIG(tooltip)
        self.png_quality_Slider.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.quality_label_1.setText(QCoreApplication.translate("MainWindow", u"Quality", None))

#if QT_CONFIG(tooltip)
        self.image_type.setToolTip(QCoreApplication.translate("MainWindow", u"Select export file type.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_13.setToolTip(QCoreApplication.translate("MainWindow", u"Choose image scaling options. \u26a0 Upscaling large images may freeze the system depending on hardware.", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Resize", None))
#if QT_CONFIG(tooltip)
        self.resize_Slider.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.resize_spinBox.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Image Adjustments", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Brightness", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Contrast", None))
#if QT_CONFIG(tooltip)
        self.grayscale_checkBox.setToolTip(QCoreApplication.translate("MainWindow", u"Converts image to Grayscale", None))
#endif // QT_CONFIG(tooltip)
        self.grayscale_checkBox.setText(QCoreApplication.translate("MainWindow", u"Black and White Mode", None))
#if QT_CONFIG(tooltip)
        self.preview_Button.setToolTip(QCoreApplication.translate("MainWindow", u"Open a preview window to see how brightness, contrast, and grayscale adjustments affect your image.", None))
#endif // QT_CONFIG(tooltip)
        self.preview_Button.setText(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Watermarking", None))
        self.watermark_lineEdit.setText("")
        self.watermark_lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Watermark Text", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Size", None))
        self.font_size_comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Tiny", None))
        self.font_size_comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Small", None))
        self.font_size_comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Normal", None))
        self.font_size_comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Large", None))
        self.font_size_comboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"Huge", None))

#if QT_CONFIG(tooltip)
        self.font_size_comboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Adjust the font size for the watermark. Size scales proportionally to image dimensions.", None))
#endif // QT_CONFIG(tooltip)
        self.font_size_comboBox.setCurrentText(QCoreApplication.translate("MainWindow", u"Normal", None))
        self.rename_group.setTitle(QCoreApplication.translate("MainWindow", u"File Naming", None))
#if QT_CONFIG(tooltip)
        self.rename_checkbox.setToolTip(QCoreApplication.translate("MainWindow", u"Enable to rename all images with a new base name. '_xx' will be added at the end of each filename.", None))
#endif // QT_CONFIG(tooltip)
        self.rename_checkbox.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
#if QT_CONFIG(tooltip)
        self.revert_checkbox.setToolTip(QCoreApplication.translate("MainWindow", u"Reverses the order of images. Useful for scanned film rolls where the last image (e.g., 36) is scanned first.", None))
#endif // QT_CONFIG(tooltip)
        self.revert_checkbox.setText(QCoreApplication.translate("MainWindow", u"Revert order", None))
        self.filename.setText("")
        self.filename.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter new File Names", None))
        self.start_button.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
#if QT_CONFIG(tooltip)
        self.insert_exif_Button.setToolTip(QCoreApplication.translate("MainWindow", u"Insert EXIF without modifying images.", None))
#endif // QT_CONFIG(tooltip)
        self.insert_exif_Button.setText(QCoreApplication.translate("MainWindow", u"Insert Exif", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QCoreApplication.translate("MainWindow", u"Main", None))
        self.exif_group.setTitle(QCoreApplication.translate("MainWindow", u"EXIF Settings", None))
#if QT_CONFIG(tooltip)
        self.exif_checkbox.setToolTip(QCoreApplication.translate("MainWindow", u"Add your own EXIF data to the images with the selection from below.", None))
#endif // QT_CONFIG(tooltip)
        self.exif_checkbox.setText(QCoreApplication.translate("MainWindow", u"Custom EXIF", None))
#if QT_CONFIG(tooltip)
        self.exif_copy_checkBox.setToolTip(QCoreApplication.translate("MainWindow", u"Copy EXIF from the input data.", None))
#endif // QT_CONFIG(tooltip)
        self.exif_copy_checkBox.setText(QCoreApplication.translate("MainWindow", u"Copy EXIF", None))
#if QT_CONFIG(tooltip)
        self.edit_exif_button.setToolTip(QCoreApplication.translate("MainWindow", u"Open the EXIF Editor to add or remove metadata entries, making them available for selection.", None))
#endif // QT_CONFIG(tooltip)
        self.edit_exif_button.setText(QCoreApplication.translate("MainWindow", u"EXIF editor", None))
        self.exif_options_group.setTitle(QCoreApplication.translate("MainWindow", u"Essential EXIF Info", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Artist", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Make", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"ISO", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Film", None))
        self.make_comboBox.setCurrentText("")
        self.make_comboBox.setPlaceholderText("")
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Developer", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Copyright", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Scanner", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Time", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Lens", None))
        self.gps_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"GPS Coordinates", None))
#if QT_CONFIG(tooltip)
        self.gps_checkBox.setToolTip(QCoreApplication.translate("MainWindow", u"From a Homepage like latlong.net", None))
#endif // QT_CONFIG(tooltip)
        self.gps_checkBox.setText(QCoreApplication.translate("MainWindow", u"Enable GPS Data", None))
#if QT_CONFIG(tooltip)
        self.lat_lineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"Format: xx.xxxxxx (e.g., 57.618520)", None))
#endif // QT_CONFIG(tooltip)
        self.lat_lineEdit.setText("")
        self.lat_lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Latitude", None))
#if QT_CONFIG(tooltip)
        self.long_lineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"Format: xx.xxxxxx (e.g., -13.779602)", None))
#endif // QT_CONFIG(tooltip)
        self.long_lineEdit.setText("")
        self.long_lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Longitude", None))
        self.date_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Original Capture Data and Time", None))
#if QT_CONFIG(tooltip)
        self.add_date_checkBox.setToolTip(QCoreApplication.translate("MainWindow", u"Adds \"Date and Time (original)\" to the image, i.e. when the picture was taking.", None))
#endif // QT_CONFIG(tooltip)
        self.add_date_checkBox.setText(QCoreApplication.translate("MainWindow", u"Enable Timestamp", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"EXIF", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

