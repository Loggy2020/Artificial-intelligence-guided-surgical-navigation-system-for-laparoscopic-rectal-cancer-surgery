from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from model import Resnet_Unet, Unet
from skimage.morphology import remove_small_objects, binary_opening
from PIL import Image, ImageDraw
import math
import numpy as np
import random
import time
import sys
import os, shutil
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
import traceback
import json
all_header_combobox, all_header_combobox2 = [], []  # 用来装行表头所有复选框 全局变量


class CheckBoxHeader(QtWidgets.QHeaderView):
    """自定义表头类"""
    select_all_clicked = pyqtSignal(bool)  # 自定义复选框全选信号
    # 这4个变量控制列头复选框的样式，位置以及大小
    _x_offset, _y_offset, _width, _height = 5, 0, 20, 20

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

    def change_state2(self, isOn):
        if isOn:
            for i in all_header_combobox2:
                i.setCheckState(QtCore.Qt.Checked)
        else:
            for i in all_header_combobox2:
                i.setCheckState(QtCore.Qt.Unchecked)


class Ui_Training(object):
    def setupUi(self, Training):
        Training.setObjectName("Train models")
        Training.resize(1700, 938)
        self.centralwidget = QtWidgets.QWidget(Training)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 1681, 921))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.title.setMinimumSize(QtCore.QSize(0, 50))
        self.title.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.tableWidget = QtWidgets.QTableWidget(self.verticalLayoutWidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        header = CheckBoxHeader()
        self.tableWidget.setHorizontalHeader(header)
        header.select_all_clicked.connect(header.change_state)  # 行表头复选框单击信号与槽
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.setColumnWidth(0, 35)
        self.tableWidget.setColumnWidth(1, 75)
        self.tableWidget.setColumnWidth(2, 140)
        self.tableWidget.setColumnWidth(3, 124)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.importOrigin = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.importOrigin.setFont(font)
        self.importOrigin.setObjectName("importOrigin")
        self.horizontalLayout_4.addWidget(self.importOrigin)
        self.deleteOrigin = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.deleteOrigin.setFont(font)
        self.deleteOrigin.setObjectName("deleteOrigin")
        self.deleteOrigin.setEnabled(False)
        self.horizontalLayout_4.addWidget(self.deleteOrigin)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.tableWidget_2 = QtWidgets.QTableWidget(self.verticalLayoutWidget)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(4)
        self.tableWidget_2.setRowCount(0)
        header2 = CheckBoxHeader()
        self.tableWidget_2.setHorizontalHeader(header2)
        header2.select_all_clicked.connect(header2.change_state2)  # 行表头复选框单击信号与槽
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, item)
        self.tableWidget_2.setColumnWidth(0, 35)
        self.tableWidget_2.setColumnWidth(1, 75)
        self.tableWidget_2.setColumnWidth(2, 140)
        self.tableWidget_2.setColumnWidth(3, 124)
        self.verticalLayout_3.addWidget(self.tableWidget_2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem2)
        self.importMask = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.importMask.setFont(font)
        self.importMask.setObjectName("importMask")
        self.horizontalLayout_7.addWidget(self.importMask)
        self.deleteMask = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.deleteMask.setFont(font)
        self.deleteMask.setObjectName("deleteMask")
        self.deleteMask.setEnabled(False)
        self.horizontalLayout_7.addWidget(self.deleteMask)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        spacerItem4 = QtWidgets.QSpacerItem(13, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_5.addWidget(self.label_4)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSpacing(10)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setMinimumSize(QtCore.QSize(100, 0))
        self.label_3.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.modelType = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.modelType.setMinimumSize(QtCore.QSize(90, 0))
        self.modelType.setFont(font)
        self.modelType.setObjectName("comboBox")
        self.modelType.addItem("")
        self.modelType.addItem("")
        self.horizontalLayout_6.addWidget(self.modelType)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem5)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem6)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSpacing(10)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_5.setMinimumSize(QtCore.QSize(100, 0))
        self.label_5.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_8.addWidget(self.label_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_6 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_9.addWidget(self.label_6)
        self.trainingSize = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.trainingSize.setFont(font)
        self.trainingSize.setText("")
        self.trainingSize.setObjectName("trainingSize")
        self.horizontalLayout_9.addWidget(self.trainingSize)
        self.trainingProportion = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.trainingProportion.setMaximumSize(QtCore.QSize(100, 16777215))
        self.trainingProportion.setFont(font)
        self.trainingProportion.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.trainingProportion.setObjectName("trainingProportion")
        self.horizontalLayout_9.addWidget(self.trainingProportion)
        self.verticalLayout_6.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_10.addWidget(self.label_7)
        self.validationSize = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.validationSize.setFont(font)
        self.validationSize.setText("")
        self.validationSize.setObjectName("validationSize")
        self.horizontalLayout_10.addWidget(self.validationSize)
        self.validationProportion = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.validationProportion.setMaximumSize(QtCore.QSize(100, 16777215))
        self.validationProportion.setFont(font)
        self.validationProportion.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.validationProportion.setObjectName("validationProportion")
        self.horizontalLayout_10.addWidget(self.validationProportion)
        self.verticalLayout_6.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_8 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_11.addWidget(self.label_8)
        self.predictionSize = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.predictionSize.setFont(font)
        self.predictionSize.setText("")
        self.predictionSize.setObjectName("predictionSize")
        self.horizontalLayout_11.addWidget(self.predictionSize)
        self.predictionProportion = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.predictionProportion.setMaximumSize(QtCore.QSize(100, 16777215))
        self.predictionProportion.setFont(font)
        self.predictionProportion.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.predictionProportion.setObjectName("predictionProportion")
        self.horizontalLayout_11.addWidget(self.predictionProportion)
        self.verticalLayout_6.addLayout(self.horizontalLayout_11)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_6.addLayout(self.horizontalLayout)
        self.horizontalLayout_8.addLayout(self.verticalLayout_6)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem7)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.sequentiallyDistribute = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.sequentiallyDistribute.setFont(font)
        self.sequentiallyDistribute.setObjectName("sequentiallyDistribute")
        self.verticalLayout_4.addWidget(self.sequentiallyDistribute)
        self.randomlyDistribute = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.randomlyDistribute.setFont(font)
        self.randomlyDistribute.setObjectName("randomlyDistribute")
        self.verticalLayout_4.addWidget(self.randomlyDistribute)
        self.horizontalLayout_8.addLayout(self.verticalLayout_4)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem8)
        self.verticalLayout_5.addLayout(self.horizontalLayout_8)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem9)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_9 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_9.setMinimumSize(QtCore.QSize(100, 0))
        self.label_9.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_2.addWidget(self.label_9)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_10 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_12.addWidget(self.label_10)
        self.learning_rate = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.learning_rate.setMaximumSize(QtCore.QSize(100, 16777215))
        self.learning_rate.setFont(font)
        self.learning_rate.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.learning_rate.setObjectName("learning_rate")
        self.horizontalLayout_12.addWidget(self.learning_rate)
        self.label_17 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_17.setMaximumSize(20, 16777215)
        font.setPointSize(16)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_12.addWidget(self.label_17)
        self.learning_rate_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.learning_rate_2.setMaximumSize(QtCore.QSize(60, 16777215))
        font.setPointSize(11)
        self.learning_rate_2.setFont(font)
        self.learning_rate_2.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.learning_rate_2.setObjectName("learning_rate_2")
        self.horizontalLayout_12.addWidget(self.learning_rate_2)
        self.label_18 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_12.addWidget(self.label_18)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem10)
        self.verticalLayout_7.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_11 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_13.addWidget(self.label_11)
        self.epochs = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.epochs.setMaximumSize(QtCore.QSize(100, 16777215))
        self.epochs.setFont(font)
        self.epochs.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.epochs.setObjectName("epochs")
        self.horizontalLayout_13.addWidget(self.epochs)
        spacerItem11 = QtWidgets.QSpacerItem(350, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem11)
        self.verticalLayout_7.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_12 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_14.addWidget(self.label_12)
        self.training_batch_size = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.training_batch_size.setMaximumSize(QtCore.QSize(100, 16777215))
        self.training_batch_size.setFont(font)
        self.training_batch_size.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.training_batch_size.setObjectName("training_batch_size")
        self.horizontalLayout_14.addWidget(self.training_batch_size)
        spacerItem12 = QtWidgets.QSpacerItem(350, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem12)
        self.verticalLayout_7.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_13 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_15.addWidget(self.label_13)
        self.validation_batch_size = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.validation_batch_size.setMaximumSize(QtCore.QSize(100, 16777215))
        self.validation_batch_size.setFont(font)
        self.validation_batch_size.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.validation_batch_size.setObjectName("validation_batch_size")
        self.horizontalLayout_15.addWidget(self.validation_batch_size)
        spacerItem13 = QtWidgets.QSpacerItem(350, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem13)
        self.verticalLayout_7.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pretrain = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.pretrain.setFont(font)
        self.pretrain.setObjectName("pretrain")
        self.horizontalLayout_5.addWidget(self.pretrain)
        self.label_14 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_5.addWidget(self.label_14)
        self.pretrainPath = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.pretrainPath.setEnabled(False)
        self.pretrainPath.setFont(font)
        self.pretrainPath.setObjectName("pretrainPath")
        self.horizontalLayout_5.addWidget(self.pretrainPath)
        self.browse1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.browse1.setEnabled(False)
        self.browse1.setFont(font)
        self.browse1.setObjectName("browse1")
        self.horizontalLayout_5.addWidget(self.browse1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2.addLayout(self.verticalLayout_7)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        spacerItem14 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem14)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setSpacing(10)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_15 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_15.setMinimumSize(QtCore.QSize(100, 0))
        self.label_15.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_15.setFont(font)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_16.addWidget(self.label_15)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.checkBox_DSC = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.checkBox_DSC.setFont(font)
        self.checkBox_DSC.setObjectName("checkBox_DSC")
        self.horizontalLayout_17.addWidget(self.checkBox_DSC)
        self.checkBox_PPV = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.checkBox_PPV.setFont(font)
        self.checkBox_PPV.setObjectName("checkBox_PPV")
        self.horizontalLayout_17.addWidget(self.checkBox_PPV)
        self.checkBox_NPV = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.checkBox_NPV.setFont(font)
        self.checkBox_NPV.setObjectName("checkBox_NPV")
        self.horizontalLayout_17.addWidget(self.checkBox_NPV)
        self.verticalLayout_8.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.checkBox_SEN = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.checkBox_SEN.setFont(font)
        self.checkBox_SEN.setObjectName("checkBox_SEN")
        self.horizontalLayout_18.addWidget(self.checkBox_SEN)
        self.checkBox_SPE = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.checkBox_SPE.setFont(font)
        self.checkBox_SPE.setObjectName("checkBox_SPE")
        self.horizontalLayout_18.addWidget(self.checkBox_SPE)
        spacerItem17 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_18.addItem(spacerItem17)
        self.verticalLayout_8.addLayout(self.horizontalLayout_18)
        self.horizontalLayout_16.addLayout(self.verticalLayout_8)
        self.verticalLayout_5.addLayout(self.horizontalLayout_16)
        spacerItem18 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem18)
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_20.setSpacing(10)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.label_16 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_16.setMinimumSize(QtCore.QSize(100, 0))
        self.label_16.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_16.setFont(font)
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_20.addWidget(self.label_16)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.save_each_epoch = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.save_each_epoch.setFont(font)
        self.save_each_epoch.setObjectName("save_each_epoch")
        self.verticalLayout_9.addWidget(self.save_each_epoch)
        self.log_validation_set = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.log_validation_set.setFont(font)
        self.log_validation_set.setObjectName("log_validation_set")
        self.verticalLayout_9.addWidget(self.log_validation_set)
        self.horizontalLayout_26 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_26.setObjectName("horizontalLayout_26")
        self.label_22 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.horizontalLayout_26.addWidget(self.label_22)
        self.savePathForModels = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.savePathForModels.setEnabled(True)
        self.savePathForModels.setFont(font)
        self.savePathForModels.setObjectName("savePathForModels")
        self.horizontalLayout_26.addWidget(self.savePathForModels)
        self.browse2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.browse2.setEnabled(True)
        self.browse2.setFont(font)
        self.browse2.setObjectName("browse2")
        self.horizontalLayout_26.addWidget(self.browse2)
        self.verticalLayout_9.addLayout(self.horizontalLayout_26)
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.label_25 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_25.setFont(font)
        self.label_25.setObjectName("label_25")
        self.horizontalLayout_29.addWidget(self.label_25)
        self.savePathForLogs = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.savePathForLogs.setEnabled(True)
        self.savePathForLogs.setFont(font)
        self.savePathForLogs.setObjectName("savePathForLogs")
        self.horizontalLayout_29.addWidget(self.savePathForLogs)
        self.browse3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.browse3.setEnabled(True)
        self.browse3.setFont(font)
        self.browse3.setObjectName("browse3")
        self.horizontalLayout_29.addWidget(self.browse3)
        self.verticalLayout_9.addLayout(self.horizontalLayout_29)
        self.horizontalLayout_20.addLayout(self.verticalLayout_9)
        self.verticalLayout_5.addLayout(self.horizontalLayout_20)
        spacerItem19 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem19)
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.start = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.start.setMaximumSize(QtCore.QSize(120, 16777215))
        self.start.setFont(font)
        self.start.setObjectName("start")
        self.horizontalLayout_19.addWidget(self.start)
        self.start.setEnabled(False)
        self.stop = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.stop.setMaximumSize(QtCore.QSize(120, 16777215))
        self.stop.setFont(font)
        self.stop.setObjectName("stop")
        self.horizontalLayout_19.addWidget(self.stop)
        self.stop.setEnabled(False)
        self.reset = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.reset.setMaximumSize(QtCore.QSize(120, 16777215))
        self.reset.setFont(font)
        self.reset.setObjectName("reset")
        self.horizontalLayout_19.addWidget(self.reset)
        self.verticalLayout_5.addLayout(self.horizontalLayout_19)
        self.horizontalLayout_3.addLayout(self.verticalLayout_5)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_33.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_33.setObjectName("horizontalLayout_33")
        self.text_elapsed = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.text_elapsed.setFont(font)
        self.text_elapsed.setObjectName("text_elapsed")
        self.text_elapsed.setHidden(True)
        self.horizontalLayout_33.addWidget(self.text_elapsed)
        self.text_remaining = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.text_remaining.setFont(font)
        self.text_remaining.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.text_remaining.setObjectName("text_remaining")
        self.text_remaining.setHidden(True)
        self.horizontalLayout_33.addWidget(self.text_remaining)
        self.verticalLayout_13.addLayout(self.horizontalLayout_33)
        self.verticalLayout.addLayout(self.verticalLayout_13)
        self.progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setMaximum(1000)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setHidden(True)
        self.verticalLayout.addWidget(self.progressBar)
        self.text_status = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.text_status.setFont(font)
        self.text_status.setText("")
        self.text_status.setObjectName("text_status")
        self.text_status.setHidden(True)
        self.verticalLayout.addWidget(self.text_status)
        Training.setCentralWidget(self.centralwidget)

        self.retranslateUi(Training)
        QtCore.QMetaObject.connectSlotsByName(Training)

    def retranslateUi(self, Training):
        _translate = QtCore.QCoreApplication.translate
        Training.setWindowTitle(_translate("Training", "Train models"))
        self.title.setText(_translate("Training", "Train models"))
        self.label.setText(_translate("Training", "Original images"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Training", "Image"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Training", "Name"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Training", "Data set"))
        self.importOrigin.setText(_translate("Training", "Import"))
        self.deleteOrigin.setText(_translate("Training", "Delete"))
        self.label_2.setText(_translate("Training", "Mask images"))
        item = self.tableWidget_2.horizontalHeaderItem(1)
        item.setText(_translate("Training", "Image"))
        item = self.tableWidget_2.horizontalHeaderItem(2)
        item.setText(_translate("Training", "Name"))
        item = self.tableWidget_2.horizontalHeaderItem(3)
        item.setText(_translate("Training", "Data set"))
        self.importMask.setText(_translate("Training", "Import"))
        self.deleteMask.setText(_translate("Training", "Delete"))
        self.label_4.setText(_translate("Training", "Preferences"))
        self.label_3.setText(_translate("Training", "Model type"))
        self.modelType.setItemText(0, _translate("Training", "ResNet50-Unet"))
        self.modelType.setItemText(1, _translate("Training", "U-net"))
        self.label_5.setText(_translate("Training", "Partition"))
        self.label_6.setText(_translate("Training", "Training set"))
        self.label_7.setText(_translate("Training", "Validation set"))
        self.label_8.setText(_translate("Training", "Prediction set"))
        self.sequentiallyDistribute.setText(_translate("Training", "Sequentially distribute"))
        self.randomlyDistribute.setText(_translate("Training", "Randomly distribute"))
        self.label_9.setText(_translate("Training", "Hyper\nparameters"))
        self.label_10.setText(_translate("Training", "Learning rate"))
        self.label_17.setText(_translate("Training", "×"))
        self.label_18.setText(_translate("Training", "each epoch"))
        self.label_11.setText(_translate("Training", "Epochs"))
        self.label_12.setText(_translate("Training", "Training batch size"))
        self.label_13.setText(_translate("Training", "Validation batch size"))
        self.pretrain.setText(_translate("Training", "Pretrain"))
        self.label_14.setText(_translate("Training", "Model path"))
        self.browse1.setText(_translate("Training", "Browse"))
        self.label_15.setText(_translate("Training", "Evaluation\nindexes"))
        self.checkBox_DSC.setText(_translate("Training", "Dice score"))
        self.checkBox_PPV.setText(_translate("Training", "Positive predictive value"))
        self.checkBox_NPV.setText(_translate("Training", "Negative predictive value"))
        self.checkBox_SEN.setText(_translate("Training", "Sensitivity "))
        self.checkBox_SPE.setText(_translate("Training", "Specificity"))
        self.label_16.setText(_translate("Training", "Save"))
        self.save_each_epoch.setText(_translate("Training", "Save a model for each epoch"))
        self.log_validation_set.setText(_translate("Training", "Log evaluation indexes of the validation set"))
        self.label_22.setText(_translate("Training", "Path for models"))
        self.browse2.setText(_translate("Training", "Browse"))
        self.label_25.setText(_translate("Training", "Path for logs"))
        self.browse3.setText(_translate("Training", "Browse"))
        self.start.setText(_translate("Training", "Start"))
        self.stop.setText(_translate("Training", "Stop"))
        self.reset.setText(_translate("Training", "Reset"))
        self.text_elapsed.setText(_translate("Training", "Elapsed:00:00:00"))
        self.text_remaining.setText(_translate("Training", "Remaining:--:--:--"))


class Dataset(torch.utils.data.Dataset):  # 读取数据集
    def __init__(self, path, transform=None):
        self.img_path = path + "case/"
        self.mask_path = path + "mask/"
        self.transform = transform
        self.imgFiles = os.listdir(self.img_path)
        self.maskFiles = os.listdir(self.mask_path)

    def __getitem__(self, index):
        img = Image.open(self.img_path + self.imgFiles[index])
        mask = Image.open(self.mask_path + self.maskFiles[index])
        mask = mask.convert("L")
        if self.transform is not None:
            img = self.transform(img)
            mask = self.transform(mask)
        return [img, mask]

    def __len__(self):
        return len(self.imgFiles)


class win_Training(QtWidgets.QMainWindow):
    signal_trainModels = pyqtSignal(list, list, list, bool, bool, str, str)

    def __init__(self, parent=None):
        super(win_Training, self).__init__(parent)
        self.ui = Ui_Training()
        self.ui.setupUi(self)
        self.timer_video = QtCore.QTimer()  # 创建定时器
        self.init_slots()
        self.setAcceptDrops(True)  # 接收drop事件
        self.originImages = []  # 原始图片路径列表
        self.maskImages = []  # 掩模图片路径列表
        self.distributed = False  # 是否分配数据集
        self.cb_in_tw_dict, self.cb_in_tw_dict2 = {}, {}  # 用于记录发出信号的comboBox的位置

    def init_slots(self):
        self.ui.importOrigin.clicked.connect(self.importOrigin)
        self.ui.deleteOrigin.clicked.connect(self.deleteOrigin)
        self.ui.importMask.clicked.connect(self.importMask)
        self.ui.deleteMask.clicked.connect(self.deleteMask)
        self.ui.sequentiallyDistribute.clicked.connect(self.distribute1)
        self.ui.randomlyDistribute.clicked.connect(self.distribute2)
        self.ui.pretrain.clicked.connect(self.isPretrain)
        self.ui.browse1.clicked.connect(self.browse1)
        self.ui.browse2.clicked.connect(self.browse2)
        self.ui.browse3.clicked.connect(self.browse3)
        self.ui.start.clicked.connect(self.start)
        self.ui.stop.clicked.connect(self.stop)
        self.ui.reset.clicked.connect(self.reset)
        self.timer_video.timeout.connect(self.timekeeping)

    def get_data(self, data1, data2, data3, data4, data5, data6, data7, data8, data9):
        self.originalData = [data1, data2, data3, data4, data5, data6, data7]
        self.ui.trainingProportion.setText(data1[0])
        self.ui.validationProportion.setText(data1[1])
        self.ui.predictionProportion.setText(data1[2])
        self.ui.learning_rate.setText(data2[0])
        self.ui.learning_rate_2.setText(data2[1])
        self.ui.epochs.setText(data2[2])
        self.ui.training_batch_size.setText((data2[3]))
        self.ui.validation_batch_size.setText((data2[4]))
        self.ui.checkBox_DSC.setChecked(data3[0])
        self.ui.checkBox_PPV.setChecked(data3[1])
        self.ui.checkBox_NPV.setChecked(data3[2])
        self.ui.checkBox_SEN.setChecked(data3[3])
        self.ui.checkBox_SPE.setChecked(data3[4])
        self.ui.save_each_epoch.setChecked(data4)
        self.ui.log_validation_set.setChecked(data5)
        self.ui.savePathForModels.setText(data6)
        self.ui.savePathForLogs.setText(data7)
        self.datasetPath = data8
        self.GPUNum = data9
        if not os.path.exists(data7):
            os.mkdir(data7)
        if not os.path.exists(data6):
            os.mkdir(data6)

    def importOrigin(self, files=None):
        if not files:
            try:
                files, filetype = QFileDialog.getOpenFileNames(self, "Import original images", os.getcwd().replace('\\', '/'),
                                                               "*.jpg;;*.png;;*.bmp;;*.tiff;;All Files(*)")
            except OSError:
                QMessageBox.warning(self, u"System", 'Error occurred when open files! Verify that the path is correct.')
                return
            if len(files) < 1:
                return
        rowCount = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.setRowCount(rowCount + len(files))
        for i in range(len(files)):
            if files[i][files[i].rfind("."):] not in ".jpg.png.bmp.tiff":
                QMessageBox.warning(self, u"System", 'Please upload a correct image file!')
                return
            self.originImages.append(files[i])
            checkBox = QtWidgets.QCheckBox()
            all_header_combobox.append(checkBox)  # 将所有的复选框都添加到 全局变量 all_header_combobox 中
            self.ui.tableWidget.setCellWidget(rowCount + i, 0, checkBox)  # 为每一行添加复选框
            label1, label2 = QtWidgets.QLabel(), QtWidgets.QLabel()
            label1.setPixmap(QtGui.QPixmap(files[i]).scaled(62, 35))
            label1.setAlignment(QtCore.Qt.AlignCenter)
            label2.setText(os.path.basename(files[i]))
            comboBox = QtWidgets.QComboBox()
            comboBox.addItem("training")
            comboBox.addItem("validation")
            comboBox.addItem("prediction")
            self.ui.tableWidget.setCellWidget(rowCount + i, 1, label1)
            self.ui.tableWidget.setCellWidget(rowCount + i, 2, label2)
            self.ui.tableWidget.setCellWidget(rowCount + i, 3, comboBox)
            self.cb_in_tw_dict[comboBox] = (rowCount + i, 3)
            # 使comboBox响应点击
            comboBox.currentIndexChanged.connect(self.selectOriSetType)
        self.ui.deleteOrigin.setEnabled(True)
        self.ui.start.setEnabled(True)

    def deleteOrigin(self):
        deleted = 0
        for i in range(self.ui.tableWidget.rowCount()):
            if self.ui.tableWidget.cellWidget(i - deleted, 0).checkState():
                self.ui.tableWidget.removeRow(i - deleted)
                del all_header_combobox[i - deleted]
                del self.originImages[i - deleted]
                deleted += 1
        if deleted == 0:
            QMessageBox.information(self, u"System", 'Please select the images you want to delete.')
        elif self.ui.tableWidget.rowCount() == 0:
            self.ui.deleteOrigin.setEnabled(False)
            self.ui.start.setEnabled(False)

    def importMask(self, files=None):
        if not files:
            try:
                files, filetype = QFileDialog.getOpenFileNames(self, "Import mask images", os.getcwd().replace(
                    '\\', '/'), "*.png;;*.jpg;;*.bmp;;*.tiff;;*.json;;All Files(*)")
            except OSError:
                QMessageBox.warning(self, u"System", 'Error occurred when open files! Verify that the path is correct.')
                return
            if len(files) < 1:
                return
        rowCount = self.ui.tableWidget_2.rowCount()
        inquired, dirPath = False, ""
        color_code = {}
        color_code['black'] = '#000000'
        color_code['white'] = (255, 255, 255)
        for i in range(len(files)):
            if files[i][files[i].rfind("."):] not in ".jpg.png.bmp.tiff.json":
                QMessageBox.warning(self, u"System", 'Please upload an image file or json file!')
                return
            label1, label2 = QtWidgets.QLabel(), QtWidgets.QLabel()
            if files[i][-5:] == ".json":
                try:
                    data = json.load(open(files[i]))
                    img = Image.new('RGB', (int(data['imageWidth']), int(data['imageHeight'])), color_code['black'])
                    img1 = ImageDraw.Draw(img)
                    label_idx_list = list(np.arange(len(data['shapes'])))
                    for j in label_idx_list:
                        # if data['shapes'][j]['label'] == 'Holy Plane':
                        xy = []
                        for xy_tuple in data['shapes'][j]['points']:
                            xy += xy_tuple
                        img1.polygon(xy, fill=color_code['white'], outline=color_code['white'])
                    if not inquired:
                        if QMessageBox.question(self, "System",
                                                "Would you like to save the the mask images generated from the json "
                                                "file?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                            dirPath = QFileDialog.getExistingDirectory(self, "Select the path for saving mask images")
                        inquired = True
                    if dirPath:
                        path = dirPath + "/" + os.path.basename(files[i])[:-5] + '.png'
                    else:
                        if not os.path.exists(self.datasetPath):
                            os.mkdir(self.datasetPath)
                        if not os.path.exists(self.datasetPath + "mask/"):
                            os.mkdir(self.datasetPath + "mask/")
                        path = self.datasetPath + "mask/" + os.path.basename(files[i])[:-5] + '.png'
                    img.save(path)
                    self.maskImages.append(path)
                    label1.setPixmap(QtGui.QPixmap(path).scaled(62, 35))
                    label2.setText(os.path.basename(path))
                except Exception as error:
                    traceback.print_exc()
                    QMessageBox.warning(self, u"System",
                                        u"Failed to convert json file %s to image file, please copy error code \"%s\" "
                                        u"and give a feedback to the author." % (files[i], error))
            else:  # 图片格式文件直接放进列表
                self.maskImages.append(files[i])
                label1.setPixmap(QtGui.QPixmap(files[i]).scaled(62, 35))
                label2.setText(os.path.basename(files[i]))
            self.ui.tableWidget_2.setRowCount(rowCount + i + 1)
            checkBox = QtWidgets.QCheckBox()
            all_header_combobox2.append(checkBox)  # 将所有的复选框都添加到 全局变量 all_header_combobox 中
            self.ui.tableWidget_2.setCellWidget(rowCount + i, 0, checkBox)  # 为每一行添加复选框
            label1.setAlignment(QtCore.Qt.AlignCenter)
            comboBox = QtWidgets.QComboBox()
            comboBox.addItem("training")
            comboBox.addItem("validation")
            comboBox.addItem("prediction")
            self.ui.tableWidget_2.setCellWidget(rowCount + i, 1, label1)
            self.ui.tableWidget_2.setCellWidget(rowCount + i, 2, label2)
            self.ui.tableWidget_2.setCellWidget(rowCount + i, 3, comboBox)
            self.cb_in_tw_dict2[comboBox] = (rowCount + i, 3)
            # 使comboBox响应点击
            comboBox.currentIndexChanged.connect(self.selectMaskSetType)
        self.ui.deleteMask.setEnabled(True)
        self.ui.start.setEnabled(True)

    def deleteMask(self):
        deleted = 0
        for i in range(self.ui.tableWidget_2.rowCount()):
            if self.ui.tableWidget_2.cellWidget(i - deleted, 0).checkState():
                self.ui.tableWidget_2.removeRow(i - deleted)
                if os.path.exists(self.maskImages[i - deleted]):
                    os.remove(self.maskImages[i - deleted])
                del all_header_combobox2[i - deleted]
                del self.maskImages[i - deleted]
                deleted += 1
        if deleted == 0:
            QMessageBox.information(self, u"System", 'Please select the images you want to delete.')
        elif self.ui.tableWidget_2.rowCount() == 0:
            self.ui.deleteMask.setEnabled(False)
            self.ui.start.setEnabled(False)

    def datasetCheck(self, len1, len2, pro1, pro2, pro3):  # 用于检验数据集数量与用户设定的比例是否合理
        if len1 != len2:
            QMessageBox.warning(self, u"System",
                                'The number of original images must be the same as the number of masks!')
            return False
        if not pro1.replace(".", "").isdigit() or not pro2.replace(".", "").isdigit() or not \
                pro3.replace(".", "").isdigit():
            QMessageBox.warning(self, u"System", 'The proportion of datasets must be a number!')
            return False
        if float(pro1) + float(pro2) + float(pro3) != 1:
            QMessageBox.warning(self, u"System", 'The sum of the dataset proportions must be 1!')
            return False
        if int(len1 * float(pro1)) == 0:
            QMessageBox.warning(self, u"System", 'The proportion of training set is too small, make sure the size of '
                                                 'the training set is not 0!')
            return False
        if int(len1 * float(pro2)) == 0:
            QMessageBox.warning(self, u"System", 'The proportion of validation set is too small, make sure the size of '
                                                 'the validation set is not 0!')
            return False
        return True

    def distribute1(self):
        lenOrigin, lenMask = self.ui.tableWidget.rowCount(), self.ui.tableWidget_2.rowCount()
        training, validation = self.ui.trainingProportion.text(), self.ui.validationProportion.text()
        prediction = self.ui.predictionProportion.text()
        if not self.datasetCheck(lenOrigin, lenMask, training, validation, prediction):
            return
        lenTraining = int(lenOrigin * float(training))
        for i in range(lenOrigin):
            if i < lenTraining:
                self.ui.tableWidget.cellWidget(i, 3).setCurrentIndex(0)
                self.ui.tableWidget_2.cellWidget(i, 3).setCurrentIndex(0)
            elif lenTraining <= i < lenTraining + int(lenOrigin * float(validation)):
                self.ui.tableWidget.cellWidget(i, 3).setCurrentIndex(1)
                self.ui.tableWidget_2.cellWidget(i, 3).setCurrentIndex(1)
            else:
                self.ui.tableWidget.cellWidget(i, 3).setCurrentIndex(2)
                self.ui.tableWidget_2.cellWidget(i, 3).setCurrentIndex(2)
        self.distributed = True

    def distribute2(self):
        lenOrigin, lenMask = self.ui.tableWidget.rowCount(), self.ui.tableWidget_2.rowCount()
        training, validation = self.ui.trainingProportion.text(), self.ui.validationProportion.text()
        prediction = self.ui.predictionProportion.text()
        if not self.datasetCheck(lenOrigin, lenMask, training, validation, prediction):
            return
        lenTraining = int(lenOrigin * float(training))
        ls = [i for i in range(lenOrigin)]
        random.shuffle(ls)
        for i in range(lenOrigin):
            if i < lenTraining:
                self.ui.tableWidget.cellWidget(ls[i], 3).setCurrentIndex(0)
                self.ui.tableWidget_2.cellWidget(ls[i], 3).setCurrentIndex(0)
            elif lenTraining <= i < lenTraining + int(lenOrigin * float(validation)):
                self.ui.tableWidget.cellWidget(ls[i], 3).setCurrentIndex(1)
                self.ui.tableWidget_2.cellWidget(ls[i], 3).setCurrentIndex(1)
            else:
                self.ui.tableWidget.cellWidget(ls[i], 3).setCurrentIndex(2)
                self.ui.tableWidget_2.cellWidget(ls[i], 3).setCurrentIndex(2)
        self.distributed = True

    def isPretrain(self):
        if self.ui.pretrain.isChecked():
            self.ui.pretrainPath.setDisabled(False)
            self.ui.browse1.setDisabled(False)
        else:
            self.ui.pretrainPath.setDisabled(True)
            self.ui.browse1.setDisabled(True)

    def browse1(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select the model for pretraining", self.ui.pretrainPath.text(),
                                              "All Files(*)")
        if ".onnx" not in file and ".pb" not in file and ".h5" not in file and ".keras" not in file and ".model" not in\
                file and ".json" not in file and ".tflite" not in file and ".prototxt" not in file and ".pt" not in \
                file and ".t7" not in file and ".cntk" not in file and ".cfg" not in file and "weights" not in file and\
                "ckpt" not in file and "bin" not in file and "bias" not in file:
            QMessageBox.warning(self, u"System", 'Please select a correct weight file. If it is do a weight file, '
                                'change the suffix to .onnx, .pb, .h5, .keras, .model, .json, .tflite, .prototxt, .pt, '
                                '.pth, .t7, .cnTk, .cfg, .weights, .ckpt, .bias or .bin')
            return
        self.ui.pretrainPath.setText(file)

    def browse2(self):
        direct = QFileDialog.getExistingDirectory(self, "Select the path for saving trained models",
                                                  self.ui.savePathForModels.text())
        self.ui.savePathForModels.setText(direct + "/")

    def browse3(self):
        direct = QFileDialog.getExistingDirectory(self, "Select the path for saving training logs",
                                                  self.ui.savePathForLogs.text())
        self.ui.savePathForLogs.setText(direct + "/")

    def start(self):
        def post_process(img1, min_size=100):
            """
            图像后处理过程，包括开运算和去除过小体素
            :return uint16格式numpy二值数组
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

        def analyse(x, y):
            """
            对输入的两个四维张量[B,1,H,W]进行逐图的DSC、PPV、Sensitivity计算
            x表示网络输出的预测值
            y表示实际的预想结果mask
            :return 一个batch中Dice score、阳性预测值、阴性预测值、敏感性、特异性的平均值及batch大小
            """
            def sum1(list1):
                s = 0
                for item in list1:
                    s += item
                return s
            x = x.type(dtype=torch.uint8)
            y = y.type(dtype=torch.uint8)
            DSC1, PPV1, NPV1, SEN, SPE = [], [], [], [], []  # Dice score、召回率、阳性预测值、阴性预测值、敏感性、特异性
            batch1 = len(x)
            if x.shape == y.shape:
                for i in range(batch1):  # 按第一个维度分开
                    tmp = torch.eq(x[i], y[i])
                    tp = int(torch.sum(torch.mul(x[i] == 1, tmp == 1)))  # 真阳性
                    tn = int(torch.sum(torch.mul(x[i] == 0, tmp == 1)))  # 真阴性
                    fp = int(torch.sum(torch.mul(x[i] == 1, tmp == 0)))  # 假阳性
                    fn = int(torch.sum(torch.mul(x[i] == 0, tmp == 0)))  # 假阴性
                    try:
                        DSC1.append(2 * tp / (fp + 2 * tp + fn))
                    except:
                        DSC1.append(0)
                    try:
                        PPV1.append(tp / (tp + fp))
                    except:
                        PPV1.append(0)
                    try:
                        NPV1.append(tn / (tn + fn))
                    except:
                        NPV1.append(0)
                    try:
                        SEN.append(tp / (tp + fn))
                    except:
                        SEN.append(0)
                    try:
                        SPE.append(tn / (tn + fp))
                    except:
                        SPE.append(0)
            else:
                self.ui.text_status.setText('Analysis input dimension error')
            DSC1, PPV1 = sum1(DSC1) / batch1, sum1(PPV1) / batch1
            NPV1, SEN, SPE = sum1(NPV1) / batch1, sum1(SEN) / batch1, sum1(SPE) / batch1
            return DSC1, PPV1, NPV1, SEN, SPE, batch1

        lenOrigin, lenMask = self.ui.tableWidget.rowCount(), self.ui.tableWidget_2.rowCount()
        training, validation = self.ui.trainingProportion.text(), self.ui.validationProportion.text()
        prediction = self.ui.predictionProportion.text()
        if not self.distributed:
            QMessageBox.warning(self, u"System", 'Please distribute the dataset first!')
            return
        if not self.datasetCheck(lenOrigin, lenMask, training, validation, prediction):
            return
        if not self.ui.training_batch_size.text().isdigit():
            QMessageBox.warning(self, u"System", 'The batch size of training set must be a integer!')
            return
        if not self.ui.validation_batch_size.text().isdigit():
            QMessageBox.warning(self, u"System", 'The batch size of validation set must be a integer!')
            return
        if not self.ui.learning_rate.text().replace(".", "").isdigit():
            QMessageBox.warning(self, u"System", 'The learning rate must be a number!')
            return
        if not self.ui.learning_rate_2.text().replace(".", "").isdigit():
            QMessageBox.warning(self, u"System", 'The decline rate of the learning rate must be a number!')
            return
        if not self.ui.epochs.text().isdigit():
            QMessageBox.warning(self, u"System", 'The epochs must be a integer!')
            return
        if self.ui.pretrain.isChecked() and not os.path.exists(self.ui.pretrainPath.text()):
            QMessageBox.warning(self, u"System", 'The pretrain model does not exist, please check that the path is entered correctly!')
            return
        if not os.path.exists(self.ui.savePathForModels.text()):
            QMessageBox.warning(self, u"System", 'The save path for the model does not exist, please check that the path is entered correctly!')
            return
        if not os.path.exists(self.ui.savePathForLogs.text()):
            QMessageBox.warning(self, u"System", 'The save path for the logs does not exist, please check that the path is entered correctly!')
            return
        if float(self.ui.learning_rate_2.text()) > 1:
            if QMessageBox.question(self, "System", "A decline rate of learning rate greater than 1 may cause problems "
                                    "such as difficulty in model convergence and gradient explosion. Are you sure to "
                                    "maintain this decline rate?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return

        self.stopTraining = False
        # 关闭所有按钮
        self.ui.importOrigin.setDisabled(True)
        self.ui.importMask.setDisabled(True)
        self.ui.deleteOrigin.setDisabled(True)
        self.ui.deleteMask.setDisabled(True)
        self.ui.modelType.setDisabled(True)
        self.ui.trainingProportion.setDisabled(True)
        self.ui.validationProportion.setDisabled(True)
        self.ui.predictionProportion.setDisabled(True)
        self.ui.learning_rate.setDisabled(True)
        self.ui.learning_rate_2.setDisabled(True)
        self.ui.epochs.setDisabled(True)
        self.ui.training_batch_size.setDisabled(True)
        self.ui.validation_batch_size.setDisabled(True)
        self.ui.pretrain.setDisabled(True)
        self.ui.start.setDisabled(True)
        self.ui.reset.setDisabled(True)
        # 打开停止按钮
        self.ui.stop.setDisabled(False)
        # 可调整的训练超参数
        batch_size = int(self.ui.training_batch_size.text())
        val_batch_size = int(self.ui.validation_batch_size.text())
        stop_epoch = int(self.ui.epochs.text())
        train_path = self.datasetPath + "train/"
        val_path = self.datasetPath + "validation/"
        pre_path = self.datasetPath + "prediction/"
        # 将数据集转移到指定文件夹
        if not os.path.exists(self.datasetPath):
            os.mkdir(self.datasetPath)
        if not os.path.exists(self.datasetPath + "train/"):
            os.mkdir(self.datasetPath + "train/")
            os.mkdir(self.datasetPath + "train/case/")
            os.mkdir(self.datasetPath + "train/mask/")
            os.mkdir(self.datasetPath + "validation/")
            os.mkdir(self.datasetPath + "validation/case/")
            os.mkdir(self.datasetPath + "validation/mask/")
            os.mkdir(self.datasetPath + "prediction/")
            os.mkdir(self.datasetPath + "prediction/case/")
            os.mkdir(self.datasetPath + "prediction/mask/")
        for i in range(len(self.originImages)):
            if self.ui.tableWidget.cellWidget(i, 3).currentIndex() == 0:
                shutil.copyfile(self.originImages[i], self.datasetPath + "train/case/" + os.path.basename(
                    self.originImages[i]))
            elif self.ui.tableWidget.cellWidget(i, 3).currentIndex() == 1:
                shutil.copyfile(self.originImages[i], self.datasetPath + "validation/case/" + os.path.basename(
                    self.originImages[i]))
            elif self.ui.tableWidget.cellWidget(i, 3).currentIndex() == 2:
                shutil.copyfile(self.originImages[i], self.datasetPath + "prediction/case/" + os.path.basename(
                    self.originImages[i]))
            if self.ui.tableWidget_2.cellWidget(i, 3).currentIndex() == 0:
                shutil.copyfile(self.maskImages[i], self.datasetPath + "train/mask/" + os.path.basename(
                    self.maskImages[i]))
            elif self.ui.tableWidget_2.cellWidget(i, 3).currentIndex() == 1:
                shutil.copyfile(self.maskImages[i], self.datasetPath + "validation/mask/" + os.path.basename(
                    self.maskImages[i]))
            elif self.ui.tableWidget_2.cellWidget(i, 3).currentIndex() == 2:
                shutil.copyfile(self.maskImages[i], self.datasetPath + "prediction/mask/" + os.path.basename(
                    self.maskImages[i]))
        # 可调整的训练相关处理
        pretrain = self.ui.pretrain.isChecked()
        os.environ['CUDA_VISIBLE_DEVICES'] = self.GPUNum
        modelType = self.ui.modelType.currentText()
        if modelType == "ResNet50-Unet":
            transform = transforms.Compose([transforms.Resize((512, 256)), transforms.ToTensor()])
        else:
            transform = transforms.Compose([transforms.Resize((512, 256)), transforms.ToTensor(),
                                            transforms.Normalize([0.5], [0.5])])
        log_path = self.ui.savePathForLogs.text()
        checkpoints_path = self.ui.savePathForModels.text()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        train_set = Dataset(path=train_path, transform=transform)
        val_set = Dataset(path=val_path, transform=transform)
        pre_set = Dataset(path=pre_path, transform=transform)
        train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_set, batch_size=val_batch_size, shuffle=False)
        pre_loader = DataLoader(pre_set, batch_size=1, shuffle=False)
        if modelType == "ResNet50-Unet":
            Model = Resnet_Unet(BN_enable=True, resnet_pretrain=pretrain).to(device)
        elif modelType == "U-net":
            Model = Unet(3, 1).to(device)
        if pretrain:
            Model.load_state_dict(torch.load(self.ui.pretrainPath.text()))
        criterion = nn.BCELoss().to(device) if modelType == "ResNet50-Unet" else nn.BCEWithLogitsLoss().to(device)
        optimizer = torch.optim.Adam(Model.parameters(), lr=float(self.ui.learning_rate.text()))
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=float(self.ui.learning_rate_2.text()))  # gamma为学习率的递减率
        batch_sum = len(train_loader)
        self.ui.text_elapsed.setHidden(False)
        self.ui.text_remaining.setHidden(False)
        self.ui.text_status.setHidden(False)
        self.ui.progressBar.setHidden(False)
        self.ui.verticalLayout.layout()
        self.ui.text_status.setText("\r[Training] [Epoch {}/{}] [Batch {}/{}] [loss:--] [learning rate:{}]".
                                    format(0, stop_epoch, 0, batch_sum, optimizer.param_groups[0]['lr']))
        self.start_time = time.time()
        self.trainTime, self.validateTime = 0, 0.1  # 每个epoch的训练和验证时间的初始设定
        self.currentValIndex, self.currentPreIndex = 0, 0
        self.timer_video.start(1000)  # 计时间隔为1秒
        QtCore.QCoreApplication.processEvents()
        with open(log_path + 'Validation result.txt', 'a') as f:
            f.write("Time: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        with open(log_path + 'Prediction result.txt', 'a') as f:
            f.write("Time: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        """——————————————————————————————————————————————————开始训练——————————————————————————————————————————————————"""
        try:
            for epoch in range(stop_epoch):
                self.currentEpoch = epoch
                scheduler.step()
                # 训练部分
                for index, (img, mask) in enumerate(train_loader):
                    temp = time.time()
                    img = img.to(device)
                    mask = mask.to(device)
                    Model.train()
                    Model.zero_grad()
                    QtCore.QCoreApplication.processEvents()
                    output = Model(img)
                    loss = criterion(output, mask)
                    loss.backward()
                    self.currentTrainIndex = epoch
                    self.trainTime = time.time() - temp
                    self.ui.text_status.setText(
                        "\r[Training] [Epoch {}/{}] [Batch {}/{}] [loss:{:.8f}] [learning rate:{}]".format(epoch + 1,
                        stop_epoch, index + 1, batch_sum, loss.item(), optimizer.param_groups[0]['lr']))
                    if self.stopTraining:
                        return
                if self.ui.save_each_epoch.isChecked():  # 根据用户设定的save for each epoch保存权重
                    torch.save(Model.state_dict(), checkpoints_path + modelType + '_{}.pth'.format(epoch + 1))
                elif epoch == stop_epoch - 1:
                    torch.save(Model.state_dict(), checkpoints_path + modelType + '_{}.pth'.format(epoch + 1))
                # 验证部分
                DSC_ave, PPV_ave, NPV_ave, Sen_ave, Spe_ave, batch_sum = 0, 0, 0, 0, 0, 0
                result = ""
                for index, (img, mask) in enumerate(val_loader):
                    temp = time.time()
                    Model.eval()
                    img = img.to(device)
                    mask = mask.to(device)
                    QtCore.QCoreApplication.processEvents()
                    with torch.no_grad():
                        output = Model(img)
                        output = torch.ge(output, 0.5).type(dtype=torch.float32)  # 二值化
                        output = post_process(output)  # 后处理
                        output = output.astype("uint8")
                        output = torch.from_numpy(output).to(device)
                        DSC, PPV, Npv, Sen, Spe, batch = analyse(output, mask)
                        DSC_ave += DSC * batch
                        PPV_ave += PPV * batch
                        NPV_ave += Npv * batch
                        Sen_ave += Sen * batch
                        Spe_ave += Spe * batch
                        batch_sum += batch
                    indexes = ""
                    if self.ui.checkBox_DSC.isChecked():
                        indexes += " [DSC:{:.3f}]".format(DSC)
                    if self.ui.checkBox_PPV.isChecked():
                        indexes += " [PPV:{:.3f}]".format(PPV)
                    if self.ui.checkBox_NPV.isChecked():
                        indexes += " [NPV:{:.3f}]".format(Npv)
                    if self.ui.checkBox_SEN.isChecked():
                        indexes += " [Sen:{.3f}]".format(Sen)
                    if self.ui.checkBox_SPE.isChecked():
                        indexes += " [Spe:{.3f}]".format(Spe)
                    self.currentValIndex = index
                    self.validateTime = time.time() - temp
                    self.ui.text_status.setText("\r[Validation] [Epoch {}/{}] [Batch {}/{}]"
                                                .format(epoch + 1, stop_epoch, index + 1, len(val_loader)) + indexes)
                    if self.ui.log_validation_set.isChecked():
                        result += "[Batch {}]\t".format(index + 1) + indexes + "\n"
                    QtWidgets.QApplication.processEvents()
                    if self.stopTraining:
                        return
                if batch_sum != 0:
                    DSC_ave /= batch_sum
                    PPV_ave /= batch_sum
                    NPV_ave /= batch_sum
                    Sen_ave /= batch_sum
                    Spe_ave /= batch_sum
                    indexes = ""
                    if self.ui.checkBox_DSC.isChecked():
                        indexes += " [DSC:{:.3f}]".format(DSC_ave)
                    if self.ui.checkBox_PPV.isChecked():
                        indexes += " [PPV:{:.3f}]".format(PPV_ave)
                    if self.ui.checkBox_NPV.isChecked():
                        indexes += " [NPV:{:.3f}]".format(NPV_ave)
                    if self.ui.checkBox_SEN.isChecked():
                        indexes += " [Sen:{.3f}]".format(Sen_ave)
                    if self.ui.checkBox_SPE.isChecked():
                        indexes += " [Spe:{.3f}]".format(Spe_ave)
                    with open(log_path + 'Validation result.txt', 'a') as f:
                        f.write('[Epoch {}]\t'.format(epoch + 1) + indexes + "\n")
                        if self.ui.log_validation_set.isChecked():
                            f.write(result)
            if len(pre_loader) != 0:
                # 测试部分
                DSC_ave, PPV_ave, NPV_ave, Sen_ave, Spe_ave, batch_sum = 0, 0, 0, 0, 0, 0
                result = ""
                files = os.listdir(self.datasetPath + "prediction/case/")
                for index, (img, mask) in enumerate(pre_loader):
                    Model.eval()
                    img = img.to(device)
                    mask = mask.to(device)
                    QtCore.QCoreApplication.processEvents()
                    with torch.no_grad():
                        output = Model(img)
                        output = torch.ge(output, 0.5).type(dtype=torch.float32)  # 二值化
                        output = post_process(output)  # 后处理
                        output = output.astype("uint8")
                        output = torch.from_numpy(output).to(device)
                        DSC, PPV, Npv, Sen, Spe, batch = analyse(output, mask)
                        DSC_ave += DSC * batch
                        PPV_ave += PPV * batch
                        NPV_ave += Npv * batch
                        Sen_ave += Sen * batch
                        Spe_ave += Spe * batch
                        batch_sum += batch
                    indexes = ""
                    if self.ui.checkBox_DSC.isChecked():
                        indexes += " [DSC:{:.3f}]".format(DSC)
                    if self.ui.checkBox_PPV.isChecked():
                        indexes += " [PPV:{:.3f}]".format(PPV)
                    if self.ui.checkBox_NPV.isChecked():
                        indexes += " [NPV:{:.3f}]".format(Npv)
                    if self.ui.checkBox_SEN.isChecked():
                        indexes += " [Sen:{.3f}]".format(Sen)
                    if self.ui.checkBox_SPE.isChecked():
                        indexes += " [Spe:{.3f}]".format(Spe)
                    self.currentPreIndex = index
                    self.ui.text_status.setText("\r[Prediction] [File {}/{}]".format(index + 1, len(pre_loader)) + indexes)
                    result += "[{}]\t".format(files[index]) + indexes + "\n"
                    QtWidgets.QApplication.processEvents()
                    if self.stopTraining:
                        return
                if batch_sum != 0:
                    DSC_ave /= batch_sum
                    PPV_ave /= batch_sum
                    NPV_ave /= batch_sum
                    Sen_ave /= batch_sum
                    Spe_ave /= batch_sum
                    indexes = ""
                    if self.ui.checkBox_DSC.isChecked():
                        indexes += " [DSC:{:.3f}]".format(DSC_ave)
                    if self.ui.checkBox_PPV.isChecked():
                        indexes += " [PPV:{:.3f}]".format(PPV_ave)
                    if self.ui.checkBox_NPV.isChecked():
                        indexes += " [NPV:{:.3f}]".format(NPV_ave)
                    if self.ui.checkBox_SEN.isChecked():
                        indexes += " [Sen:{.3f}]".format(Sen_ave)
                    if self.ui.checkBox_SPE.isChecked():
                        indexes += " [Spe:{.3f}]".format(Spe_ave)
                    with open(log_path + 'Prediction result.txt', 'a') as f:
                        f.write("Average" + indexes + "\n")
                        f.write(result + "\n")
                self.timer_video.stop()
                QMessageBox.information(self, u"System", u"Complete training and prediction successfully!")
            else:
                self.timer_video.stop()
                QMessageBox.information(self, u"System", u"Complete training successfully!")
            self.stop()
        except Exception as error:
            traceback.print_exc()
            QMessageBox.warning(self, u"System", u"Training failed, please copy error code \"%s\" and give a feedback "
                                                 u"to the author." % error)

    def stop(self):
        self.timer_video.stop()
        self.stopTraining = True
        self.ui.importOrigin.setDisabled(False)
        self.ui.importMask.setDisabled(False)
        self.ui.deleteOrigin.setDisabled(False)
        self.ui.deleteMask.setDisabled(False)
        self.ui.modelType.setDisabled(False)
        self.ui.trainingProportion.setDisabled(False)
        self.ui.validationProportion.setDisabled(False)
        self.ui.predictionProportion.setDisabled(False)
        self.ui.learning_rate.setDisabled(False)
        self.ui.learning_rate_2.setDisabled(False)
        self.ui.epochs.setDisabled(False)
        self.ui.training_batch_size.setDisabled(False)
        self.ui.validation_batch_size.setDisabled(False)
        self.ui.pretrain.setDisabled(False)
        self.ui.start.setDisabled(False)
        self.ui.stop.setDisabled(True)
        self.ui.reset.setDisabled(False)
        self.ui.text_elapsed.setHidden(True)
        self.ui.text_remaining.setHidden(True)
        self.ui.text_status.setHidden(True)
        self.ui.progressBar.setHidden(True)
        self.ui.text_elapsed.setText("Elapsed:00:00:00")
        self.ui.text_remaining.setText("Remaining:--:--:--")
        self.ui.progressBar.setValue(0)
        self.ui.verticalLayout.layout()
        shutil.rmtree(self.datasetPath)
        QtCore.QCoreApplication.processEvents()

    def reset(self):
        self.ui.trainingProportion.setText(self.originalData[0][0])
        self.ui.validationProportion.setText(self.originalData[0][1])
        self.ui.predictionProportion.setText(self.originalData[0][2])
        self.ui.learning_rate.setText(self.originalData[1][0])
        self.ui.learning_rate_2.setText(self.originalData[1][1])
        self.ui.epochs.setText(self.originalData[1][2])
        self.ui.training_batch_size.setText((self.originalData[1][3]))
        self.ui.validation_batch_size.setText((self.originalData[1][4]))
        self.ui.checkBox_DSC.setChecked(self.originalData[2][0])
        self.ui.checkBox_PPV.setChecked(self.originalData[2][1])
        self.ui.checkBox_NPV.setChecked(self.originalData[2][2])
        self.ui.checkBox_SEN.setChecked(self.originalData[2][3])
        self.ui.checkBox_SPE.setChecked(self.originalData[2][4])
        self.ui.save_each_epoch.setChecked(self.originalData[3])
        self.ui.log_validation_set.setChecked(self.originalData[4])
        self.ui.savePathForModels.setText(self.originalData[5])
        self.ui.savePathForLogs.setText(self.originalData[6])

    def timekeeping(self):
        elapsed = time.time() - self.start_time
        self.ui.text_elapsed.setText("Elapsed:" + time.strftime("%H:%M:%S", time.gmtime(elapsed)))
        if self.trainTime == 0:  # 若还没开始训练则不显示剩余时间
            self.ui.text_remaining.setText("Remaining:--:--:--")
        else:
            epochs = int(self.ui.epochs.text())
            files = (int(self.ui.tableWidget.rowCount()))
            valBatchSize = int(self.ui.validation_batch_size.text())
            trainBatches = math.ceil(files * float(self.ui.trainingProportion.text()) /
                                     int(self.ui.training_batch_size.text()))
            valBatches = math.ceil(files * float(self.ui.validationProportion.text()) / valBatchSize)
            preBatches = math.ceil(files * float(self.ui.predictionProportion.text()))
            remaining = (epochs - self.currentEpoch - 1) * (trainBatches * self.trainTime + valBatches *
                        self.validateTime) + (trainBatches - self.currentTrainIndex) * self.trainTime + \
                        (valBatches - self.currentValIndex) * self.validateTime + (preBatches - self.currentPreIndex) * self.validateTime / valBatchSize
            self.ui.progressBar.setValue(int(round((elapsed / (remaining + elapsed)) * 1000)))
            self.ui.text_remaining.setText("Remaining:" + time.strftime("%H:%M:%S", time.gmtime(remaining)))

    def selectOriSetType(self):
        index = self.cb_in_tw_dict[self.sender()]  # 记录发出信号的comboBox的位置，即self.sender()
        self.ui.tableWidget.cellChanged.emit(*index)  # 将信号发送给tableWidget令其修改

    def selectMaskSetType(self):
        index = self.cb_in_tw_dict2[self.sender()]  # 记录发出信号的comboBox的位置，即self.sender()
        self.ui.tableWidget_2.cellChanged.emit(*index)  # 将信号发送给tableWidget2令其修改

    def closeEvent(self, event):
        def numberCheck(string, item):
            if not string.replace(".", "").isdigit():
                QMessageBox.warning(self, u"System", u"The %s must be a number!" % item)
                event.ignore()
                return False
            return True

        if self.timer_video.isActive():
            if QMessageBox.question(self, "Quit", "Exiting the program will stop training, but the saved models and "
                                                  "logs will not be deleted. Are you sure you want to quit the program?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                shutil.rmtree(self.datasetPath)
            else:
                event.ignore()
                return
        data1, data2, data3 = self.ui.trainingProportion.text(), self.ui.validationProportion.text(), \
            self.ui.predictionProportion.text()
        data4, data5, data6 = self.ui.learning_rate.text(), self.ui.learning_rate_2.text(), self.ui.epochs.text()
        data7, data8 = self.ui.training_batch_size.text(), self.ui.validation_batch_size.text()
        if not numberCheck(data1, "proportion of the training set"):
            return
        if not numberCheck(data2, "proportion of the validation set"):
            return
        if not numberCheck(data3, "proportion of the prediction set"):
            return
        if not numberCheck(data4, "learning rate"):
            return
        if not numberCheck(data5, "decline rate of the learning rate"):
            return
        if not numberCheck(data6, "epochs"):
            return
        if not numberCheck(data7, "batch size of the training set"):
            return
        if not numberCheck(data8, "batch size of the validation set"):
            return
        self.signal_trainModels.emit([data1, data2, data3], [data4, data5, data6, data7, data8],
                                     [self.ui.checkBox_DSC.isChecked(), self.ui.checkBox_PPV.isChecked(),
                                     self.ui.checkBox_NPV.isChecked(), self.ui.checkBox_SEN.isChecked(),
                                     self.ui.checkBox_SPE.isChecked()], self.ui.save_each_epoch.isChecked(),
                                     self.ui.log_validation_set.isChecked(), self.ui.savePathForModels.text(),
                                     self.ui.savePathForLogs.text())
        if os.path.exists(self.datasetPath):
            shutil.rmtree(self.datasetPath)

    def dragEnterEvent(self, QDragEnterEvent):
        if QDragEnterEvent.mimeData().hasText():
            QDragEnterEvent.acceptProposedAction()

    def dragMoveEvent(self, event):
        rect1, rect2 = self.ui.tableWidget.rect(), self.ui.tableWidget_2.rect()
        if QtCore.QRect(10, 100, rect1.width(), rect1.height()).contains(event.pos()) or \
                QtCore.QRect(14 + rect1.width(), 100, rect2.width(), rect2.height()).contains(event.pos()):
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
        ls = []
        for i in filePath:
            if i[i.rfind("."):] in ".jpg.png.bmp.tiff":
                ls.append(i)
        if ls:
            rect1, rect2 = self.ui.tableWidget.rect(), self.ui.tableWidget_2.rect()
            if QtCore.QRect(10, 100, rect1.width(), rect1.height()).contains(event.pos()):
                self.importOrigin(ls)
            else:
                self.importMask(ls)
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = win_Training()
    MainWindow.show()
    sys.exit(app.exec_())