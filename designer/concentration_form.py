# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConcentrationForm.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ConcentrationForm(object):
    def setupUi(self, ConcentrationForm):
        ConcentrationForm.setObjectName("ConcentrationForm")
        ConcentrationForm.resize(400, 80)
        self.label = QtWidgets.QLabel(ConcentrationForm)
        self.label.setGeometry(QtCore.QRect(10, 10, 331, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(ConcentrationForm)
        self.label_2.setGeometry(QtCore.QRect(20, 40, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.intervalSpinBox = QtWidgets.QDoubleSpinBox(ConcentrationForm)
        self.intervalSpinBox.setGeometry(QtCore.QRect(130, 40, 51, 22))
        self.intervalSpinBox.setDecimals(1)
        self.intervalSpinBox.setMinimum(0.2)
        self.intervalSpinBox.setMaximum(5.0)
        self.intervalSpinBox.setSingleStep(0.1)
        self.intervalSpinBox.setProperty("value", 0.5)
        self.intervalSpinBox.setObjectName("intervalSpinBox")
        self.startToggleBtn = QtWidgets.QPushButton(ConcentrationForm)
        self.startToggleBtn.setGeometry(QtCore.QRect(200, 40, 75, 23))
        self.startToggleBtn.setObjectName("startToggleBtn")

        self.retranslateUi(ConcentrationForm)
        QtCore.QMetaObject.connectSlotsByName(ConcentrationForm)

    def retranslateUi(self, ConcentrationForm):
        _translate = QtCore.QCoreApplication.translate
        ConcentrationForm.setWindowTitle(_translate("ConcentrationForm", "Form"))
        self.label.setText(_translate("ConcentrationForm", "Concentration Settings:"))
        self.label_2.setText(_translate("ConcentrationForm", "Interval:"))
        self.startToggleBtn.setText(_translate("ConcentrationForm", "Start"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConcentrationForm = QtWidgets.QWidget()
    ui = Ui_ConcentrationForm()
    ui.setupUi(ConcentrationForm)
    ConcentrationForm.show()
    sys.exit(app.exec_())
