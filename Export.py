from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from moviepy.editor import VideoFileClip
import os
import time
import cv2


class Ui_Export(object):
    def setupUi(self, Export):
        Export.setObjectName("Export")
        Export.resize(1200, 580)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Export.sizePolicy().hasHeightForWidth())
        Export.setSizePolicy(sizePolicy)
        Export.setMinimumSize(QtCore.QSize(1200, 580))
        Export.setMaximumSize(QtCore.QSize(1200, 580))
        self.centralwidget = QtWidgets.QWidget(Export)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 1181, 569))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.title.setMinimumSize(QtCore.QSize(0, 50))
        self.title.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.Source = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.Source.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.Source.setFont(font)
        self.Source.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft)
        self.Source.setObjectName("Source")
        self.verticalLayout.addWidget(self.Source)
        self.progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.progressBar.setStyleSheet("QProgressBar {border-radius: 10px; text-align: center;}")
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(self.verticalLayoutWidget)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 370))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 370))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.groupBox.setFont(font)
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.groupBox)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(0, 20, 1141, 340))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.preview = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.preview.setMinimumSize(QtCore.QSize(600, 338))
        self.preview.setMaximumSize(QtCore.QSize(600, 338))
        self.preview.setText("")
        self.preview.setObjectName("preview")
        self.horizontalLayout_2.addWidget(self.preview)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_3.setMinimumSize(QtCore.QSize(100, 0))
        self.label_3.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.FileName = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.FileName.setText("")
        self.FileName.setObjectName("FileName")
        self.horizontalLayout_3.addWidget(self.FileName)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_5.setMinimumSize(QtCore.QSize(100, 0))
        self.label_5.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.Path = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.Path.setText("")
        self.Path.setObjectName("Path")
        self.horizontalLayout_5.addWidget(self.Path)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_10 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_10.setMinimumSize(QtCore.QSize(100, 0))
        self.label_10.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_10.addWidget(self.label_10)
        self.Type = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.Type.setText("")
        self.Type.setObjectName("Type")
        self.horizontalLayout_10.addWidget(self.Type)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_6 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_6.setMinimumSize(QtCore.QSize(100, 0))
        self.label_6.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.Coding = QtWidgets.QComboBox(self.horizontalLayoutWidget_2)
        self.Coding.setMinimumSize(QtCore.QSize(100, 0))
        self.Coding.setMaximumSize(QtCore.QSize(100, 16777215))
        self.Coding.setObjectName("Coding")
        self.Coding.addItem("")
        self.Coding.addItem("")
        self.Coding.addItem("")
        self.Coding.addItem("")
        self.Coding.addItem("")
        self.Coding.addItem("")
        self.Coding.addItem("")
        self.horizontalLayout_6.addWidget(self.Coding)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_7 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_7.setMinimumSize(QtCore.QSize(100, 0))
        self.label_7.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_7.addWidget(self.label_7)
        self.Parameters = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.Parameters.setText("")
        self.Parameters.setObjectName("Parameters")
        self.horizontalLayout_7.addWidget(self.Parameters)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_8 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_8.setMinimumSize(QtCore.QSize(100, 0))
        self.label_8.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_8.addWidget(self.label_8)
        self.bitrate = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.bitrate.setMinimumSize(QtCore.QSize(50, 0))
        self.bitrate.setMaximumSize(QtCore.QSize(50, 16777215))
        self.bitrate.setObjectName("bitrate")
        self.horizontalLayout_8.addWidget(self.bitrate)
        self.label_9 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_8.addWidget(self.label_9)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem4)
        self.pushButton_start = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_start.setMinimumSize(QtCore.QSize(150, 35))
        self.pushButton_start.setMaximumSize(QtCore.QSize(150, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.pushButton_start.setFont(font)
        self.pushButton_start.setObjectName("pushButton_start")
        self.horizontalLayout_9.addWidget(self.pushButton_start)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem5)
        self.pushButton_path = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_path.setMinimumSize(QtCore.QSize(150, 35))
        self.pushButton_path.setMaximumSize(QtCore.QSize(150, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.pushButton_path.setFont(font)
        self.pushButton_path.setObjectName("pushButton_path")
        self.horizontalLayout_9.addWidget(self.pushButton_path)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem6)
        self.pushButton_pause = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_pause.setEnabled(False)
        self.pushButton_pause.setMinimumSize(QtCore.QSize(150, 35))
        self.pushButton_pause.setMaximumSize(QtCore.QSize(150, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.pushButton_pause.setFont(font)
        self.pushButton_pause.setObjectName("pushButton_pause")
        self.horizontalLayout_9.addWidget(self.pushButton_pause)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem7)
        self.pushButton_stop = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_stop.setMinimumSize(QtCore.QSize(150, 35))
        self.pushButton_stop.setMaximumSize(QtCore.QSize(150, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.pushButton_stop.setFont(font)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.horizontalLayout_9.addWidget(self.pushButton_stop)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem8)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        Export.setCentralWidget(self.centralwidget)

        self.retranslateUi(Export)
        QtCore.QMetaObject.connectSlotsByName(Export)

    def retranslateUi(self, Export):
        _translate = QtCore.QCoreApplication.translate
        Export.setWindowTitle(_translate("Export", "Export"))
        self.title.setText(_translate("Export", "Export videos"))
        self.Source.setText(_translate("Export", "Souce: "))
        self.label_2.setText(_translate("Export", "Elapsed: "))
        self.label.setText(_translate("Export", "Remaining:              "))
        self.groupBox.setTitle(_translate("Export", "Output Preview"))
        self.label_3.setText(_translate("Export", "File Name:"))
        self.label_5.setText(_translate("Export", "Path:"))
        self.label_10.setText(_translate("Export", "Type:"))
        self.label_6.setText(_translate("Export", "Coding:"))
        self.Coding.setItemText(0, _translate("Export", "mp4v"))
        self.Coding.setItemText(1, _translate("Export", "x264"))
        self.Coding.setItemText(2, _translate("Export", "x263"))
        self.Coding.setItemText(3, _translate("Export", "xvid"))
        self.Coding.setItemText(4, _translate("Export", "divx"))
        self.Coding.setItemText(5, _translate("Export", "flv1"))
        self.Coding.setItemText(6, _translate("Export", "theo"))
        self.label_7.setText(_translate("Export", "Video:"))
        self.label_8.setText(_translate("Export", "Bitrate:"))
        self.label_9.setText(_translate("Export", "kbps"))
        self.pushButton_start.setText(_translate("Export", "Start"))
        self.pushButton_path.setText(_translate("Export", "Edit path"))
        self.pushButton_pause.setText(_translate("Export", "Pause / Continue"))
        self.pushButton_stop.setText(_translate("Export", "Stop"))


class win_Export(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(win_Export, self).__init__(parent)
        self.ui = Ui_Export()
        self.ui.setupUi(self)
        self.timer_video = QtCore.QTimer()  # 创建定时器
        self.init_slots()
        self.stopFlag = 1  # 暂停与播放辅助信号，note：通过奇偶来控制暂停与播放

    def init_slots(self):
        self.ui.pushButton_start.clicked.connect(self.start)
        self.ui.pushButton_path.clicked.connect(self.editPath)
        self.ui.pushButton_pause.clicked.connect(self.pause)
        self.ui.pushButton_stop.clicked.connect(self.stop)
        self.timer_video.timeout.connect(self.openFrame)

    def imshow(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        QtImg = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_ARGB32)
        self.ui.preview.setPixmap(QtGui.QPixmap.fromImage(QtImg))
        self.ui.preview.setScaledContents(True)  # 设置图像自适应界面大小

    def openFrame(self):
        temp = time.time()
        frame = self.video[self.frame]
        self.imshow(frame)
        self.videowrite.write(frame)
        rate = time.time() - temp  # 每一帧的处理时间
        self.frame += 1
        # 更新进度条界面
        value = int(self.frame / 2) if self.isCompression == 0 else self.frame  # 若对视频进行压缩则进度减半
        self.ui.progressBar.setValue(value)
        self.ui.label_2.setText("Elapsed:" + time.strftime("%H:%M:%S", time.gmtime(time.time() - self.startTime)))
        self.ui.label.setText("Remaining:" + time.strftime("%H:%M:%S", time.gmtime(
            rate * (self.totalFrames - value))))  # 估计剩余时间
        if self.frame == self.totalFrames:
            self.videowrite.release()
            self.timer_video.stop()  # 停止计时器
            if self.isCompression == 0:  # 压缩视频文件
                self.ui.label_2.setText("Compressing...")
                QtWidgets.QApplication.processEvents()
                clip = VideoFileClip(self.path)
                clip.write_videofile(self.path[:self.path.rfind(".")] + "_compressed" + self.path[self.path.rfind("."):]
                                     , bitrate='%dk' % int(self.ui.bitrate.text()))
                os.remove(self.path)
                self.ui.progressBar.setValue(self.totalFrames)
                self.ui.label_2.setText(
                    "Elapsed:" + time.strftime("%H:%M:%S", time.gmtime(time.time() - self.startTime)))
                self.ui.label.setText("Remaining:00:00:00")
                self.ui.bitrate.setDisabled(False)
            QMessageBox.information(self, u"System", u"Save successfully!")
            self.ui.pushButton_start.setDisabled(False)
            self.ui.pushButton_path.setDisabled(False)
            self.ui.pushButton_pause.setDisabled(True)
            self.ui.pushButton_stop.setDisabled(True)
            self.frame = 0
        
    def get_data(self, data1, data2, data3, data4, data5, data6, data7):
        self.video, self.fps, self.isCompression = data1, data4, data7
        basename, format = data2[:data2.rfind(".")], data2[data2.rfind("."):]
        if format == ".avi":
            self.ui.Coding.setCurrentText("xvid")
        elif format == ".mkv":
            self.ui.Coding.setCurrentText("x264")
        elif format == ".flv":
            self.ui.Coding.setCurrentText("flv1")
        elif format == ".ogv":
            self.ui.Coding.setCurrentText("theo")
        self.path = basename + "_mask" + format if data3 == 1 else basename + "_label" + format
        frame0 = self.video[0]
        self.size = (frame0.shape[1], frame0.shape[0])  # 输出大小即原视频大小
        videoType = "mask" if data3 == 1 else "label"
        self.totalFrames = len(self.video)
        self.imshow(frame0)
        self.ui.Source.setText("Source: %s" % os.path.basename(data2))
        self.ui.FileName.setText(os.path.basename(self.path))
        self.ui.Path.setText(os.path.dirname(self.path))
        self.ui.Type.setText(videoType)
        self.ui.Parameters.setText("{}x{} (1.0), {} fps, Apple ProRes 422, {:02d}:{:02d}:{:02d}:{:02d}".format(
            self.size[0], self.size[1], data4, self.totalFrames // self.fps // 3600,
            self.totalFrames // self.fps // 60 % 60, self.totalFrames // self.fps % 60, self.totalFrames % self.fps))
        self.ui.bitrate.setText(str(data5))
        if data6 == 0:  # 若自动开始的变量为0, 则直接开始导出
            self.start()

    def start(self):
        if self.isCompression == 0:
            bitrate = self.ui.bitrate.text()
            if not bitrate.isdigit():
                QMessageBox.warning(self, u"System", u"The bit rate of the video must be a digit!")
                return
            if int(bitrate) <= 0:
                QMessageBox.warning(self, u"System", u"The bit rate of the video must be a positive!")
                return
            if 480 <= self.size[1] < 720 and int(bitrate) < 800:
                if QMessageBox.question(self, "System", "A too low bit rate will make the video blurred. Do you need to"
                                        " adjust the bit rate?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    return
            elif 720 <= self.size[1] < 1080 and int(bitrate) < 1500:
                if QMessageBox.question(self, "System", "A too low bit rate will make the video blurred. Do you need to"
                                        " adjust the bit rate?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    return
            elif self.size[1] > 1080 and int(bitrate) < 2500:
                if QMessageBox.question(self, "System", "A too low bit rate will make the video blurred. Do you need to"
                                        " adjust the bit rate?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    return
            self.ui.bitrate.setDisabled(True)
        # 关闭Start, Path按键点击功能，打开Pause, Stop按键点击功能
        self.ui.pushButton_start.setDisabled(True)
        self.ui.pushButton_path.setDisabled(True)
        self.ui.pushButton_pause.setDisabled(False)
        self.ui.pushButton_stop.setDisabled(False)
        self.ui.pushButton_pause.setText(u'Pause')
        self.videowrite = cv2.VideoWriter(self.path, cv2.VideoWriter_fourcc(*self.ui.Coding.currentText()), self.fps, self.size)
        self.frame = 0
        self.timer_video.start(0)
        self.startTime = time.time()
        self.ui.progressBar.setMaximum(self.totalFrames)

    def editPath(self):
        temp = self.path
        self.path, filetype = QFileDialog.getSaveFileName(
            self, "Select a save path", self.path, "All Files (*);;*.mp4;;*.avi;;*.flv;;*.mkv;;*.ogv;;*.wmv;;*.mov")
        if self.path == "":
            self.path = temp
            return
        if not os.path.exists(os.path.dirname(self.path)):
            QMessageBox.warning(self, u"System", u"Please check whether the path exists.")
            self.path = temp
            return
        if filetype == "*.flv":
            self.ui.Coding.setCurrentText("flv1")
        elif filetype == "*.ogv":
            self.ui.Coding.setCurrentText("theo")
        self.ui.FileName.setText(os.path.basename(self.path))
        self.ui.Path.setText(os.path.dirname(self.path))

    def pause(self):
        if self.timer_video.isActive() and self.stopFlag % 2 == 1:
            self.ui.pushButton_pause.setText(u'Continue')  # 当前状态为暂停状态
            self.stopFlag = self.stopFlag + 1  # 调整标记信号为偶数
            self.timer_video.blockSignals(True)
        else:
            self.stopFlag = self.stopFlag - 1
            self.ui.pushButton_pause.setText(u'Pause')
            self.timer_video.blockSignals(False)

    def stop(self):
        if QMessageBox.question(self, "System", "Stopping will delete the video content that has been exported. Are you"
                                " sure you want to stop?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.ui.preview.clear()
            self.timer_video.stop()  # 停止计时器
            self.ui.progressBar.setValue(0)
            self.ui.pushButton_start.setDisabled(False)
            self.ui.pushButton_path.setDisabled(False)
            self.ui.pushButton_pause.setDisabled(True)
            self.ui.pushButton_stop.setDisabled(True)
            self.frame = 0
            self.ui.pushButton_pause.setText(u'Pause / continue')
            if self.stopFlag % 2 == 0:
                self.stopFlag = self.stopFlag + 1
                self.timer_video.blockSignals(False)
            os.remove(self.path)

    def closeEvent(self, event):  # 函数名固定不可变
        if self.timer_video.isActive():
            if QMessageBox.question(self, "Quit", "Exiting the program will stop exporting the video, and the exported "
                                    "video will be deleted. Are you sure you want to quit the program?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                os.remove(self.path)
            else:
                event.ignore()
