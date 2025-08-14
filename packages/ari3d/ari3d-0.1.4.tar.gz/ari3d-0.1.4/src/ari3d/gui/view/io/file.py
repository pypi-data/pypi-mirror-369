"""Module for the ImageModifierDialog UI."""
from __future__ import annotations

from PyQt6 import QtCore, QtGui, QtWidgets


class ImageModifierDialog:
    """UI class for the ImageModifierDialog."""

    def setupUi(self, Dialog):
        """Set up the UI for the ImageModifierDialog."""
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 278)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 12, 381, 42))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSizeConstraint(
            QtWidgets.QLayout.SizeConstraint.SetFixedSize
        )
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineSetPath = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget)
        self.lineSetPath.setMaximumSize(QtCore.QSize(16777215, 25))
        self.lineSetPath.setObjectName("lineSetPath")
        self.horizontalLayout.addWidget(self.lineSetPath)
        self.linkButtonSetpath = QtWidgets.QCommandLinkButton(
            parent=self.horizontalLayoutWidget
        )
        self.linkButtonSetpath.setMaximumSize(QtCore.QSize(100, 40))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.linkButtonSetpath.setFont(font)
        self.linkButtonSetpath.setIconSize(QtCore.QSize(25, 25))
        self.linkButtonSetpath.setObjectName("linkButtonSetpath")
        self.horizontalLayout.addWidget(self.linkButtonSetpath)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(parent=Dialog)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 90, 381, 31))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.horizontalLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget_2)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_2.addWidget(self.lineEdit_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget_2)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.lineEdit = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget_2)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.label_2 = QtWidgets.QLabel(parent=Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 63, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(parent=Dialog)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(10, 130, 381, 31))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(parent=self.horizontalLayoutWidget_3)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        spacerItem = QtWidgets.QSpacerItem(
            16,
            25,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_3.addItem(spacerItem)
        self.lineEdit_6 = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget_3)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.horizontalLayout_3.addWidget(self.lineEdit_6)
        self.lineEdit_5 = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget_3)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.horizontalLayout_3.addWidget(self.lineEdit_5)
        self.lineEdit_4 = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget_3)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.horizontalLayout_3.addWidget(self.lineEdit_4)
        self.checkBox = QtWidgets.QCheckBox(parent=Dialog)
        self.checkBox.setGeometry(QtCore.QRect(10, 190, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.checkBox.setFont(font)
        self.checkBox.setIconSize(QtCore.QSize(30, 30))
        self.checkBox.setObjectName("checkBox")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)  # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        """Set the text for the UI elements."""
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("ImageModifierDialog", "Dialog"))
        self.linkButtonSetpath.setText(_translate("ImageModifierDialog", "setPath"))
        self.label.setText(_translate("ImageModifierDialog", "Center"))
        self.label_2.setText(_translate("ImageModifierDialog", "Crop"))
        self.label_3.setText(_translate("ImageModifierDialog", "Size"))
        self.checkBox.setText(_translate("ImageModifierDialog", "8-bit"))
