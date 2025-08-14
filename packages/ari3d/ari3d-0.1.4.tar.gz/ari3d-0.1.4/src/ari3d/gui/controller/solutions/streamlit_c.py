"""Controller for managing the streamlit data viewer dialog in the ari3d application."""
import os
from datetime import datetime
from pathlib import Path

from PyQt6 import QtWidgets
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QDialog, QMessageBox, QWidget

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.gui.controller.io.album_c import AlbumController
from ari3d.gui.controller.io.project_c import OpenProjectController
from ari3d.gui.model.tasks import RunSolutionTask
from ari3d.gui.view.solutions.streamlit_ui import StreamlitDialog


class DataViewerDialogController:
    """Controller for managing the streamlit data viewer dialog in the ari3d application."""

    def __init__(
        self,
        parent: QWidget,
        album_api: AlbumController,
        open_project_dialog_controller: OpenProjectController,
        interactive: bool = True,
    ):
        """Initialize the DataViewerDialogController with the parent widget, album API, and project controller."""
        self.parent = parent
        self.album_api = album_api
        self.project_controller = open_project_dialog_controller
        self.streamlit_window = QDialog()
        self.streamlit_window_ui = StreamlitDialog()
        self.logger = Ari3dLogger()
        self.interactive = interactive
        self.task = None

    def setup_ui(self):
        """Set up the UI for the streamlit data viewer dialog."""
        # Clear the existing layout if it exists
        if self.streamlit_window.layout() is not None:
            QtWidgets.QWidget().setLayout(self.streamlit_window.layout())

        self.streamlit_window_ui.setupUi(self.streamlit_window)
        self.streamlit_window.setWindowTitle("Streamlit Parameters")
        self.set_defaults()
        self.set_connections()

    @property
    def histogram_file(self):
        """Return the path to the histogram file."""
        return self._histogram_file

    def handle_missing_h5ad(self):
        """Handle the case where no histogram files are found."""
        self.logger.log.error(
            "No histogram files found, please ensure the analysis path is correct and try again."
        )
        if self.interactive:
            # show info message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(
                "No histogram files found, please ensure the analysis path is correct and try again."
            )
            msg.setWindowTitle("Info")
            msg.exec()
            self.streamlit_window_ui.buttonBox.button(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
            ).setEnabled(False)

    def load_data_path(self):
        """Load the data path for the streamlit solution."""
        path = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select Data Path",
            directory=str(self.project_controller.analysis_path),
        )

        if not path:
            return

        files = [f for f in os.listdir(path) if f.endswith(".h5ad")]
        if files:
            if self.interactive:
                self.streamlit_window_ui.data_pathTextEdit.setText(path)
                self.streamlit_window_ui.buttonBox.button(
                    QtWidgets.QDialogButtonBox.StandardButton.Ok
                ).setEnabled(True)
        else:
            self.handle_missing_h5ad()

    def load_report_path(self):
        """Load the report path for the streamlit solution."""
        path = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select Report Path",
            directory=str(self.project_controller.report_path),
        )

        if not path:
            return

        if self.interactive:
            self.streamlit_window_ui.report_pathTextEdit.setText(path)

    def load_parameters_file(self):
        """Load the parameters file for the streamlit solution."""
        path = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select Parameters File",
            directory=str(self.project_controller.report_path),
            filter="YML Files (*.yml)",
        )[0]

        if not path:
            return

        if self.interactive:
            self.streamlit_window_ui.parameters_ymlTextEdit.setText(path)

    def set_defaults(self):
        """Set default paths for the streamlit solution dialog."""
        analysis_path = str(self.project_controller.analysis_path)

        if self.interactive:
            self.streamlit_window_ui.data_pathTextEdit.setText(analysis_path)
            self.streamlit_window_ui.report_pathTextEdit.setText(
                str(self.project_controller.report_path)
            )

        parameters_path = None
        if self.project_controller.report_path is not None:
            parameters_path = str(
                self.project_controller.report_path.joinpath("parameters.yml")
            )
            self.streamlit_window_ui.parameters_ymlTextEdit.setText(parameters_path)

            files = [f for f in os.listdir(analysis_path) if f.endswith(".h5ad")]
            if not files:
                self.handle_missing_h5ad()
            else:
                self.streamlit_window_ui.buttonBox.button(
                    QtWidgets.QDialogButtonBox.StandardButton.Ok
                ).setEnabled(True)

        self.logger.log.debug("Setting analysis path to %s" % analysis_path)
        self.logger.log.debug(
            "Setting report path to %s" % str(self.project_controller.report_path)
        )
        self.logger.log.debug("Setting parameters yml path to %s" % parameters_path)

    def set_connections(self):
        """Set up the connections for the streamlit solution dialog."""
        self.streamlit_window_ui.buttonBox.accepted.connect(
            self._run_streamlit_solution
        )
        self.streamlit_window_ui.buttonBox.rejected.connect(
            self.streamlit_window.reject
        )

        # Connect the buttons to the appropriate methods
        self.streamlit_window_ui.data_pathButton.clicked.connect(self.load_data_path)
        self.streamlit_window_ui.report_pathButton.clicked.connect(
            self.load_report_path
        )
        self.streamlit_window_ui.parameters_ymlButton.clicked.connect(
            self.load_parameters_file
        )

    def _run_streamlit_solution(self):
        solution = "de.mdc:data_viewer:0.1.0"

        if self.interactive:
            data_path = self.streamlit_window_ui.data_pathTextEdit.toPlainText()
            report_path = self.streamlit_window_ui.report_pathTextEdit.toPlainText()
            parameter_yml = str(Path(report_path).joinpath("parameters.yml"))
        else:
            data_path = str(self.project_controller.analysis_path)
            report_path = str(self.project_controller.report_path)
            parameter_yml = str(
                self.project_controller.report_path.joinpath("parameters.yml")
            )

        self.logger.log.info(
            "Running streamlit solution with data path %s and report path %s"
            % (data_path, report_path)
        )

        argv = [
            str(os.path.dirname(os.path.realpath(__file__))),
            "--data_path=%s" % str(data_path),
            "--report_path=%s" % str(report_path),
            "--parameter_yml=%s" % parameter_yml,
            "--run_online=%s" % str(self.interactive),
        ]

        self.logger.log.debug(f"Streamlit solution argv: {argv}")

        self.task = RunSolutionTask(self.album_api, solution, argv)

        # Connect the error signal to the handle_error method
        self.task.on_error = self.handle_error

        # connect the finished signal to the handle_segmentation_result method
        self.task.on_finished = self.handle_streamlit_result

        QThreadPool().globalInstance().start(self.task)

    def handle_streamlit_result(self):
        """Handle the result of the streamlit solution execution."""
        output_file = self.project_controller.project_files_path.joinpath(
            "quantification_done.txt"
        )
        with open(output_file, "w") as f:
            f.write(
                f"Quantification successfully done at {self.project_controller.analysis_path}\n"
            )
            f.write(f"Active Zarr file: {self.project_controller.active_zarr_file}\n")
            f.write(f"Date: {str(datetime.now().strftime('%Y%m%d_%H%M%S'))}")

        self.task = None

    def handle_error(self, e):
        """Handle errors that occur during the execution of the streamlit solution."""
        self.logger.log.error(
            f"An error occurred. See the log for further information: {str(e)}"
        )
        if self.interactive:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("An error occurred")
            msg.setInformativeText(str(e))
            msg.setWindowTitle("Error")
            msg.exec()
