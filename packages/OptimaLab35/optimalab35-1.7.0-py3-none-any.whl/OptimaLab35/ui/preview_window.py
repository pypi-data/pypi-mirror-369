# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preview_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_Preview_Window(object):
    def setupUi(self, Preview_Window):
        if not Preview_Window.objectName():
            Preview_Window.setObjectName(u"Preview_Window")
        Preview_Window.resize(875, 775)
        Preview_Window.setMinimumSize(QSize(800, 700))
        self.centralwidget = QWidget(Preview_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.QLabel = QLabel(self.centralwidget)
        self.QLabel.setObjectName(u"QLabel")
        self.QLabel.setMinimumSize(QSize(628, 628))
        self.QLabel.setFrameShape(QFrame.Shape.Box)
        self.QLabel.setScaledContents(False)

        self.horizontalLayout.addWidget(self.QLabel)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(160, 628))
        self.widget.setMaximumSize(QSize(180, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.widget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_3 = QGroupBox(self.widget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.image_path_lineEdit = QLineEdit(self.groupBox_3)
        self.image_path_lineEdit.setObjectName(u"image_path_lineEdit")
        self.image_path_lineEdit.setEnabled(False)

        self.verticalLayout_3.addWidget(self.image_path_lineEdit)

        self.load_Button = QPushButton(self.groupBox_3)
        self.load_Button.setObjectName(u"load_Button")

        self.verticalLayout_3.addWidget(self.load_Button)


        self.verticalLayout_4.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(self.widget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout = QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.brightness_spinBox = QSpinBox(self.groupBox_2)
        self.brightness_spinBox.setObjectName(u"brightness_spinBox")
        self.brightness_spinBox.setMinimum(-100)
        self.brightness_spinBox.setMaximum(100)

        self.verticalLayout.addWidget(self.brightness_spinBox)

        self.brightness_Slider = QSlider(self.groupBox_2)
        self.brightness_Slider.setObjectName(u"brightness_Slider")
        self.brightness_Slider.setMinimum(-100)
        self.brightness_Slider.setMaximum(100)
        self.brightness_Slider.setOrientation(Qt.Orientation.Horizontal)
        self.brightness_Slider.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.verticalLayout.addWidget(self.brightness_Slider)

        self.reset_brightness_Button = QPushButton(self.groupBox_2)
        self.reset_brightness_Button.setObjectName(u"reset_brightness_Button")

        self.verticalLayout.addWidget(self.reset_brightness_Button)


        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.widget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.contrast_spinBox = QSpinBox(self.groupBox)
        self.contrast_spinBox.setObjectName(u"contrast_spinBox")
        self.contrast_spinBox.setMinimum(-100)
        self.contrast_spinBox.setMaximum(100)

        self.verticalLayout_2.addWidget(self.contrast_spinBox)

        self.contrast_Slider = QSlider(self.groupBox)
        self.contrast_Slider.setObjectName(u"contrast_Slider")
        self.contrast_Slider.setMinimum(-100)
        self.contrast_Slider.setMaximum(100)
        self.contrast_Slider.setOrientation(Qt.Orientation.Horizontal)
        self.contrast_Slider.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.verticalLayout_2.addWidget(self.contrast_Slider)

        self.reset_contrast_Button = QPushButton(self.groupBox)
        self.reset_contrast_Button.setObjectName(u"reset_contrast_Button")

        self.verticalLayout_2.addWidget(self.reset_contrast_Button)


        self.verticalLayout_4.addWidget(self.groupBox)

        self.groupBox_5 = QGroupBox(self.widget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout = QGridLayout(self.groupBox_5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.grayscale_checkBox = QCheckBox(self.groupBox_5)
        self.grayscale_checkBox.setObjectName(u"grayscale_checkBox")

        self.gridLayout.addWidget(self.grayscale_checkBox, 0, 0, 1, 1)


        self.verticalLayout_4.addWidget(self.groupBox_5)

        self.verticalSpacer = QSpacerItem(20, 219, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label.setAutoFillBackground(False)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.label)

        self.show_OG_Button = QPushButton(self.widget)
        self.show_OG_Button.setObjectName(u"show_OG_Button")

        self.verticalLayout_4.addWidget(self.show_OG_Button)

        self.groupBox_4 = QGroupBox(self.widget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setMaximumSize(QSize(170, 16777215))
        self.gridLayout_2 = QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox = QCheckBox(self.groupBox_4)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox, 3, 0, 1, 2)

        self.close_Button = QPushButton(self.groupBox_4)
        self.close_Button.setObjectName(u"close_Button")

        self.gridLayout_2.addWidget(self.close_Button, 4, 0, 1, 2)

        self.live_update = QCheckBox(self.groupBox_4)
        self.live_update.setObjectName(u"live_update")
        font = QFont()
        font.setPointSize(11)
        self.live_update.setFont(font)
        self.live_update.setChecked(True)

        self.gridLayout_2.addWidget(self.live_update, 0, 0, 1, 1)

        self.scale_Slider = QSlider(self.groupBox_4)
        self.scale_Slider.setObjectName(u"scale_Slider")
        self.scale_Slider.setMinimum(10)
        self.scale_Slider.setMaximum(100)
        self.scale_Slider.setPageStep(10)
        self.scale_Slider.setValue(50)
        self.scale_Slider.setOrientation(Qt.Orientation.Horizontal)
        self.scale_Slider.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.gridLayout_2.addWidget(self.scale_Slider, 1, 0, 1, 2)

        self.update_Button = QPushButton(self.groupBox_4)
        self.update_Button.setObjectName(u"update_Button")
        self.update_Button.setEnabled(False)
        self.update_Button.setAutoFillBackground(False)

        self.gridLayout_2.addWidget(self.update_Button, 2, 0, 1, 2)

        self.scale_label = QLabel(self.groupBox_4)
        self.scale_label.setObjectName(u"scale_label")
        font1 = QFont()
        font1.setPointSize(9)
        self.scale_label.setFont(font1)

        self.gridLayout_2.addWidget(self.scale_label, 0, 1, 1, 1)


        self.verticalLayout_4.addWidget(self.groupBox_4)


        self.horizontalLayout.addWidget(self.widget)

        Preview_Window.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Preview_Window)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 875, 19))
        Preview_Window.setMenuBar(self.menubar)

        self.retranslateUi(Preview_Window)
        self.brightness_Slider.valueChanged.connect(self.brightness_spinBox.setValue)
        self.brightness_spinBox.valueChanged.connect(self.brightness_Slider.setValue)
        self.contrast_Slider.valueChanged.connect(self.contrast_spinBox.setValue)
        self.contrast_spinBox.valueChanged.connect(self.contrast_Slider.setValue)
        self.live_update.toggled.connect(self.update_Button.setDisabled)
        self.scale_Slider.valueChanged.connect(self.scale_label.setNum)

        QMetaObject.connectSlotsByName(Preview_Window)
    # setupUi

    def retranslateUi(self, Preview_Window):
        Preview_Window.setWindowTitle(QCoreApplication.translate("Preview_Window", u"OptimaLab35 - Preview", None))
        self.QLabel.setText("")
        self.groupBox_3.setTitle(QCoreApplication.translate("Preview_Window", u"File", None))
#if QT_CONFIG(tooltip)
        self.image_path_lineEdit.setToolTip(QCoreApplication.translate("Preview_Window", u"Enter the path to the image file or use the 'Select Image' button to browse.", None))
#endif // QT_CONFIG(tooltip)
        self.image_path_lineEdit.setPlaceholderText(QCoreApplication.translate("Preview_Window", u"Image Path", None))
        self.load_Button.setText(QCoreApplication.translate("Preview_Window", u"Select image", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Preview_Window", u"Brightness", None))
#if QT_CONFIG(tooltip)
        self.reset_brightness_Button.setToolTip(QCoreApplication.translate("Preview_Window", u"Click to reset the brightness to its default value (0).", None))
#endif // QT_CONFIG(tooltip)
        self.reset_brightness_Button.setText(QCoreApplication.translate("Preview_Window", u"Reset", None))
        self.groupBox.setTitle(QCoreApplication.translate("Preview_Window", u"Contrast", None))
#if QT_CONFIG(tooltip)
        self.reset_contrast_Button.setToolTip(QCoreApplication.translate("Preview_Window", u"Click to reset the contrast to its default value (0).", None))
#endif // QT_CONFIG(tooltip)
        self.reset_contrast_Button.setText(QCoreApplication.translate("Preview_Window", u"Reset", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Preview_Window", u"Grayscale", None))
#if QT_CONFIG(tooltip)
        self.grayscale_checkBox.setToolTip(QCoreApplication.translate("Preview_Window", u"Convert the image to grayscale (black and white).", None))
#endif // QT_CONFIG(tooltip)
        self.grayscale_checkBox.setText(QCoreApplication.translate("Preview_Window", u"Black and White", None))
        self.label.setText(QCoreApplication.translate("Preview_Window", u"Hold button to show original image", None))
        self.show_OG_Button.setText(QCoreApplication.translate("Preview_Window", u"Show", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Preview_Window", u"Behavior", None))
#if QT_CONFIG(tooltip)
        self.checkBox.setToolTip(QCoreApplication.translate("Preview_Window", u"Enable to copy adjustments to the main window upon closing", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox.setText(QCoreApplication.translate("Preview_Window", u"Copy Values", None))
#if QT_CONFIG(tooltip)
        self.close_Button.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.close_Button.setText(QCoreApplication.translate("Preview_Window", u"Close", None))
#if QT_CONFIG(tooltip)
        self.live_update.setToolTip(QCoreApplication.translate("Preview_Window", u"Live update applies changes instantly. If the app becomes unresponsive or lags, disable this option.", None))
#endif // QT_CONFIG(tooltip)
        self.live_update.setText(QCoreApplication.translate("Preview_Window", u"Live refresh", None))
#if QT_CONFIG(tooltip)
        self.scale_Slider.setToolTip(QCoreApplication.translate("Preview_Window", u"Sets the resize value for the preview image. A high value may cause the application to freeze.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.update_Button.setToolTip(QCoreApplication.translate("Preview_Window", u"Apply Changes to Preview", None))
#endif // QT_CONFIG(tooltip)
        self.update_Button.setText(QCoreApplication.translate("Preview_Window", u"Refresh image", None))
#if QT_CONFIG(tooltip)
        self.scale_label.setToolTip(QCoreApplication.translate("Preview_Window", u"Sets the resize value for the preview image. A high value may cause the application to freeze.", None))
#endif // QT_CONFIG(tooltip)
        self.scale_label.setText(QCoreApplication.translate("Preview_Window", u"50", None))
    # retranslateUi

