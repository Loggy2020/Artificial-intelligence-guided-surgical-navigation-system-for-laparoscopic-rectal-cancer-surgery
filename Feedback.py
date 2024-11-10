import re
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from captcha.image import ImageCaptcha
import smtplib
from email.mime.text import MIMEText
from random import randint
import cv2
import numpy as np


class Ui_Feedback(object):
    def setupUi(self, Feedback):
        Feedback.setObjectName("Feedback")
        Feedback.resize(765, 675)
        Feedback.setMinimumSize(765, 675)
        Feedback.setMaximumSize(765, 675)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Feedback.sizePolicy().hasHeightForWidth())
        Feedback.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Feedback.setWindowIcon(icon)
        self.verticalLayoutWidget = QtWidgets.QWidget(Feedback)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 10, 737, 587))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setMinimumSize(QtCore.QSize(750, 0))
        self.label_2.setMaximumSize(QtCore.QSize(750, 16777215))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setMinimumSize(QtCore.QSize(250, 0))
        self.lineEdit.setMaximumSize(QtCore.QSize(250, 16777215))
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.textEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout_2.addWidget(self.textEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_6 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(75, 0))
        self.lineEdit_2.setMaximumSize(QtCore.QSize(75, 16777215))
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_3.addWidget(self.lineEdit_2)
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_7.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.label_8 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.layoutWidget = QtWidgets.QWidget(Feedback)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 615, 737, 48))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_2.setMinimumSize(QtCore.QSize(100, 30))
        self.pushButton_2.setMaximumSize(QtCore.QSize(100, 30))
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.pushButton.setMaximumSize(QtCore.QSize(100, 30))
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_5.addWidget(self.pushButton)

        self.retranslateUi(Feedback)
        QtCore.QMetaObject.connectSlotsByName(Feedback)

    def retranslateUi(self, Feedback):
        _translate = QtCore.QCoreApplication.translate
        Feedback.setWindowTitle(_translate("Feedback", "Feedback"))
        self.label.setText(_translate("Feedback", "Feedback"))
        self.label_2.setText(_translate("Feedback", "If you have any questions, comments or suggestions, please write below and send them to the author."))
        self.label_3.setText(_translate("Feedback", "<html><head/><body><p>Your Email:<span style=\" color:#ff0000; vertical-align:super;\">*</span></p></body></html>"))
        self.label_4.setText(_translate("Feedback", "　　　　　  Replies will be sent to this Email address."))
        self.label_5.setText(_translate("Feedback", "<html><head/><body><p>Suggestions:<span style=\" color:#ff0000; vertical-align:super;\">*</span></p></body></html>"))
        self.label_6.setText(_translate("Feedback", "<html><head/><body><p>Verification Code:<span style=\" color:#ff0000; vertical-align:super;\">*</span></p></body></html>"))
        self.label_8.setText(_translate("Feedback", "Click the verification code to replace it."))
        self.pushButton_2.setText(_translate("Feedback", "Submit"))
        self.pushButton.setText(_translate("Feedback", "Close"))


class win_Feedback(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(win_Feedback, self).__init__(parent)
        self.ui = Ui_Feedback()
        self.ui.setupUi(self)
        self.init_slots()
        self.generate_authCode()

    def generate_authCode(self):
        ls = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
              'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F',
              'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.code = ''
        for i in range(4):
            self.code += ls[randint(0, 61)]
        img = ImageCaptcha().generate_image(self.code)
        image = cv2.resize(np.asarray(img), dsize=(100, 33), interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        QtImg = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_ARGB32)
        self.ui.label_7.setPixmap(QtGui.QPixmap.fromImage(QtImg))

    def init_slots(self):
        self.ui.pushButton.clicked.connect(self.Close)
        self.ui.pushButton_2.clicked.connect(self.submit)

    def mousePressEvent(self, qme):
        if self.childAt(qme.x(), qme.y()) is self.ui.label_7:
            self.generate_authCode()

    def submit(self):
        if self.ui.lineEdit.text() == "":
            QMessageBox.warning(self, u"System", u"Please fill in the email!")
            return
        if not re.findall('^\w+@\w+\.com$', self.ui.lineEdit.text()):
            QMessageBox.warning(self, u"System", u"Please fill in the correct email format!")
            return
        if self.ui.textEdit.toPlainText() == "":
            QMessageBox.warning(self, u"System", u"The content of suggestions must not be empty.")
            return
        if self.ui.lineEdit_2.text() != self.code:
            warningText = "Please fill in the verification code!" if self.ui.lineEdit_2.text() == "" else \
                "The verification code is wrong!"
            QMessageBox.warning(self, u"System", warningText)
            return
        s = smtplib.SMTP("smtp.163.com", 25)
        s.login("loggy12@163.com", "TZDAMKTDUDKSHXVR")
        msg = self.ui.textEdit.toPlainText()
        msg += "\n邮箱：%s" % self.ui.lineEdit.text()
        msg = MIMEText(msg)
        msg["Subject"] = "The feedback of Surgical Navigation System"
        msg["From"] = "loggy12@163.com"
        msg["To"] = "773645385@qq.com"
        s.sendmail("loggy12@163.com", "773645385@qq.com", msg.as_string())
        QMessageBox.information(self, u"System", u"Comments submitted successfully, thank you for your feedback!")

    def Close(self):
        self.close()
