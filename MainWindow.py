from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAbstractItemView
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
import traceback
import sys, os, time, re
import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from model import Resnet_Unet, Unet
from PIL import Image
from skimage import measure
from skimage.morphology import remove_small_objects, binary_opening
import pyautogui  # 用于获取屏幕分辨率的库
import shutil
# 导入其他界面
from Export import win_Export
from Options import win_Options
from Training import win_Training
from Manual import win_Manual
from Feedback import win_Feedback
from About import win_About
all_header_combobox = []  # 用来装行表头所有复选框 全局变量


class CheckBoxHeader(QtWidgets.QHeaderView):
    """自定义表头类"""
    select_all_clicked = pyqtSignal(bool)  # 自定义复选框全选信号
    # 这4个变量控制列头复选框的样式，位置以及大小
    _x_offset, _y_offset, _width, _height = 15, 0, 20, 20

    def __init__(self, orientation=QtCore.Qt.Horizontal, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isOn = False

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()
        self._y_offset = int((rect.height() - self._width) / 2.)
        if logicalIndex == 0:
            option = QtWidgets.QStyleOptionButton()
            option.rect = QtCore.QRect(rect.x() + self._x_offset, rect.y() + self._y_offset, self._width, self._height)
            option.state = QtWidgets.QStyle.State_Enabled | QtWidgets.QStyle.State_Active
            if self.isOn:
                option.state |= QtWidgets.QStyle.State_On
            else:
                option.state |= QtWidgets.QStyle.State_Off
            self.style().drawControl(QtWidgets.QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if 0 == index:
            x = self.sectionPosition(index)
            if (x + self._x_offset < event.pos().x() < x + self._x_offset + self._width and self._y_offset <
                    event.pos().y() < self._y_offset + self._height):
                if self.isOn:
                    self.isOn = False
                else:
                    self.isOn = True
                self.select_all_clicked.emit(self.isOn)  # 当用户点击了行表头复选框，发射 自定义信号 select_all_clicked()
                self.updateSection(0)
        super(CheckBoxHeader, self).mousePressEvent(event)

    def change_state(self, isOn):  # 自定义信号 select_all_clicked 的槽方法
        if isOn:  # 如果行表头复选框为勾选状态
            # 将所有的复选框都设为勾选状态
            for i in all_header_combobox:
                i.setCheckState(QtCore.Qt.Checked)
        else:
            for i in all_header_combobox:
                i.setCheckState(QtCore.Qt.Unchecked)


class Ui_MainWindow(object):
    def setupUi(self, Main):
        Main.setObjectName("Main")
        Main.resize(1600, 938)
        Main.setMinimumSize(QtCore.QSize(1600, 938))
        font = QtGui.QFont()
        Main.setFont(font)
        self.centralwidget = QtWidgets.QWidget(Main)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 1580, 906))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.verticalLayoutWidget)
        self.groupBox.setMinimumSize(QtCore.QSize(1549, 840))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 1543, 808))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_13 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_13.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_13.setObjectName("label_13")
        self.verticalLayout_4.addWidget(self.label_13)
        self.ModelTable = QtWidgets.QTableWidget(self.horizontalLayoutWidget)
        self.ModelTable.verticalHeader().setSectionsMovable(True)
        self.ModelTable.verticalHeader().setDragEnabled(True)
        self.ModelTable.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)
        self.ModelTable.setMinimumSize(QtCore.QSize(400, 180))
        self.ModelTable.setMaximumSize(QtCore.QSize(400, 180))
        self.ModelTable.setObjectName("ModelTable")
        self.ModelTable.setColumnCount(3)
        self.ModelTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.ModelTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.ModelTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.ModelTable.setHorizontalHeaderItem(2, item)
        self.ModelTable.setColumnWidth(0, 70)
        self.ModelTable.setColumnWidth(1, 149)
        self.ModelTable.setColumnWidth(2, 157)
        self.verticalLayout_4.addWidget(self.ModelTable)
        self.label_12 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_12.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_12.setObjectName("label_12")
        self.verticalLayout_4.addWidget(self.label_12)
        self.FileTable = QtWidgets.QTableWidget(self.horizontalLayoutWidget)
        # self.FileTable.verticalHeader().setSectionsMovable(True)
        # self.FileTable.verticalHeader().setDragEnabled(True)
        # self.FileTable.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)
        self.FileTable.setObjectName("FileTable")
        self.FileTable.setColumnCount(4)
        self.FileTable.setRowCount(0)
        header = CheckBoxHeader()
        self.FileTable.setHorizontalHeader(header)
        header.select_all_clicked.connect(header.change_state)  # 行表头复选框单击信号与槽
        item = QtWidgets.QTableWidgetItem()
        self.FileTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.FileTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.FileTable.setHorizontalHeaderItem(2, item)
        self.FileTable.setColumnWidth(0, 40)
        self.FileTable.setColumnWidth(1, 255)
        self.FileTable.setColumnWidth(2, 50)
        self.FileTable.setColumnHidden(3, True)  # 第4列为文件检测状态，隐藏显示
        self.verticalLayout_4.addWidget(self.FileTable)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.delete = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.delete.setEnabled(False)
        self.delete.setObjectName("delete")
        self.horizontalLayout_4.addWidget(self.delete)
        self.horizontalLayout_4.addItem(spacerItem)
        self.redetect = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.redetect.setEnabled(False)
        self.redetect.setObjectName("redetect")
        self.horizontalLayout_4.addWidget(self.redetect)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setAlignment(QtCore.Qt.AlignCenter)
        self.preview = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.preview.setMinimumSize(QtCore.QSize(1280, 720))
        self.preview.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.preview.setText("")
        self.preview.setObjectName("preview")
        self.preview.setAlignment(QtCore.Qt.AlignHCenter)
        self.verticalLayout_3.addWidget(self.preview)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.displayMode = QtWidgets.QComboBox(self.horizontalLayoutWidget)
        self.displayMode.setObjectName("displayMode")
        self.displayMode.addItem("")
        self.displayMode.addItem("")
        self.displayMode.addItem("")
        self.horizontalLayout_3.addWidget(self.displayMode)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.colour = QtWidgets.QComboBox(self.horizontalLayoutWidget)
        self.colour.setMinimumSize(QtCore.QSize(120, 0))
        self.colour.setMaximumSize(QtCore.QSize(120, 16777215))
        self.colour.setObjectName("colour")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon, "")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/black.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon1, "")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/red.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon2, "")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/orange.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon3, "")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("images/yellow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon4, "")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("images/green.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon5, "")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("images/cyan.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon6, "")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("images/blue.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon7, "")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("images/purple.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colour.addItem(icon8, "")
        self.horizontalLayout_3.addWidget(self.colour)
        self.width = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.width.setMinimumSize(QtCore.QSize(40, 0))
        self.width.setMaximumSize(QtCore.QSize(40, 16777215))
        self.width.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.width.setText("")
        self.width.setObjectName("width")
        self.horizontalLayout_3.addWidget(self.width)
        self.label_4 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_5 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.threshold = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.threshold.setMinimumSize(QtCore.QSize(60, 0))
        self.threshold.setMaximumSize(QtCore.QSize(60, 16777215))
        self.threshold.setObjectName("threshold")
        self.horizontalLayout_3.addWidget(self.threshold)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_6 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6)
        self.maxFPS = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.maxFPS.setMinimumSize(QtCore.QSize(40, 0))
        self.maxFPS.setMaximumSize(QtCore.QSize(40, 16777215))
        self.maxFPS.setObjectName("maxFPS")
        self.horizontalLayout_3.addWidget(self.maxFPS)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.start = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.start.setMinimumSize(QtCore.QSize(0, 40))
        self.start.setMaximumSize(QtCore.QSize(170, 40))
        self.start.setObjectName("Start")
        self.horizontalLayout_5.addWidget(self.start)
        self.start.setDisabled(True)
        self.pause = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pause.setMinimumSize(QtCore.QSize(0, 40))
        self.pause.setMaximumSize(QtCore.QSize(170, 40))
        self.pause.setObjectName("Pause")
        self.horizontalLayout_5.addWidget(self.pause)
        self.pause.setDisabled(True)
        self.stop = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.stop.setMinimumSize(QtCore.QSize(0, 40))
        self.stop.setMaximumSize(QtCore.QSize(170, 40))
        self.stop.setObjectName("stop")
        self.horizontalLayout_5.addWidget(self.stop)
        self.stop.setDisabled(True)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.source = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.source.setMinimumSize(QtCore.QSize(0, 60))
        self.source.setMaximumSize(QtCore.QSize(16777215, 60))
        font = QtGui.QFont()
        if width > 2560 and height > 1600:
            font.setPointSize(14)
        else:
            font.setPointSize(11)
        self.source.setFont(font)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("images/instrument.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.source.setIcon(icon9)
        self.source.setObjectName("source")
        self.horizontalLayout.addWidget(self.source)
        self.videos = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.videos.setMinimumSize(QtCore.QSize(0, 60))
        self.videos.setMaximumSize(QtCore.QSize(16777215, 60))
        self.videos.setFont(font)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("images/视频设备.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.videos.setIcon(icon10)
        self.videos.setObjectName("videos")
        self.horizontalLayout.addWidget(self.videos)
        self.images = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.images.setMinimumSize(QtCore.QSize(0, 60))
        self.images.setMaximumSize(QtCore.QSize(16777215, 60))
        self.images.setFont(font)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("images/图片.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.images.setIcon(icon11)
        self.images.setObjectName("images")
        self.horizontalLayout.addWidget(self.images)
        self.export = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.export.setMinimumSize(QtCore.QSize(0, 60))
        self.export.setMaximumSize(QtCore.QSize(16777215, 60))
        self.export.setFont(font)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("images/导出.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.export.setIcon(icon12)
        self.export.setObjectName("export")
        self.horizontalLayout.addWidget(self.export)
        self.export.setDisabled(True)
        self.importModels = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.importModels.setMinimumSize(QtCore.QSize(0, 60))
        self.importModels.setMaximumSize(QtCore.QSize(16777215, 60))
        self.importModels.setFont(font)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap("images/U-Net.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.importModels.setIcon(icon13)
        self.importModels.setObjectName("importModels")
        self.horizontalLayout.addWidget(self.importModels)
        self.trainModels = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.trainModels.setMinimumSize(QtCore.QSize(0, 60))
        self.trainModels.setMaximumSize(QtCore.QSize(16777215, 60))
        self.trainModels.setFont(font)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap("images/模型训练.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.trainModels.setIcon(icon14)
        self.trainModels.setObjectName("trainModels")
        self.horizontalLayout.addWidget(self.trainModels)
        self.verticalLayout.addLayout(self.horizontalLayout)
        Main.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Main)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1569, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuOpen = QtWidgets.QMenu(self.menuFile)
        self.menuOpen.setObjectName("menuOpen")
        self.menuModel = QtWidgets.QMenu(self.menuFile)
        self.menuModel.setObjectName("menuModel")
        self.menuOperate = QtWidgets.QMenu(self.menubar)
        self.menuOperate.setObjectName("menuOperate")
        self.menuSet = QtWidgets.QMenu(self.menubar)
        self.menuSet.setObjectName("menuSet")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setTearOffEnabled(False)
        self.menuHelp.setObjectName("menuHelp")
        Main.setMenuBar(self.menubar)
        self.actionSource = QtWidgets.QAction(Main)
        self.actionSource.setObjectName("actionSource")
        self.actionVideo = QtWidgets.QAction(Main)
        self.actionVideo.setObjectName("actionVideo")
        self.actionImages = QtWidgets.QAction(Main)
        self.actionImages.setObjectName("actionImages")
        self.actionSave_as = QtWidgets.QAction(Main)
        self.actionSave_as.setShortcutVisibleInContextMenu(True)
        self.actionSave_as.setObjectName("actionSave_as")
        self.actionSave_as.setDisabled(True)
        self.actionImport = QtWidgets.QAction(Main)
        self.actionImport.setObjectName("actionImport")
        self.actionTrain = QtWidgets.QAction(Main)
        self.actionTrain.setObjectName("actionTrain")
        self.actionSystemLogs = QtWidgets.QAction(Main)
        self.actionSystemLogs.setObjectName("actionSystemLogs")
        self.actionQuit = QtWidgets.QAction(Main)
        self.actionQuit.setShortcutVisibleInContextMenu(False)
        self.actionQuit.setObjectName("actionQuit")
        self.actionStart = QtWidgets.QAction(Main)
        self.actionStart.setShortcutVisibleInContextMenu(True)
        self.actionStart.setObjectName("actionStart")
        self.actionStart.setDisabled(True)
        self.actionPause = QtWidgets.QAction(Main)
        self.actionPause.setShortcutVisibleInContextMenu(True)
        self.actionPause.setObjectName("actionPause")
        self.actionPause.setDisabled(True)
        self.actionStop = QtWidgets.QAction(Main)
        self.actionStop.setShortcutVisibleInContextMenu(True)
        self.actionStop.setObjectName("actionStop")
        self.actionStop.setDisabled(True)
        self.actionOptions = QtWidgets.QAction(Main)
        self.actionOptions.setObjectName("actionOptions")
        self.actionManual = QtWidgets.QAction(Main)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/User's manual.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionManual.setIcon(icon1)
        self.actionManual.setShortcutVisibleInContextMenu(True)
        self.actionManual.setObjectName("actionManual")
        self.actionFeedback = QtWidgets.QAction(Main)
        self.actionFeedback.setObjectName("actionFeedback")
        self.actionAbout = QtWidgets.QAction(Main)
        self.actionAbout.setObjectName("actionAbout")
        self.menuOpen.addAction(self.actionSource)
        self.menuOpen.addAction(self.actionVideo)
        self.menuOpen.addAction(self.actionImages)
        self.menuModel.addAction(self.actionImport)
        self.menuModel.addAction(self.actionTrain)
        self.menuFile.addAction(self.menuOpen.menuAction())
        self.menuFile.addAction(self.menuModel.menuAction())
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSystemLogs)
        self.menuFile.addAction(self.actionQuit)
        self.menuOperate.addAction(self.actionStart)
        self.menuOperate.addAction(self.actionPause)
        self.menuOperate.addAction(self.actionStop)
        self.menuSet.addAction(self.actionOptions)
        self.menuHelp.addAction(self.actionManual)
        self.menuHelp.addAction(self.actionFeedback)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOperate.menuAction())
        self.menubar.addAction(self.menuSet.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(Main)
        QtCore.QMetaObject.connectSlotsByName(Main)

    def retranslateUi(self, Main):
        _translate = QtCore.QCoreApplication.translate
        Main.setWindowTitle(_translate("Main", "Surgical Navigation System"))
        self.groupBox.setTitle(_translate("Main", "Preview"))
        self.label_13.setText(_translate("Main", "Models"))
        item = self.ModelTable.horizontalHeaderItem(0)
        item.setText(_translate("Main", "Select"))
        item = self.ModelTable.horizontalHeaderItem(1)
        item.setText(_translate("Main", "Name"))
        item = self.ModelTable.horizontalHeaderItem(2)
        item.setText(_translate("Main", "Type"))
        self.label_12.setText(_translate("Main", "Files"))
        item = self.FileTable.horizontalHeaderItem(1)
        item.setText(_translate("Main", "Name"))
        item = self.FileTable.horizontalHeaderItem(2)
        item.setText(_translate("Main", "State"))
        self.delete.setText(_translate("MainWindow", "Delete"))
        self.redetect.setText(_translate("MainWindow", "Redetect"))
        self.label_2.setText(_translate("Main", "Display"))
        self.displayMode.setItemText(0, _translate("Main", "Original"))
        self.displayMode.setItemText(1, _translate("Main", "Mask"))
        self.displayMode.setItemText(2, _translate("Main", "Result"))
        self.label_3.setText(_translate("Main", "Label Pattern"))
        self.colour.setItemText(0, _translate("Main", "White"))
        self.colour.setItemText(1, _translate("Main", "Black"))
        self.colour.setItemText(2, _translate("Main", "Red"))
        self.colour.setItemText(3, _translate("Main", "Orange"))
        self.colour.setItemText(4, _translate("Main", "Yellow"))
        self.colour.setItemText(5, _translate("Main", "Green"))
        self.colour.setItemText(6, _translate("Main", "Cyan"))
        self.colour.setItemText(7, _translate("Main", "Blue"))
        self.colour.setItemText(8, _translate("Main", "Purple"))
        self.label_4.setText(_translate("Main", "px"))
        self.label_5.setText(_translate("Main", "Threshold"))
        self.label_6.setText(_translate("Main", "Max FPS"))
        self.start.setText(_translate("Main", "Start"))
        self.start.setShortcut(_translate("Main", "F5"))
        self.pause.setText(_translate("Main", "Pause / Continue"))
        self.pause.setShortcut(_translate("Main", "P"))
        self.stop.setText(_translate("Main", "Stop"))
        self.stop.setShortcut(_translate("Main", "Esc"))
        self.source.setText(_translate("Main", "Turn on signal source"))
        self.videos.setText(_translate("Main", "Import videos"))
        self.images.setText(_translate("Main", "Import images"))
        self.export.setText(_translate("Main", "Export results"))
        self.importModels.setText(_translate("Main", "Import models"))
        self.trainModels.setText(_translate("Main", "Train models"))
        self.menuFile.setTitle(_translate("Main", "File"))
        self.menuOpen.setTitle(_translate("Main", "Open"))
        self.menuModel.setTitle(_translate("Main", "Model"))
        self.menuOperate.setTitle(_translate("Main", "Operate"))
        self.menuSet.setTitle(_translate("Main", "Setting"))
        self.menuHelp.setTitle(_translate("Main", "Help"))
        self.actionSource.setText(_translate("Main", "Signal source..."))
        self.actionVideo.setText(_translate("Main", "Videos..."))
        self.actionImages.setText(_translate("Main", "Images..."))
        self.actionSave_as.setText(_translate("Main", "Save as..."))
        self.actionSave_as.setShortcut(_translate("Main", "Ctrl+S"))
        self.actionImport.setText(_translate("Main", "Import models..."))
        self.actionTrain.setText(_translate("Main", "Train models..."))
        self.actionSystemLogs.setText(_translate("Main", "System logs"))
        self.actionQuit.setText(_translate("Main", "Quit"))
        self.actionStart.setText(_translate("Main", "Start detection"))
        self.actionStart.setShortcut(_translate("Main", "F5"))
        self.actionPause.setText(_translate("Main", "Pause / Continue"))
        self.actionPause.setShortcut(_translate("Main", "Ctrl+P"))
        self.actionStop.setText(_translate("Main", "Stop"))
        self.actionStop.setShortcut(_translate("Main", "Esc"))
        self.actionOptions.setText(_translate("Main", "Options..."))
        self.actionManual.setText(_translate("Main", "User's manual"))
        self.actionManual.setShortcut(_translate("Main", "F1"))
        self.actionFeedback.setText(_translate("Main", "Feedback..."))
        self.actionAbout.setText(_translate("Main", "About"))


class Dataset(torch.utils.data.Dataset):  # 读取数据集
    def __init__(self, path, transform=None):
        self.img_path = path
        self.transform = transform
        self.files = os.listdir(self.img_path)

    def __getitem__(self, index):
        img = Image.open(self.img_path + self.files[index])
        if self.transform is not None:
            img = self.transform(img)
        return [img, self.img_path + self.files[index]]

    def __len__(self):
        return len(self.files)


class win_Main(QtWidgets.QMainWindow):
    signal_int = pyqtSignal(int)  # 传送数值的信号
    signal_list = pyqtSignal(list)  # 传送列表的信号
    signal_str = pyqtSignal(str)  # 传送字符串的信号
    signal_img = pyqtSignal(np.ndarray)  # 传送图像的信号
    # 传送设置的信号
    signal_opt = pyqtSignal(tuple, bool, bool, int, list, str, str, int, int, str, int, tuple, int, int, str, int, int,
                            str, int, int)
    # 传送视频导出界面的信号，分别对应输出图片列表、视频路径、输出类型、fps、比特率、是否自动开始导出、是否压缩视频
    signal_export = pyqtSignal(list, str, int, int, int, int, int)
    signal_training = pyqtSignal(list, list, list, bool, bool, str, str, str, str)

    def __init__(self, parent=None):
        super(win_Main, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer_video = QtCore.QTimer()  # 创建定时器
        self.init_slots()
        self.cap = cv2.VideoCapture()
        self.stopFlag = 1  # 暂停与播放辅助信号，note：通过奇偶来控制暂停与播放
        self.sourceFlag = False
        self.setAcceptDrops(True)  # 接收drop事件
        self.ui.preview.setScaledContents(True)  # 设置图像自适应界面大小
        self.buttonGroup = QtWidgets.QButtonGroup()
        """初始化"""
        self.modelFiles = []  # 每个元素为一个模型的路径
        self.testFiles = []  # 每个元素为一个视频/图像，其格式为[文件名，类型]，其中类型=0代表视频，类型=1代表图片
        self.processingImg = []  # 用于存放测试集的序号
        self.importType = 0  # 检测源，1为摄像头，2为视频，3为图片
        self.processingRate = 0  # 处理速率，若为0说明处理对象为图片
        self.displayModeChanged = False  # 是否对displayMode做过更改
        self.noLog = False
        self.cb_in_pos_dict = {}  # 用于记录发出信号的comboBox的位置
        self.mask_result = []  # 存储识别得到的掩码，其元素个数等于文件数量
        self.final_result = []  # 存储最终处理结果，其元素个数等于文件数量
        self.files_to_process = []  # 未处理文件的下标
        """用户设定变量"""
        self.ui.width.setText("5")  # 标注线条的宽度
        self.previewSize = (1280, 720)
        self.keepAspectRatio = True
        self.fullScreenPreview = True  # 是否全屏显示preview界面
        self.deviceNum = 0
        self.GPUNum = "0"
        self.logResults = [2, 0, 0]  # 分别对应source, videos, images的是否记录测试结果
        self.priority = 0  # 文件检测优先权，0=视频，1=图片
        self.logPath = os.getcwd().replace('\\', '/')  # 系统日志的默认保存路径
        self.targetPath = os.getcwd().replace('\\', '/') + "/temp/"  # 系统复制文件的目标路径
        self.onlyShowLargest = 1  # 0=Yes, 1=No
        self.autoSetThreshold = 0  # 0=Yes, 1=No
        self.autoSetFPS = 1  # 0=Yes, 1=No
        self.customSize = 0  # 0=Source size, 1=Custom
        self.exportSize = (1280, 720)
        self.autoStart = 1  # 0=Yes, 1=No
        self.customPath = 0  # 0=Source path, 1=Custom
        self.exportPath = ""  # 识别结果默认导出路径
        self.isCompression = 1  # 是否对视频进行压缩，0=Yes, 1=No
        self.bitrate = 0  # 导出视频的比特率
        """训练模型初始设定"""
        self.datasetPartition = ["0.6", "0.2", "0.2"]
        self.hyperParameters = ["0.001", "0.9", "30", "4", "4"]
        self.evaluations = [True, True, True, False, False]
        self.saveEachEpoch = True
        self.logValidationSet = False
        self.pathForModels = os.getcwd().replace('\\', '/') + "/training/models/"
        self.pathForLogs = os.getcwd().replace('\\', '/') + "/training/"

    # 控件绑定相关操作
    def init_slots(self):
        self.ui.displayMode.currentIndexChanged.connect(self.displayMode)
        self.ui.delete.clicked.connect(self.delete)
        self.ui.redetect.clicked.connect(self.redetect)
        self.ui.start.clicked.connect(self.start)
        self.ui.pause.clicked.connect(self.pause)
        self.ui.stop.clicked.connect(self.stop)
        self.ui.source.clicked.connect(self.openSource)
        self.ui.videos.clicked.connect(self.importVideos)
        self.ui.images.clicked.connect(self.importImage)
        self.ui.export.clicked.connect(self.export)
        self.ui.importModels.clicked.connect(self.importModels)
        self.ui.trainModels.clicked.connect(self.trainModels)
        self.ui.FileTable.cellClicked.connect(self.preview)
        self.timer_video.timeout.connect(self.openFrame)
        # 菜单操作
        self.ui.actionSource.triggered.connect(self.openSource)
        self.ui.actionVideo.triggered.connect(self.importVideos)
        self.ui.actionImages.triggered.connect(self.importImage)
        self.ui.actionImport.triggered.connect(self.importModels)
        self.ui.actionTrain.triggered.connect(self.trainModels)
        self.ui.actionSave_as.triggered.connect(self.export)
        self.ui.actionSystemLogs.triggered.connect(self.systemLogs)
        self.ui.actionQuit.triggered.connect(self.quit)
        self.ui.actionStart.triggered.connect(self.start)
        self.ui.actionStop.triggered.connect(self.stop)
        self.ui.actionPause.triggered.connect(self.pause)
        self.ui.actionOptions.triggered.connect(self.setting)
        self.ui.actionManual.triggered.connect(self.manual)
        self.ui.actionFeedback.triggered.connect(self.feedback)
        self.ui.actionAbout.triggered.connect(self.about)

    def generateLog(self, sourceDuration, programDuration, result=0):
        text = "Start time: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))
        text += "End Time: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if self.importType == 1:
            text += "Detection source: signal source\n"
        else:
            text += "Detection source: images or videos\n"
        if result == 0:
            if self.importType == 1:
                text += "Duration of the signal source: %ds" % sourceDuration
            else:
                text += "Number of test files: %d" % len(self.testFiles)
            text += "\nSystem run duration: %ds\n\n" % programDuration
        elif result == 1:
            text += "Detection failed with error code: %s\n\n" % programDuration
        with open(self.logPath + "/syslog.txt", "a") as f:
            f.write(text)
        f.close()

    def imshow(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image = cv2.resize(image, (self.previewSize[0], self.previewSize[1]))
        QtImg = QtGui.QImage(image.data, self.previewSize[0], self.previewSize[1], QtGui.QImage.Format_ARGB32)
        self.ui.preview.setPixmap(QtGui.QPixmap.fromImage(QtImg))

    def predict(self, fileType, size, image=None, index=0):
        """
        预测主函数
        :param size: 输出的图像或视频的大小，若为0则输出大小为源文件大小
        :param fileType: 数据集类型，0代表视频，1代表图片（文件夹）
        :param image: 输入的帧图像，仅用于输入数据集为视频的情况，默认为空
        :param index: 处理的文件编号，仅用于输入数据集为视频的情况，默认为0
        """
        os.environ['CUDA_VISIBLE_DEVICES'] = self.GPUNum
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        threshold = float(self.ui.threshold.text())  # 硬预测的阈值由用户设定

        def getColour():  # 获取标注线条颜色
            colour = self.ui.colour.currentText()
            if colour == "White":
                return (255, 255, 255)
            elif colour == "Black":
                return (0, 0, 0)
            elif colour == "Red":
                return (36, 28, 237)
            elif colour == "Orange":
                return (39, 127, 255)
            elif colour == "Yellow":
                return (0, 242, 255)
            elif colour == "Green":
                return (76, 177, 34)
            elif colour == "Cyan":
                return (232, 162, 0)
            elif colour == "Blue":
                return (204, 72, 63)
            elif colour == "Purple":
                return (164, 73, 163)

        def errorHandle(i):  # 发生错误时的处理
            if i == -1:
                self.ui.preview.clear()
            else:
                self.label1.setAlignment(QtCore.Qt.AlignCenter)
                self.label1.setPixmap(QtGui.QPixmap("images/fail.png").scaled(25, 25))
                self.ui.FileTable.cellWidget(i, 2).clear()
                self.ui.FileTable.setCellWidget(i, 2, self.label1)
                self.ui.FileTable.item(i, 3).setText("1")
                self.ui.redetect.setEnabled(True)
            self.stop(1)  # 参数1代表不生成日志且不释放videoCapture
            self.ui.actionStart.setDisabled(False)
            if len(self.final_result) == 0:
                self.ui.export.setDisabled(True)
                self.ui.actionSave_as.setDisabled(True)

        def updateStatus(i):  # 更改File table中的文件状态
            self.label1.setAlignment(QtCore.Qt.AlignCenter)
            self.label1.setPixmap(QtGui.QPixmap("images/processing.png").scaled(30, 30))
            self.ui.FileTable.cellWidget(i, 2).clear()
            self.ui.FileTable.setCellWidget(i, 2, self.label1)

        def post_process(img1, min_size=100):
            """
            图像后处理过程，包括开运算和去除过小体素
            :return: uint16格式numpy二值数组
            """
            img1 = img1.cpu()
            img1 = img1.numpy().astype(np.bool_)
            b, c, w, h = img1.shape
            if c == 1:
                for i in range(b):
                    img1_tmp = img1[i, 0, :, :]
                    img1_tmp = binary_opening(img1_tmp)
                    remove_small_objects(img1_tmp, min_size=min_size)
                    img1_tmp = ~remove_small_objects(~img1_tmp, min_size=min_size)
                    img1[i, 0, :, :] = img1_tmp
            return img1.astype(np.uint16)

        def connectedArea(label):  # 搜索最大的两个连通区域
            max_index_rec = 0
            for j in range(2):
                label = measure.label(label, connectivity=1)
                props = measure.regionprops(label)
                max_area = 0
                max_index = 0
                # props只包含像素值不为零区域的属性，因此index要从1开始
                for i, prop in enumerate(props, start=1):
                    if prop.area > max_area and i != max_index_rec:
                        max_area = prop.area
                        # index 代表每个联通区域内的像素值；prop.area代表相应连通区域内的像素个数
                        max_index = i
                label[label != max_index] = 0
                label[label == max_index] = 1
                max_index_rec = max_index
                if j == 0:
                    label3 = label
                elif max_index != 0:
                    label += label3
                elif max_index == 0:
                    label = label3
            return label

        def merge(label, img, i, fType):  # 将掩码与原始图像合并，得到最终结果
            canny = cv2.Canny(label, 0, 255)
            width = int(self.ui.width.text())
            kernel = np.ones((width, width), np.uint8)
            canny = cv2.dilate(canny, kernel, iterations=1)
            oriImg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if fType == 0 else img
            oriImg = cv2.resize(oriImg, size)
            result = oriImg
            result[canny == 255] = getColour()
            if not self.noLog:
                self.final_result[i].append(result)
            displayMode = self.ui.displayMode.currentIndex()
            if displayMode == 0:  # Original
                self.imshow(oriImg)
            elif displayMode == 1:  # Mask
                self.imshow(label)
            elif displayMode == 2:
                self.imshow(result)

        if self.ui.ModelTable.cellWidget(self.selectedModel, 2).currentText() == "ResNet50-Unet":  # ResNet50-Unet模型
            self.label1 = QtWidgets.QLabel()
            if self.frame_count == 0:
                Model_path = self.modelFiles[self.selectedModel]
                self.Model = Resnet_Unet(BN_enable=True, resnet_pretrain=False).to(device)
                try:
                    self.Model.load_state_dict(torch.load(Model_path, map_location=torch.device('cpu')))
                except RuntimeError:
                    QMessageBox.warning(self, u"System", u"Please check that the type of model is selected correctly!")
                    if fileType == 1:
                        index = self.processingImg[0]
                    errorHandle(index)
                    return
                except OSError:
                    QMessageBox.warning(self, u"System", u"The model file does not exist, it may have been moved or deleted.")
                    if fileType == 1:
                        index = self.processingImg[0]
                    errorHandle(index)
                    return
                self.Model.eval()
            if fileType == 0:
                startTime = time.time()
                transform = transforms.Compose([
                    transforms.Resize((256, 128)),
                    transforms.ToTensor(),
                ])
                if index >= 0:  # 若index=-1, 则检测源为摄像头，无需更新文件状态
                    updateStatus(index)
                PIL = transforms.ToPILImage()
                PIL_img = PIL(image)
                img = transform(PIL_img)
                img = img.unsqueeze(0)
                img = img.to(device)
                QtCore.QCoreApplication.processEvents()
                with torch.no_grad():
                    predict = self.Model(img)
                    output = torch.ge(predict, threshold).type(dtype=torch.float32)  # 二值化
                    mask = post_process(output)  # 后处理
                    mask = np.reshape(mask, (128, 256))
                    mask = mask[0: 128, 0: 128]
                    if self.onlyShowLargest == 0:
                        mask = connectedArea(mask)
                    mask = cv2.resize(mask.astype("uint8"), size, interpolation=cv2.INTER_CUBIC)
                    if not self.noLog:
                        self.mask_result[index].append(mask)
                    if not self.ui.width.text().isdigit():
                        QMessageBox.warning(self, u"System", u"The width of label line must be a digit!")
                        self.stop()
                        return
                    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    for k in contours:
                        mask = cv2.fillPoly(mask, [k], (255, 255, 255))  # 填充内部
                    merge(mask, image, index, 0)
                if self.autoSetFPS == 0 and self.processingRate == 0:
                    self.processingRate = time.time() - startTime
                    self.ui.maxFPS.setText("%.2f" % (1 / self.processingRate))
                else:
                    self.processingRate = time.time() - startTime
            elif fileType == 1:
                transform = transforms.Compose([
                    transforms.Resize((256, 128)),
                    transforms.ToTensor(),
                ])
                test_set = Dataset(path=self.targetPath, transform=transform)
                test_loader = DataLoader(test_set, batch_size=1, shuffle=False)
                for idx, (img, path) in enumerate(test_loader):
                    oriImage = cv2.imdecode(np.fromfile(path[0], dtype=np.uint8), cv2.IMREAD_COLOR)
                    self.label1 = QtWidgets.QLabel()
                    updateStatus(self.processingImg[idx])
                    if size == 0:
                        size = (oriImage.shape[1], oriImage.shape[0])
                    img = img.to(device)
                    QtCore.QCoreApplication.processEvents()
                    with torch.no_grad():
                        predict = self.Model(img)
                        output = torch.ge(predict, threshold).type(dtype=torch.float32)  # 二值化
                        mask = post_process(output)  # 后处理
                        mask = np.reshape(mask, (128, 256))
                        mask = mask[0: 128, 0: 128]
                        if self.onlyShowLargest:
                            mask = connectedArea(mask)
                        mask = cv2.resize(mask.astype("uint8"), size, interpolation=cv2.INTER_CUBIC)
                        if not self.noLog:
                            self.mask_result[self.processingImg[idx]].append(mask)
                        if not self.ui.width.text().isdigit():
                            QMessageBox.warning(self, u"System", u"The width of label line must be a digit!")
                            self.stop()
                            break
                        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        for k in contours:
                            mask = cv2.fillPoly(mask, [k], (255, 255, 255))  # 填充内部
                        merge(mask, oriImage, self.processingImg[idx], 1)
                        if index >= 0:
                            self.label1.setPixmap(QtGui.QPixmap("images/finish.png").scaled(25, 25))
                            self.ui.FileTable.item(self.processingImg[idx], 3).setText("1")  # 将处理完毕的文件状态改为1
                            self.ui.redetect.setEnabled(True)
        elif self.ui.ModelTable.cellWidget(self.selectedModel, 2).currentText() == "U-net":  # U-net模型
            self.label1 = QtWidgets.QLabel()
            if self.frame_count == 0:
                modelPath = self.modelFiles[self.selectedModel]
                self.Model = Unet(3, 1)
                try:
                    self.Model.load_state_dict(torch.load(modelPath, map_location=torch.device('cpu')))
                except RuntimeError:
                    QMessageBox.warning(self, u"System", u"Please check that the type of model is selected correctly!")
                    if fileType == 1:
                        index = self.processingImg[0]
                    errorHandle(index)
                    return
                except OSError:
                    QMessageBox.warning(self, u"System", u"The model file does not exist, it may have been moved or deleted")
                    if fileType == 1:
                        index = self.processingImg[0]
                    errorHandle(index)
                    return
                self.Model.eval()
            if fileType == 0:  # 视频
                startTime = time.time()
                transform = transforms.Compose([
                    transforms.Resize((256, 128)),
                    transforms.ToTensor(),
                    transforms.Normalize([0.5], [0.5])
                ])
                if index >= 0:  # 若index=-1, 则检测源为摄像头，无需更新文件状态
                    updateStatus(index)
                PIL = transforms.ToPILImage()
                PIL_img = PIL(image)
                img = transform(PIL_img)
                img = img.unsqueeze(0)
                img = img.to(device)
                QtCore.QCoreApplication.processEvents()
                with torch.no_grad():
                    predict = self.Model(img)
                    img_pre = torch.squeeze(predict).numpy()
                    img_pre = img_pre[:, :, np.newaxis]
                    mask = img_pre[:, :, 0]
                    mask = cv2.resize(mask, dsize=size, interpolation=cv2.INTER_CUBIC)
                    _, mask = cv2.threshold(mask, threshold, 1, cv2.THRESH_BINARY)
                    if self.onlyShowLargest == 0:
                        mask = connectedArea(mask)
                    mask = np.uint8(mask * 255)
                    if not self.noLog:
                        self.mask_result[index].append(mask)
                    if not self.ui.width.text().isdigit():
                        QMessageBox.warning(self, u"System", u"The width of label line must be a digit!")
                        self.stop()
                        return
                    merge(mask, image, index, 0)
                if self.autoSetFPS == 0 and self.processingRate == 0:
                    self.processingRate = time.time() - startTime
                    self.ui.maxFPS.setText("%.2f" % (1 / self.processingRate))
                else:
                    self.processingRate = time.time() - startTime
            elif fileType == 1:  # 图片
                transform = transforms.Compose([
                    transforms.Resize((256, 128)),
                    transforms.ToTensor(),
                    transforms.Normalize([0.5], [0.5])
                ])
                test_dataset = Dataset(self.targetPath, transform=transform)
                dataloaders = DataLoader(test_dataset, batch_size=1)
                for idx, (img, path) in enumerate(dataloaders):
                    oriImage = cv2.imdecode(np.fromfile(path[0], dtype=np.uint8), cv2.IMREAD_COLOR)
                    self.label1 = QtWidgets.QLabel()
                    updateStatus(self.processingImg[idx])
                    if size == 0:
                        size = (oriImage.shape[1], oriImage.shape[0])
                    img = img.to(device)
                    QtCore.QCoreApplication.processEvents()
                    with torch.no_grad():
                        predict = self.Model(img)
                        img_pre = torch.squeeze(predict).numpy()
                        img_pre = img_pre[:, :, np.newaxis]
                        mask = img_pre[:, :, 0]
                        mask = cv2.resize(mask.astype("uint8"), dsize=size, interpolation=cv2.INTER_CUBIC)
                        _, mask = cv2.threshold(mask, threshold, 1, cv2.THRESH_BINARY)
                        if self.onlyShowLargest == 0:
                            mask = connectedArea(mask)
                        mask = np.uint8(mask * 255)
                        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
                        self.mask_result[self.processingImg[idx]].append(mask)
                        if not self.ui.width.text().isdigit():
                            QMessageBox.warning(self, u"System", u"The width of label line must be a digit!")
                            self.stop()
                            break
                        merge(mask, oriImage, self.processingImg[idx], 1)
                        if index >= 0:
                            self.label1.setPixmap(QtGui.QPixmap("images/finish.png").scaled(25, 25))
                            self.ui.FileTable.item(self.processingImg[idx], 3).setText("1")  # 将处理完毕的文件状态改为1
                            self.ui.redetect.setEnabled(True)

    def restore(self):  # 检测结束后使界面复原
        if self.fullScreenPreview:
            self.ui.label_12.setHidden(False)
            self.ui.label_13.setHidden(False)
            self.ui.ModelTable.setHidden(False)
            self.ui.FileTable.setHidden(False)
            self.ui.delete.setHidden(False)
            self.ui.redetect.setHidden(False)
            if self.keepAspectRatio:
                width, height = self.previewSize[0], self.previewSize[1]
                self.previewSize = (width - 400, int(height / (width / (width - 400))))
                if not MainWindow.isMaximized():
                    width_Window, height_Window = MainWindow.width(), MainWindow.height() - (height - self.previewSize[1])
                    MainWindow.resize(QtCore.QSize(width_Window, height_Window))
                    self.ui.FileTable.resize(self.ui.FileTable.width(), self.ui.FileTable.height() -
                                             (height - self.previewSize[1]))
                    self.ui.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, width_Window - 20, height_Window - 32))
                    QtWidgets.QApplication.processEvents()
                    self.ui.horizontalLayoutWidget.setGeometry(
                        QtCore.QRect(10, 20, width_Window - 57, height_Window - 115))
            else:
                self.previewSize = (self.previewSize[0] - 400, self.previewSize[1])
            self.ui.preview.resize(QtCore.QSize(self.previewSize[0], self.previewSize[1]))
            QtWidgets.QApplication.processEvents()
            self.ui.verticalLayout_3.layout()
            self.ui.verticalLayout_4.layout()
            self.ui.horizontalLayout_2.layout()

    def openFrame(self):
        if self.importType == 1 and not self.sourceFlag:
            ret, img = self.cap.read()
            self.imshow(img)
            return
        if self.frame_count != 0 and (self.ui.maxFPS.text().isdigit() or re.match(r'^[-+]?[0-9]+\.[0-9]+$', self.ui.maxFPS.text())):
            skip = int(self.fps / float(self.ui.maxFPS.text()))  # 跳跃帧数
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count + skip)
            self.frame_count += skip
        ret, frame = self.cap.read()
        if ret:
            try:
                size = self.exportSize if self.customSize else (frame.shape[1], frame.shape[0])
                # 注意!!!需将图像色彩从RGB转换为BGR后方能预测
                self.predict(0, size, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), self.fileIndex)
                self.frame_count += 1
            except Exception as error:
                traceback.print_exc()
                QMessageBox.warning(self, u"System", u"Detection failed, please copy error code %s and give a feedback "
                                                     u"to the author." % error)
                self.generateLog(0, error, 1)
                self.stop(1)
        else:
            if self.fileIndex >= 0:  # 若检测源为视频，则更新文件状态，并检查是否还有未检测的文件
                self.label1.setPixmap(QtGui.QPixmap("images/finish.png").scaled(25, 25))
                self.ui.FileTable.item(self.fileIndex, 3).setText("1")  # 将处理完毕的文件状态改为1
                self.ui.redetect.setEnabled(True)
                if self.files_to_process:
                    if self.testFiles[self.files_to_process[0]][1] == 0:  # 待处理的文件为视频
                        index = self.files_to_process.pop(0)
                        self.cap.open(self.testFiles[index][0])
                        self.timer_video.start(0)
                        self.fileIndex = index
                        return
                    else:  # 待处理的文件为图片
                        try:
                            size = self.exportSize if self.customSize else 0  # 若输出大小非自定义，则输出大小=原图像大小
                            self.predict(1, size)
                        except Exception as error:
                            traceback.print_exc()
                            QMessageBox.warning(self, u"System", u"Detection failed, please copy error code %s and give"
                                                                 u" a feedback to the author." % error)
                            self.ui.preview.clear()
                            self.generateLog(0, error, 1)  # res参数赋为1时代表检测失败
            self.cap.release()
            self.timer_video.stop()  # 停止计时器
            self.ui.source.setDisabled(False)
            self.ui.actionSource.setDisabled(False)
            self.ui.videos.setDisabled(False)
            self.ui.actionVideo.setDisabled(False)
            self.ui.images.setDisabled(False)
            self.ui.actionImages.setDisabled(False)
            self.ui.pause.setDisabled(True)
            self.ui.stop.setDisabled(True)
            self.ui.actionPause.setDisabled(True)
            self.ui.actionStop.setDisabled(True)
            self.sourceFlag = False
            self.noLog = False
            self.processingRate = 0
            self.frame_count = 0
            self.files_to_process = []
            duarion = np.round(self.frame_count / self.fps) if self.importType == 2 else time.time() - self.start_time
            self.generateLog(duarion, time.time() - self.start_time)
            if os.path.exists(self.targetPath):
                shutil.rmtree(self.targetPath)
            self.restore()

    def openSource(self):
        if self.importType == 1:
            if self.sourceFlag:
                if QMessageBox.question(self, "System", "Turning off the signal source will end the detection, are you "
                                                        "sure to turn it off?",
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.stop()
            else:
                self.ui.source.setText("Turn on signal source")
                self.cap.release()
                self.ui.preview.clear()
                self.timer_video.stop()
                self.importType = 0
        else:
            self.ui.start.setDisabled(False)
            self.ui.actionStart.setDisabled(False)
            self.ui.export.setDisabled(True)
            self.ui.actionSave_as.setDisabled(True)
            self.ui.source.setText("Turn off signal source")
            self.cap.open(self.deviceNum)
            self.importType = 1
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)  # 读取视频的帧速率
            self.timer_video.start(int(round(1000 / self.fps, 0)))

    def importToTable(self, fileType, fileName):  # 将图片或视频导入File Table中
        self.testFiles.append([fileName, fileType])
        rowCount = self.ui.FileTable.rowCount()
        self.ui.FileTable.setRowCount(rowCount + 1)
        self.ui.FileTable.setRowHeight(rowCount, 20)
        checkBox = QtWidgets.QCheckBox()
        all_header_combobox.append(checkBox)  # 将所有的复选框都添加到 全局变量 all_header_combobox 中
        self.ui.FileTable.setCellWidget(rowCount, 0, checkBox)  # 在第一列添加复选框
        if rowCount >= 99:
            self.ui.FileTable.setColumnWidth(1, 210)
        elif rowCount >= 9:
            self.ui.FileTable.setColumnWidth(1, 230)
        icon = "images/video.png" if fileType == 0 else "images/image.png"
        self.ui.FileTable.setItem(rowCount, 1, QtWidgets.QTableWidgetItem(QtGui.QIcon(icon), os.path.basename(fileName)))
        label1 = QtWidgets.QLabel()
        label1.setPixmap(QtGui.QPixmap("images/not started.png").scaled(30, 30))
        label1.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.FileTable.setCellWidget(rowCount, 2, label1)
        self.ui.FileTable.setItem(rowCount, 3, QtWidgets.QTableWidgetItem("0"))
        self.ui.FileTable.resizeRowToContents(rowCount)
        self.mask_result.append([])
        self.final_result.append([])
        self.ui.delete.setDisabled(False)  # 激活删除按钮
        self.ui.start.setDisabled(False)  # 激活开始按钮
        self.ui.actionStart.setDisabled(False)

    def importVideos(self, files=None):
        if not files:
            try:
                files, _ = QFileDialog.getOpenFileNames(self, "Import videos", os.getcwd().replace('\\', '/'),
                                                        "*.mp4;;*.avi;;*.wmv;;*.mov;;*.mkv;;*.flv;;All Files(*)")
            except OSError:
                QMessageBox.warning(self, u"System", 'Error occurred when open files! Verify that the path is correct.')
                return
            if len(files) < 1:
                return
        flag = self.cap.open(files[0])
        if not flag:
            QMessageBox.warning(self, u"System", u"Video import failed.")
        else:
            if self.timer_video.isActive():  # 能获取图片但计时器被打开，说明打开了摄像头
                self.timer_video.stop()
                self.ui.source.setText("Turn on signal source")
            self.ui.export.setDisabled(True)
            self.ui.actionSave_as.setDisabled(True)
            ret, img = self.cap.read()
            self.imshow(img)
            self.importType = 2
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)  # 读取视频的帧速率
            self.frame_num = self.cap.get(7)
            self.duration = self.frame_num / self.fps
            for i in files:
                self.importToTable(0, i)

    def importImage(self, files=None):
        if not files:
            try:
                files, filetype = QFileDialog.getOpenFileNames(self, "Import images", os.getcwd().replace('\\', '/'),
                                                               "*.jpg;;*.png;;*.bmp;;*.tiff;;All Files(*)")
            except OSError:
                QMessageBox.warning(self, u"System", 'Error occurred when open files! Verify that the path is correct.')
                return
            if len(files) < 1:
                return
        if self.timer_video.isActive():
            self.timer_video.stop()
            self.ui.source.setText("Turn on signal source")
        self.ui.export.setDisabled(True)
        self.ui.actionSave_as.setDisabled(True)
        img = cv2.imdecode(np.fromfile(files[0], dtype=np.uint8), cv2.IMREAD_COLOR)
        self.imshow(img)
        self.importType = 3
        for i in files:
            self.importToTable(1, i)

    def importModels(self, files=None):
        if not files:
            try:
                files, filetype = QFileDialog.getOpenFileNames(self, "Import models", os.getcwd().replace('\\', '/'),
                                                               "All Files(*)")
            except OSError:
                QMessageBox.warning(self, u"System", 'Error occurred when open file! Verify that the path is correct.')
                return
            if len(files) < 1:
                return
        for i in files:
            if i[i.rfind("."):] not in ".onnx, .pb, .h5, .keras, .model, .json, .tflite, .prototxt, .pt,.pth, .t7, " \
                                        ".cnTk, .cfg, .weights, .ckpt, .bias, .bin":
                QMessageBox.warning(self, u"System", 'Please upload a correct weight file. If it is do a weight file, '
                                    'change the suffix to .onnx, .pb, .h5, .keras, .model, .json, .tflite, .prototxt, '
                                    '.pt, .pth, .t7, .cnTk, .cfg, .weights, .ckpt, .bias or .bin')
                return
            if i in self.modelFiles:
                QMessageBox.warning(self, u"System", 'The model %s already exists. Please check whether it has been '
                                    'uploaded again. If not, change the file name and upload it again.'
                                    % os.path.basename(i))
                continue
            self.modelFiles.append(i)
            rowCount = self.ui.ModelTable.rowCount()
            self.ui.ModelTable.setRowCount(rowCount + 1)
            widget = QtWidgets.QWidget()
            widget.radioBox = QtWidgets.QRadioButton()  # 将radioBox放在widget中
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(widget.radioBox)  # 为小部件添加radioBox属性
            layout.setAlignment(QtCore.Qt.AlignCenter)  # 设置小控件水平居中
            widget.setLayout(layout)  # 在QWidget放置布局
            self.buttonGroup.addButton(widget.radioBox)
            self.ui.ModelTable.setCellWidget(rowCount, 0, widget)
            self.ui.ModelTable.setItem(rowCount, 1, QtWidgets.QTableWidgetItem(os.path.basename(i)))
            comboBox = QtWidgets.QComboBox()
            """尝试根据文件名判断模型类型，若硬预测阈值为空，则由系统自动填充"""
            if "resnet" in i or "RESNET" in i or "Resnet" in i or "ResNet" in i:
                comboBox.addItem("ResNet50-Unet")
                comboBox.addItem("U-net")
                if self.ui.threshold.text() == "" and self.autoSetThreshold == 0:
                    self.ui.threshold.setText("0.51")
            elif "unet" in i or "u-net" in i or "UNET" in i or "U-Net" in i or "U-NET" in i:
                comboBox.addItem("U-net")
                comboBox.addItem("ResNet50-Unet")
                if self.ui.threshold.text() == "" and self.autoSetThreshold == 0:
                    self.ui.threshold.setText("0.74")
            else:
                comboBox.addItem("ResNet50-Unet")
                comboBox.addItem("U-net")
                if self.ui.threshold.text() == "" and self.autoSetThreshold == 0:
                    self.ui.threshold.setText("0.51")
            self.cb_in_pos_dict[comboBox] = (rowCount, 2)
            self.ui.ModelTable.setCellWidget(rowCount, 2, comboBox)
            self.ui.ModelTable.resizeRowToContents(rowCount)
            # 使comboBox响应点击
            comboBox.currentIndexChanged.connect(self.selectModelType)

    def trainModels(self):
        self.training = win_Training()
        self.training.show()
        self.signal_training.connect(self.training.get_data)
        self.signal_training.emit(self.datasetPartition, self.hyperParameters, self.evaluations, self.saveEachEpoch,
                                  self.logValidationSet, self.pathForModels, self.pathForLogs, self.targetPath,
                                  self.GPUNum)
        self.training.signal_trainModels.connect(self.getData_training)

    def export(self):
        def save(img, folder):
            fileName = os.path.basename(self.testFiles[self.processingImg[i]][0])
            path = folder + "/" + fileName
            if os.path.exists(path):
                if QMessageBox.question(self, "Export results", "The file %s has already existed, would you like to "
                                        "replace it?" % fileName, QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                    return
            cv2.imencode('.jpg', img)[1].tofile(path)

        exportType = 0  # 输出类型, 1代表mask, 2代表label
        if self.ui.displayMode.currentIndex() == 0:
            msg_box = QMessageBox()  # 实例化一个QMessageBox对象
            msg_box.setWindowTitle("Export results")  # 设置对话框的标题
            msg_box.setText("\nWhich form do you want to export?\n")  # 设置对话框的内容
            msg_box.addButton("Mask", QMessageBox.YesRole)
            msg_box.addButton("Label", QMessageBox.YesRole)
            msg_box.addButton("Cancel", QMessageBox.NoRole)
            msg_box.exec()
            if msg_box.clickedButton().text() == "Mask":
                exportType = 1
            elif msg_box.clickedButton().text() == "Label":
                exportType = 2
        elif self.ui.displayMode.currentIndex() == 1:
            exportType = 1
        elif self.ui.displayMode.currentIndex() == 2:
            exportType = 2

        length, direct = len(self.final_result), ""
        if exportType == 1:
            for i in range(length):
                if len(self.mask_result[i]) == 1:  # mask_result的长度为1时，该元素为图片
                    while not os.path.exists(direct):
                        direct = QFileDialog.getExistingDirectory(self, "Select a save path", self.exportPath)
                    save(self.mask_result[i][0], direct)
                else:  # 视频
                    self.win_export = win_Export()
                    self.win_export.show()
                    self.signal_export.connect(self.win_export.get_data)
                    path = self.exportPath + "\\" + os.path.basename(self.testFiles[self.fileIndex][0]) if \
                        self.customPath else self.testFiles[self.fileIndex][0]
                    self.signal_export.emit(self.mask_result[i], path, 1, int(self.fps), self.bitrate,
                                            self.autoStart, self.isCompression)
                    return
        elif exportType == 2:
            for i in range(length):
                if len(self.mask_result[i]) == 1:  # 图片
                    while not os.path.exists(direct):
                        direct = QFileDialog.getExistingDirectory(self, "Select a save path", self.exportPath)
                    save(self.final_result[i][0], direct)
                else:  # 视频
                    self.win_export = win_Export()
                    self.win_export.show()
                    self.signal_export.connect(self.win_export.get_data)
                    path = self.exportPath + "\\" + os.path.basename(self.testFiles[self.fileIndex][0]) if \
                        self.customPath else self.testFiles[self.fileIndex][0]
                    self.signal_export.emit(self.final_result[i], path, 2, int(self.fps), self.bitrate,
                                            self.autoStart, self.isCompression)
                    return
            if os.path.exists(direct):  # 只有文件列表中有图片时才提示成功
                QMessageBox.information(self, u"System", u"Save successfully!")

    def systemLogs(self):
        try:
            os.startfile(self.logPath + "/syslog.txt")
        except:
            QMessageBox.warning(self, u"System", u"Failed to open, the system log does not exist!")

    def displayMode(self):
        self.displayModeChanged = True
        row = self.ui.FileTable.currentRow()
        if row == -1:
            return
        if self.final_result[row]:
            if self.ui.displayMode.currentIndex() == 0:
                self.imshow(cv2.imdecode(np.fromfile(self.testFiles[row][0], dtype=np.uint8), cv2.IMREAD_COLOR))
            elif self.ui.displayMode.currentIndex() == 1:
                self.imshow(self.mask_result[row][0])
            elif self.ui.displayMode.currentIndex() == 2:
                self.imshow(self.final_result[row][0])

    def delete(self):
        deleted = 0
        for i in range(self.ui.FileTable.rowCount()):
            if self.ui.FileTable.cellWidget(i - deleted, 0).checkState():
                self.ui.FileTable.removeRow(i - deleted)
                del all_header_combobox[i - deleted]
                del self.testFiles[i - deleted]
                del self.mask_result[i - deleted]
                del self.final_result[i - deleted]
                deleted += 1
        if deleted == 0:
            QMessageBox.information(self, u"System", 'Please select the files you want to delete.')
        elif self.ui.FileTable.rowCount() == 0:
            self.ui.delete.setEnabled(False)
            self.ui.redetect.setEnabled(False)
            self.ui.start.setEnabled(False)
            self.ui.actionStart.setEnabled(False)

    def redetect(self):
        restarted = 0
        for i in range(self.ui.FileTable.rowCount()):
            if self.ui.FileTable.cellWidget(i, 0).checkState() and self.ui.FileTable.item(i, 3).text() == "1":
                self.mask_result[i] = []  # 将对应的检测结果清空
                self.final_result[i] = []
                label1 = QtWidgets.QLabel()
                label1.setPixmap(QtGui.QPixmap("images/not started.png").scaled(30, 30))
                label1.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.FileTable.cellWidget(i, 2).clear()
                self.ui.FileTable.setCellWidget(i, 2, label1)
                self.ui.FileTable.item(i, 3).setText("0")
                self.ui.start.setEnabled(True)
                self.ui.actionStart.setEnabled(True)
                restarted += 1
        if restarted == 0:
            QMessageBox.information(self, u"System", 'Please select the files that have been detected.')

    def start(self):
        def checkLog(i):  # 根据列表logResults判断是否记录预测结果
            if self.logResults[i] == 2:
                if QMessageBox.question(self, "System",
                                        "Would you like to log and export test results, which likely take up a large "
                                        "amount of memory?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                    self.noLog = True
                else:
                    self.ui.export.setDisabled(False)
                    self.ui.actionSave_as.setDisabled(False)
            elif self.logResults[i] == 1:
                self.noLog = True
            else:
                self.ui.export.setDisabled(False)
                self.ui.actionSave_as.setDisabled(False)

        # 获取选取的模型编号
        self.selectedModel = -1
        for i in range(self.ui.ModelTable.rowCount()):
            if self.ui.ModelTable.cellWidget(i, 0).radioBox.isChecked():
                self.selectedModel = i
        if self.selectedModel == -1:
            QMessageBox.warning(self, u"System", u"You must select a model first!")
            return
        if self.importType == 1:  # 摄像头
            checkLog(0)
            self.sourceFlag = True
            self.fileIndex = -1  # 检测文件的编号，为全局变量，摄像头=1，其余=0
        else:  # 视频或图片
            self.fileIndex = 0
        image = False
        # 开始识别时，关闭检测源按键点击功能，打开操作区按键点击功能
        self.ui.videos.setDisabled(True)
        self.ui.images.setDisabled(True)
        self.ui.source.setDisabled(True)
        self.ui.actionVideo.setDisabled(True)
        self.ui.actionImages.setDisabled(True)
        self.ui.actionSource.setDisabled(True)
        self.ui.start.setDisabled(True)
        self.ui.pause.setDisabled(False)
        self.ui.stop.setDisabled(False)
        self.ui.actionStart.setDisabled(True)
        self.ui.actionPause.setDisabled(False)
        self.ui.actionStop.setDisabled(False)
        self.ui.export.setDisabled(False)
        self.ui.actionSave_as.setDisabled(False)
        self.ui.pause.setText(u'Pause')
        self.start_time = time.time()
        self.frame_count = 0
        if self.fullScreenPreview:  # 复选框Show full screen of preview when detecting被勾选的情况
            self.ui.label_12.setHidden(True)
            self.ui.label_13.setHidden(True)
            self.ui.ModelTable.setHidden(True)
            self.ui.FileTable.setHidden(True)
            self.ui.delete.setHidden(True)
            self.ui.redetect.setHidden(True)
            if self.keepAspectRatio:
                width, height = self.previewSize[0], self.previewSize[1]
                self.previewSize = (width + 400, int(height * (width + 400) / width))
                if not MainWindow.isMaximized():
                    width_Window, height_Window = MainWindow.width(), MainWindow.height() + self.previewSize[1] - height
                    MainWindow.resize(QtCore.QSize(width_Window, height_Window))
                    self.ui.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, width_Window - 20, height_Window - 32))
                    QtWidgets.QApplication.processEvents()
                    self.ui.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, width_Window - 57, height_Window - 115))
            else:
                self.previewSize = (self.previewSize[0] + 400, self.previewSize[1])
            self.ui.preview.resize(QtCore.QSize(self.previewSize[0], self.previewSize[1]))
            QtWidgets.QApplication.processEvents()
            self.ui.verticalLayout_3.layout()
            self.ui.verticalLayout_4.layout()
            self.ui.horizontalLayout_2.layout()
        if self.importType != 1:  # 视频或图片
            self.processingImg = []
            if not self.displayModeChanged:
                self.ui.displayMode.setCurrentIndex(2)
            for index, file in enumerate(self.testFiles):
                if self.ui.FileTable.item(index, 3).text() == "1":
                    continue
                if file[1] == 0:  # 文件为视频
                    if self.priority == 0:  # 优先处理视频
                        checkLog(1)
                        self.cap.open(file[0])
                        self.timer_video.start(0)
                        self.fileIndex = index
                        for i in range(index + 1, len(self.testFiles)):
                            if file[i] == 1:
                                self.files_to_process.append(index)
                        return
                    else:  # 优先处理图片
                        self.files_to_process.append(index)
                else:  # 文件为图片
                    if not image:
                        if not os.path.exists(self.targetPath):
                            os.mkdir(self.targetPath)  # 创建存放测试集的文件夹
                        checkLog(2)
                        image = True
                    if self.priority == 0:  # 优先处理视频
                        self.files_to_process.append(index)
                    if not os.path.exists(self.targetPath + os.path.basename(file[0])):
                        try:
                            shutil.copyfile(file[0], self.targetPath + os.path.basename(file[0]))
                        except Exception:
                            traceback.print_exc()
                            break
                    self.processingImg.append(index)
            try:
                size = self.exportSize if self.customSize else 0  # 若输出大小非自定义，则输出大小=原图像大小
                self.predict(1, size)
            except Exception as error:
                traceback.print_exc()
                QMessageBox.warning(self, u"System", u"Detection failed, please copy error code %s and give a feedback "
                                                     u"to the author." % error)
                self.ui.preview.clear()
                self.generateLog(0, error, 1)  # res参数赋为1时代表检测失败
            if self.files_to_process and self.priority == 1:
                if os.path.exists(self.targetPath):
                    shutil.rmtree(self.targetPath)
                checkLog(1)
                index = self.files_to_process.pop(0)
                self.cap.open(self.testFiles[index][0])
                self.timer_video.start(0)
                self.fileIndex = index
            else:
                self.stop()

    def pause(self):
        # 若QTimer已经触发，且激活
        if self.timer_video.isActive() and self.stopFlag % 2 == 1:
            if self.fileIndex >= 0:
                self.label1.setPixmap(QtGui.QPixmap("images/pause.png").scaled(25, 25))
            self.ui.pause.setText(u'Continue')  # 当前状态为暂停状态
            self.stopFlag = self.stopFlag + 1  # 调整标记信号为偶数
            self.timer_video.blockSignals(True)
        # 继续检测
        else:
            self.stopFlag = self.stopFlag - 1
            self.ui.pause.setText(u'Pause')
            self.timer_video.blockSignals(False)

    def stop(self, flag=0):
        """
        结束检测。
        :param flag: 0代表正常停止，1通常为因意外而停止的情况，因而保留video_capture, preview以及start按钮
        """
        self.timer_video.stop()  # 停止计时器
        # 启动其他检测按键功能
        self.ui.videos.setDisabled(False)
        self.ui.images.setDisabled(False)
        self.ui.source.setDisabled(False)
        self.ui.actionVideo.setDisabled(False)
        self.ui.actionImages.setDisabled(False)
        self.ui.actionSource.setDisabled(False)
        self.ui.pause.setDisabled(True)
        self.ui.stop.setDisabled(True)
        self.ui.actionPause.setDisabled(True)
        self.ui.actionStop.setDisabled(True)
        self.frame_count = 0
        self.processingRate = 0
        self.sourceFlag = False
        self.noLog = False
        self.files_to_process = []
        self.ui.source.setText("Turn on signal source")
        # 结束检测时，将暂停功能恢复至初始状态。若处于暂停状态，需要调整stopFlag并关闭计时器的阻塞信号
        self.ui.pause.setText(u'Pause / continue')
        if self.stopFlag % 2 == 0:
            self.stopFlag = self.stopFlag + 1
            self.timer_video.blockSignals(False)
        duarion = np.round(self.frame_count / self.fps) if self.importType == 1 else 0
        if os.path.exists(self.targetPath):
            shutil.rmtree(self.targetPath)
        if not flag:
            if self.fileIndex >= 0:
                self.label1.setPixmap(QtGui.QPixmap("images/finish.png").scaled(25, 25))  # 更新文件状态
                self.ui.FileTable.item(self.fileIndex, 3).setText("1")  # 将处理完毕的文件状态改为1
                self.ui.redetect.setEnabled(True)
            else:
                self.ui.preview.clear()  # 清空preview区
            self.cap.release()  # 释放video_capture资源
            self.importType = 0
            self.generateLog(duarion, time.time() - self.start_time)
        else:
            self.ui.start.setDisabled(False)
            self.ui.actionStart.setDisabled(False)
        self.restore()

    def preview(self, row, col):  # 预览图片/视频
        if col == 1:
            if self.final_result[row]:
                if self.ui.displayMode.currentIndex() == 0:
                    self.imshow(cv2.imdecode(np.fromfile(self.testFiles[row][0], dtype=np.uint8), cv2.IMREAD_COLOR))
                elif self.ui.displayMode.currentIndex() == 1:
                    self.imshow(self.mask_result[row][0])
                elif self.ui.displayMode.currentIndex() == 2:
                    self.imshow(self.final_result[row][0])
            else:
                if self.testFiles[row][1] == 0:  # 视频
                    self.cap.open(self.testFiles[row][0])
                    ret, img = self.cap.read()
                    self.imshow(img)
                elif self.testFiles[row][1] == 1:  # 图片
                    self.imshow(cv2.imdecode(np.fromfile(self.testFiles[row][0], dtype=np.uint8), cv2.IMREAD_COLOR))

    def quit(self):
        if QMessageBox.question(self, "System", "Are you sure you want to quit the program?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.cap.release()
            sys.exit(app.exec_())

    def setting(self):
        self.options = win_Options()
        self.options.show()
        recommendedFPS = "%.2f" % (1 / self.processingRate) if self.processingRate != 0 else ""  # 推荐最大FPS
        self.signal_opt.connect(self.options.get_data)
        self.signal_opt.emit(self.previewSize, self.keepAspectRatio, self.fullScreenPreview, self.deviceNum,
                             self.logResults, self.logPath, self.targetPath, self.autoSetThreshold, self.autoSetFPS,
                             recommendedFPS, self.customSize, self.exportSize, self.autoStart, self.customPath,
                             self.exportPath, self.isCompression, self.bitrate, self.GPUNum, self.priority,
                             self.onlyShowLargest)
        self.options.signal_options.connect(self.getData_options)

    def manual(self):
        self.win_manual = win_Manual()
        self.win_manual.show()

    def feedback(self):
        self.win_feedback = win_Feedback()
        self.win_feedback.show()

    def about(self):
        self.win_about = win_About()
        self.win_about.show()

    def selectModelType(self):
        index = self.cb_in_pos_dict[self.sender()]  # 记录发出信号的comboBox的位置，即self.sender()
        self.ui.ModelTable.cellChanged.emit(*index)  # 将信号发送给ModelTable令其修改

    def markFile(self):
        if not self.timer_video.isActive():  # 若没有激活计时器且选中文件，则启动开始功能
            self.ui.start.setDisabled(False)
            self.ui.actionStart.setDisabled(False)

    def closeEvent(self, event):  # 函数名固定不可变
        if QMessageBox.question(self, "Quit", "Are you sure you want to quit the program?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.cap.release()
        else:
            event.ignore()

    def getData_training(self, data1, data2, data3, data4, data5, data6, data7):
        self.datasetPartition, self.hyperParameters, self.evaluations, self.saveEachEpoch, self.logValidationSet, \
            self.pathForModels, self.pathForLogs = data1, data2, data3, data4, data5, data6, data7

    def getData_options(self, data1, data2, data3, data4, data5, data6, data7, data8, data9, data10, data11, data12, data13, data14, data15, data16, data17, data18, data19, data20):
        preSizeW, preSizeH = self.previewSize[0], self.previewSize[1]
        winSizeW, winSizeH = MainWindow.size().width(), MainWindow.size().height()
        self.previewSize, self.keepAspectRatio, self.fullScreenPreview, self.deviceNum, self.logResults, self.logPath, \
            self.targetPath, self.autoSetThreshold, self.autoSetFPS, temp, self.customSize, self.exportSize, \
            self.autoStart,  self.customPath, self.exportPath, self.isCompression, self.bitrate, self.GPUNum, \
            self.priority, self.onlyShowLargest = data1, data2, data3, data4, data5, data6, data7, data8, data9, \
            data10, data11, data12, data13, data14, data15, data16, data17, data18, data19, data20
        """根据设置的preview大小调整窗口大小"""
        if data1 != (preSizeW, preSizeH):
            newSizeW, newSizeH = data1[0], data1[1]
            if newSizeW <= 1280:
                winSizeW = 1600
            else:
                winSizeW += newSizeW - preSizeW
            if newSizeH <= 720:
                winSizeH = 913
            else:
                winSizeH += newSizeH - preSizeH
            if not MainWindow.isMaximized():  # 若窗口不是最大化，则对窗口进行调整
                MainWindow.resize(QtCore.QSize(winSizeW, winSizeH))
            self.ui.preview.setMinimumSize(QtCore.QSize(0, 0))
            self.ui.preview.resize(QtCore.QSize(newSizeW, newSizeH))
            self.ui.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, winSizeW - 20, winSizeH - 32))
            QtWidgets.QApplication.processEvents()
            self.ui.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, winSizeW - 57, winSizeH - 115))
            QtWidgets.QApplication.processEvents()
            self.ui.verticalLayout_3.layout()
            self.ui.verticalLayout_4.layout()
            self.ui.horizontalLayout_2.layout()

    def dragEnterEvent(self, QDragEnterEvent):
        if QDragEnterEvent.mimeData().hasText():
            QDragEnterEvent.acceptProposedAction()

    def dragMoveEvent(self, event):
        mtRect, ftRect = self.ui.ModelTable.rect(), self.ui.FileTable.rect()
        if QtCore.QRect(20, 75, mtRect.width(), mtRect.height()).contains(event.pos()) or \
                QtCore.QRect(20, 120 + mtRect.height(), ftRect.width(), ftRect.height()).contains(event.pos()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        filePath = event.mimeData().text().replace('file:///', '')
        if "\n" in filePath:
            filePath = filePath.split("\n")
            filePath.remove('')
        else:
            filePath = [filePath]
        mtRect, ftRect = self.ui.ModelTable.rect(), self.ui.FileTable.rect()
        if QtCore.QRect(20, 75, mtRect.width(), mtRect.height()).contains(event.pos()):
            ls = []
            for i in filePath:
                if i[i.rfind("."):] in ".onnx, .pb, .h5, .keras, .model, .json, .tflite, .prototxt, .pt,.pth,"\
                                                     " .t7, .cnTk, .cfg, .weights, .ckpt, .bias, .bin":
                    ls.append(i)
            if ls:
                self.importModels(ls)
        elif QtCore.QRect(20, 120 + mtRect.height(), ftRect.width(), ftRect.height()).contains(event.pos()):
            videos, images = [], []
            for i in filePath:
                if i[i.rfind("."):] in "*.mp4;;*.avi;;*.wmv;;*.mov;;*.mkv;;*.flv":
                    videos.append(i)
                elif i[i.rfind("."):] in "*.jpg;;*.png;;*.bmp;;*.tiff":
                    images.append(i)
            if images:
                self.importImage(images)
            if videos:
                self.importVideos(videos)
        else:
            event.ignore()


if __name__ == '__main__':
    font = QtGui.QFont()
    font.setFamily("Times New Roman")
    width, height = pyautogui.size()
    if width > 2560 and height > 1600:  # 如果屏幕分辨率大于2560×1600，则自动放大系统分辨率
        QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
        font.setPointSize(12)
    else:
        font.setPointSize(10)
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(font)
    MainWindow = win_Main()
    MainWindow.show()
    sys.exit(app.exec_())
