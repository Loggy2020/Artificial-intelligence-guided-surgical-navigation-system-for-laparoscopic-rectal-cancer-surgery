from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(About.sizePolicy().hasHeightForWidth())
        About.setSizePolicy(sizePolicy)
        About.setMinimumSize(QtCore.QSize(680, 520))
        About.setMaximumSize(QtCore.QSize(680, 520))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        About.setWindowIcon(icon)
        self.horizontalLayoutWidget = QtWidgets.QWidget(About)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 0, 641, 500))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(80, 80))
        self.label.setMaximumSize(QtCore.QSize(80, 80))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("images/logo.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_2.setMinimumSize(QtCore.QSize(500, 500))
        self.label_2.setMaximumSize(QtCore.QSize(500, 500))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "About"))
        self.label_2.setText(_translate("About", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Times New Roman\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p style=\" font-size:16pt; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Surgical Navigation System</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p style=\" font-size:12pt; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ver 1.0</p>\n"
"<p align=\"justify\" style=\" font-size:11pt; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Times New Roman,serif\'; color:#000000;\">Based on the potential of deep learning for phase recognition and target structure segmentation, this system constructs and evaluates a deep learning model for automatic segmentation of holy plane space during laparoscopic rectal cancer surgery, and evaluates the feasibility of image-guided laparoscopic TME. This helps surgeons to realize automatic identification of holy plane space in laparoscopic rectal cancer surgery, and contributes to safe and accurate completion of high-quality laparoscopic TME surgery.</span></p>\n"
"<p style=\" font-size:12pt; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Copyright(C) 2023 Linxin Dai</p></body></html>"))


class win_About(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(win_About, self).__init__(parent)
        self.ui = Ui_About()
        self.ui.setupUi(self)