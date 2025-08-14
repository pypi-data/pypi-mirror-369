"""Module for Streamlit dialog UI."""
from PyQt6 import QtCore, QtWidgets


class StreamlitDialog:
    """UI class for the Streamlit dialog."""

    def setupUi(self, Dialog):
        """Set up the UI for the Streamlit dialog."""
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 200)

        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")

        self._add_data_path_section(Dialog)
        self._add_report_path_section(Dialog)
        self._add_parameters_file_section(Dialog)
        self._add_button_box(Dialog)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def _add_data_path_section(self, Dialog):
        label = QtWidgets.QLabel(Dialog)
        label.setText("data_path:")
        self.gridLayout.addWidget(label, 0, 0, 1, 1)

        self.data_pathTextEdit = QtWidgets.QTextEdit(Dialog)
        self.data_pathTextEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.data_pathTextEdit, 0, 1, 1, 1)

        button = QtWidgets.QPushButton(Dialog)
        button.setText("Load Data Path")
        button.setToolTip("Path to the data folder")
        self.gridLayout.addWidget(button, 0, 2, 1, 1)
        self.data_pathButton = button

    def _add_report_path_section(self, Dialog):
        label = QtWidgets.QLabel(Dialog)
        label.setText("report_path:")
        self.gridLayout.addWidget(label, 1, 0, 1, 1)

        self.report_pathTextEdit = QtWidgets.QTextEdit(Dialog)
        self.report_pathTextEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.report_pathTextEdit, 1, 1, 1, 1)

        button = QtWidgets.QPushButton(Dialog)
        button.setText("Load Report Path")
        button.setToolTip(
            "Path to the folder where the quantification report should be written"
        )
        self.gridLayout.addWidget(button, 1, 2, 1, 1)
        self.report_pathButton = button

    def _add_parameters_file_section(self, Dialog):
        label = QtWidgets.QLabel(Dialog)
        label.setText("parameters_yml:")
        self.gridLayout.addWidget(label, 2, 0, 1, 1)

        self.parameters_ymlTextEdit = QtWidgets.QTextEdit(Dialog)
        self.parameters_ymlTextEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.parameters_ymlTextEdit, 2, 1, 1, 1)

        button = QtWidgets.QPushButton(Dialog)
        button.setText("Load Parameters File")
        button.setToolTip("Path to the parameters file")
        self.gridLayout.addWidget(button, 2, 2, 1, 1)
        self.parameters_ymlButton = button

    def _add_button_box(self, Dialog):
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText(
            "Run"
        )
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)

    def retranslateUi(self, Dialog):
        """Set the text for the UI elements."""
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Streamlit Parameters"))
