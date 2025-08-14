"""Controller for managing the particle segmentation solution in the ari3d application."""
import json
import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import requests
import zarr
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QWidget

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.gui.controller.io.album_c import AlbumController
from ari3d.gui.controller.io.project_c import OpenProjectController
from ari3d.gui.controller.io.view_c import ImageViewController
from ari3d.gui.model.tasks import RunSolutionTask
from ari3d.gui.view.solutions.particleSegWindow_ui import UI_ParticleSeg3DPredict
from ari3d.gui.view.solutions.particleSegWindow_ui_advanced import (
    UI_ParticleSeg3DAdvanced,
)
from ari3d.utils.conversion import zarr2float
from ari3d.utils.operations.file_operations import copy_folder


def _list_models():
    # create folder if not exists:
    if not os.path.exists(CUR_MODELS_DIR):
        os.makedirs(CUR_MODELS_DIR)

    # get all folders in the models directory
    return [
        f
        for f in os.listdir(CUR_MODELS_DIR)
        if os.path.isdir(os.path.join(CUR_MODELS_DIR, f))
    ]


MAX_INT = 2147483647

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
CUR_MODELS_DIR = Path(CUR_DIR).parent.parent.parent.joinpath("resources", "models")
CUR_MODELS = _list_models()
DEFAULT_MODEL_URL = "https://syncandshare.desy.de/index.php/s/id9D9pkATrFw65s/download/Task310_particle_seg.zip"
SOURCE_SPACING = 0.1
SOURCE_PARTICLE_SIZE = 1.0

SOLUTION_DEFAULTS = {
    "_input": "",  # manually set
    "_output": "",  # commandLinkButton
    "_model": CUR_MODELS_DIR,
    "_name": "",
    "_zscore": "5850.29762143569 7078.294543817302",  # VALUE MODEL TRAINED ON - DO NOT CHANGE - THIS IS NOT A USER INPUT  # noqa
    "_target_particle_size": 60,  # VALUE MODEL TRAINED ON - DO NOT CHANGE - THIS IS NOT A USER INPUT - see source_particle_size for input  # noqa
    "_target_spacing": 0.1,  # VALUE MODEL TRAINED ON - DO NOT CHANGE - THIS IS NOT A USER INPUT - see source_spacing for input  # noqa
    "_fold": "0 1 2 3 4",
    "_batch_size": 6,
    "_processes": 4,
    "_min_rel_particle_size": 0.005,  # VALUE MODEL TRAINED ON - DO NOT CHANGE - THIS IS NOT A USER INPUT
}


class UI_ParticleSeg3DBaseController:
    """Base controller for the ParticleSeg3D solution in the ari3d application."""

    def __init__(
        self,
        parent: QWidget,
        album_api: AlbumController,
        open_project_dialog: OpenProjectController,
        image_view_controller: ImageViewController,
        interactive: bool = True,
    ):
        """Initialize the ParticleSeg3D controller with the necessary parameters."""
        self.parent = parent
        self.logger = Ari3dLogger()
        self.open_project_dialog = open_project_dialog
        self.image_view_controller = image_view_controller
        self.album_api = album_api
        self.interactive = interactive  # whether to show dialogs or not
        self.particle_seg_window = None

        self._particle_seg_input = ""

        # solution arguments
        self._input = SOLUTION_DEFAULTS["_input"]
        self._output = SOLUTION_DEFAULTS["_output"]
        self._model = SOLUTION_DEFAULTS["_model"]
        self._name = SOLUTION_DEFAULTS["_name"]
        self._zscore = SOLUTION_DEFAULTS["_zscore"]
        self._target_particle_size_target_particle_size = SOLUTION_DEFAULTS[
            "_target_particle_size"
        ]
        self._target_spacing = SOLUTION_DEFAULTS["_target_spacing"]
        self._fold = SOLUTION_DEFAULTS["_fold"]
        self._batch_size = SOLUTION_DEFAULTS["_batch_size"]
        self._processes = SOLUTION_DEFAULTS["_processes"]
        self._min_rel_particle_size = SOLUTION_DEFAULTS["_min_rel_particle_size"]
        self._save_tiff = True

        # metadata parameters
        self._source_spacing = None
        self._source_particle_size = None

    def download_default_model(self):
        """Download the default model from the specified URL."""
        response = requests.get(DEFAULT_MODEL_URL, stream=True)
        # to update the download progress bar, we need to know the total
        # size of the file and iterate over the response in chunks
        total_size_in_bytes = int(response.headers.get("content-length", 0))

        # Calculate the scaling factor
        scaling_factor = 1
        if total_size_in_bytes > MAX_INT:
            scaling_factor = total_size_in_bytes // MAX_INT + 1

        # Create a QProgressDialog instance
        if self.interactive:
            progress_dialog = QProgressDialog(
                "Downloading...",
                "Cancel",
                0,
                total_size_in_bytes // scaling_factor,
                self.particle_seg_window,
            )
            progress_dialog.setWindowTitle("Download Progress")
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.show()

        bytes_downloaded = 0
        with open(CUR_MODELS_DIR / "Task310_particle_seg.zip", "wb") as f:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                bytes_downloaded += len(data)

                # Update the progress dialog
                if self.interactive:
                    progress_dialog.setValue(bytes_downloaded // scaling_factor)

                    # Check if the Cancel button was clicked
                    if progress_dialog.wasCanceled():
                        break
                else:
                    # If not interactive, just log the progress
                    if (
                        bytes_downloaded % (10000 * 1024 * scaling_factor) == 0
                    ):  # log every 100 MB
                        self.logger.log.info(
                            f"Downloaded {bytes_downloaded // scaling_factor} of {total_size_in_bytes // scaling_factor} bytes"  # noqa: E501
                        )

        # Close the progress dialog
        if self.interactive:
            progress_dialog.close()

        # UnZip the model
        with ZipFile(CUR_MODELS_DIR / "Task310_particle_seg.zip", "r") as zip_ref:
            zip_ref.extractall(CUR_MODELS_DIR)
        (CUR_MODELS_DIR / "Task310_particle_seg.zip").unlink()


class UI_ParticleSeg3DPredictController(UI_ParticleSeg3DBaseController):
    """Controller for the ParticleSeg3D prediction solution in the ari3d application."""

    def __init__(
        self,
        parent: QWidget,
        album_api: AlbumController,
        open_project_dialog: OpenProjectController,
        image_view_controller: ImageViewController,
        interactive: bool = True,
    ):
        """Initialize the ParticleSeg3D prediction controller with the necessary parameters."""
        super().__init__(
            parent, album_api, open_project_dialog, image_view_controller, interactive
        )
        self.particle_seg_window_ui = UI_ParticleSeg3DPredict()
        self.task = None

    def setup_ui(self):
        """Set up the UI for the ParticleSeg3D prediction dialog."""
        self.particle_seg_window = QtWidgets.QDialog()
        self.particle_seg_window_ui.setupUi(self.particle_seg_window)
        self.particle_seg_window.setWindowTitle("ParticleSeg3D Parameters")

        # check if model dir empty
        if not CUR_MODELS:
            reply = QMessageBox.question(
                self.particle_seg_window,
                "Model Not Found",
                "No model was found. Do you want to download the default model?"
                " This might take some time but will only be done once?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.download_default_model()

        self.set_defaults_by_parameters()

        # set UI defaults
        _cur_models_list = CUR_MODELS.copy()
        if self.particle_seg_window_ui.model_name_box.count() > 0:
            _added_items = [
                self.particle_seg_window_ui.model_name_box.itemText(i)
                for i in range(self.particle_seg_window_ui.model_name_box.count())
            ]
            for x in _added_items:
                if x in _cur_models_list:
                    _cur_models_list.remove(x)
        self.particle_seg_window_ui.model_name_box.addItems(
            [os.path.basename(x) for x in _cur_models_list]
        )

        self.link_buttons()

        # non-parameter defaults
        self.set_defaults()

    def set_defaults_by_parameters(self):
        """Set defaults based on the parameters from the open project dialog."""
        if "model_path" in self.open_project_dialog.parameters:
            if self.open_project_dialog.parameters["model_path"] in CUR_MODELS:
                self.particle_seg_window_ui.model_name_box.addItem(
                    self.open_project_dialog.parameters["model_path"]
                )

        if "average_particle_size_mm" in self.open_project_dialog.parameters:
            self.particle_seg_window_ui.particle_size_box.setValue(
                self.open_project_dialog.parameters["average_particle_size_mm"]
            )

        if "voxel_size_mm" in self.open_project_dialog.parameters:
            self.particle_seg_window_ui.voxel_size_box.setValue(
                self.open_project_dialog.parameters["voxel_size_mm"]
            )

        if "save_seg_labels" in self.open_project_dialog.parameters:
            self.particle_seg_window_ui.save_label.setChecked(
                self.open_project_dialog.parameters["save_seg_labels"]
            )

        if "apply_to_slice" in self.open_project_dialog.parameters:
            pass  # todo: implement me

    def set_defaults(self):
        """Set default values for the ParticleSeg3D parameters."""
        if not self.interactive:
            global CUR_MODELS
            # download model
            if len(CUR_MODELS) == 0:
                self.download_default_model()
                CUR_MODELS = _list_models()

        if self.open_project_dialog.active_zarr_file_altered is not None:
            self._particle_seg_input = self.open_project_dialog.active_zarr_file_altered
        elif self.open_project_dialog.active_zarr_file is not None:
            self._particle_seg_input = self.open_project_dialog.active_zarr_file
        else:
            self._particle_seg_input = ""
        self._model = (
            os.path.join(CUR_MODELS_DIR, CUR_MODELS[0]) if len(CUR_MODELS) >= 1 else ""
        )
        self._output = self.open_project_dialog.particle_seg_path

        self._source_spacing = (
            self.open_project_dialog.parameters["voxel_size_mm"]
            if "voxel_size_mm" in self.open_project_dialog.parameters
            else SOURCE_SPACING
        )
        self._source_particle_size = (
            self.open_project_dialog.parameters["average_particle_size_mm"]
            if "average_particle_size_mm" in self.open_project_dialog.parameters
            else SOURCE_PARTICLE_SIZE
        )

        # print debug information
        self.logger.log.debug("Setting defaults for ParticleSeg3D:")
        self.logger.log.debug(f"Input: {self._particle_seg_input}")
        self.logger.log.debug(f"Output: {self._output}")
        self.logger.log.debug(f"Model: {self._model}")
        self.logger.log.debug(f"Source Spacing: {self._source_spacing}")
        self.logger.log.debug(f"Source Particle Size: {self._source_particle_size}")

    def _check_input(self):
        self.logger.log.debug("Checking input...")
        if not self.particle_seg_input:
            if self.interactive:
                QMessageBox.information(
                    self.particle_seg_window,
                    "Information",
                    "Please specify the input image path.",
                )
            self.logger.log.error("No input image path specified!")
            return False

        if self.save_tiff:
            if not self.output:
                if self.interactive:
                    QMessageBox.information(
                        self.particle_seg_window,
                        "Information",
                        "Please specify the output path.",
                    )
                self.logger.log.error("No output path specified!")
                return False

        # check if viewer is open
        if self.interactive:
            if self.image_view_controller.viewer is None:
                QMessageBox.information(
                    self.particle_seg_window,
                    "Information",
                    "Please open an image first.",
                )
                self.logger.log.error("No image viewer open!")
                return False

        if ".particle_seg" in str(self.particle_seg_input):
            if self.interactive:
                QMessageBox.information(
                    self.particle_seg_window,
                    "Information",
                    'Do not specify ".particle_seg" as input folder!',
                )
            self.logger.log.error('Input folder should not contain ".particle_seg"!')
            return False

        return True

    def _prepare_input(self):
        self.logger.log.info("Preparing input...")
        # todo: replace me with link structure in the future. why should we copy stuff?
        # copy input to hidden .particle_seg folder
        if os.path.exists(self.particle_seg_input):
            # ensure float dtype for input
            d = zarr.open(str(self.particle_seg_input), mode="r")
            if d.dtype != float:
                zarr2float(
                    self.particle_seg_input,
                    self.open_project_dialog.particle_seg_image_path,
                )
            else:
                copy_folder(
                    self.particle_seg_input,
                    self.open_project_dialog.particle_seg_image_path,
                )

            # necessary because particle seq expects the input to be in a folder in a certain format
            self._input = self.open_project_dialog.particle_seg_path
        self.logger.log.info("Done preparing input!")

    def _check_output_exists(self):
        # if the output of the segmentation already exists ask whether to re-compute - else load result
        if (
            self.output.joinpath(self.open_project_dialog.project_path.stem)
            .joinpath(self.open_project_dialog.project_path.stem + ".zarr")
            .exists()
        ):
            reply = QMessageBox.question(
                self.particle_seg_window,
                "Output Exists",
                "The output folder already exists. Do you want to use these results?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.handle_particle_seg_result()
                return True
        return False

    def _run_particlseSeg3d_solution(self):
        check = self._check_input()
        if not check:
            return

        if self.interactive:
            if self._check_output_exists():
                self.particle_seg_window.hide()
                return

        self._prepare_input()

        self.logger.log.debug("Building solution arguments...")
        argv = [str(os.path.dirname(os.path.realpath(__file__)))]
        for attr in dir(self):
            if attr.startswith("_") and attr in SOLUTION_DEFAULTS.keys():
                value = getattr(self, attr)
                if value != "":
                    # special case for model:
                    if attr == "_model":
                        value = str(CUR_MODELS_DIR.joinpath(value))
                    argv.append(f"--{attr[1:]}={value}")

        # treat special save_tiff case
        if self.save_tiff:
            argv.append(f"--save_tiff={str(self.open_project_dialog.masks_folder)}")

        self.logger.log.debug("Arguments: %s" % argv)

        metadata_path = os.path.join(Path(self._input), "metadata.json")
        self.logger.log.debug("Metadata path: %s" % metadata_path)

        self.logger.log.info("Creating metadata file...")
        self.create_project_metadata_file(metadata_path)

        self.logger.log.debug("Creating solution task...")
        solution = "de.mdc:particleSeg3D-predict:0.1.0"
        self.task = RunSolutionTask(self.album_api, solution, argv)

        # Connect the error signal to the handle_error method
        self.task.on_error = self.handle_error

        # connect the finished signal to the handle_segmentation_result method
        self.task.on_finished = self.handle_particle_seg_result

        self.logger.log.debug("Running task...")

        if self.interactive:
            self.particle_seg_window_ui.pushButton_2.setEnabled(False)

        QThreadPool().globalInstance().start(self.task)

    def create_project_metadata_file(self, metadata_path: Path):
        """Create a metadata file for the project with the necessary parameters."""
        with open(metadata_path, "w") as json_file:
            json.dump(
                {
                    self._particle_seg_input.stem: {
                        "spacing": self.source_spacing,
                        "particle_size": self.source_particle_size,
                    }
                },
                json_file,
                indent=4,
            )
        self.logger.log.info("Metadata file created.")
        with open(metadata_path) as f:
            self.logger.log.debug("Metadata file content: %s" % json.load(f))

    def handle_error(self, e: Exception):
        """Handle errors that occur during the ParticleSeg3D solution execution."""
        self.logger.log.error(
            f"An error occurred. See the log for further information: {str(e)}"
        )

        if self.interactive:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("An error occurred")
            msg.setInformativeText(
                "An error occurred. See the log for further information."
            )
            msg.setWindowTitle("Error")
            msg.exec()

            # enable the button again
            self.particle_seg_window_ui.pushButton_2.setEnabled(True)

    def handle_particle_seg_result(self):
        """Handle the result of the ParticleSeg3D solution execution."""
        if self.interactive:
            zarr_name = Path(self._particle_seg_input).stem + ".zarr"

            # yes, this is in a subfolder
            out_zarr = Path(self.output).joinpath(
                Path(self._particle_seg_input).stem, zarr_name
            )

            if out_zarr.exists():
                # Load Zarr file in output and treat as mask
                data = zarr.open(str(out_zarr), mode="r")
                self.image_view_controller.overlay_instance_segmentation_result(data)
            else:
                QMessageBox.information(
                    self.particle_seg_window,
                    "Information",
                    "No segmentation result found! Consider running ParticleSeg3D first.",
                )

            # enable the button again
            self.particle_seg_window_ui.pushButton_2.setEnabled(True)

        self.open_project_dialog.save_parameters()

        # create output file for snakemake
        output_file = self.open_project_dialog.project_files_path.joinpath(
            "segmentation_created.txt"
        )
        with open(output_file, "w") as f:
            f.write(
                f"Segmentation created successfully at {self.open_project_dialog.masks_folder}\n"
            )
            f.write(f"Active Zarr file: {self.open_project_dialog.active_zarr_file}\n")
            f.write(f"Date: {str(datetime.now().strftime('%Y%m%d_%H%M%S'))}")

        self.task = None  # reset task

    @property
    def particle_seg_input(self):
        """Get the particle segmentation input path."""
        return self._particle_seg_input

    def _on_input_clicked(self):
        # open input dialog
        directory = QFileDialog.getExistingDirectory(
            self.particle_seg_window, "Select a folder"
        )
        if directory:  # if a directory was selected
            self._particle_seg_input = directory

    # ## output
    @property
    def output(self):
        """Get the output path for the particle segmentation."""
        return self._output

    @output.setter
    def output(self, value):
        """Set the output path for the particle segmentation."""
        self._output = value

    def _on_output_clicked(self):
        # open input dialog
        directory = QFileDialog.getExistingDirectory(
            self.particle_seg_window, "Select a folder"
        )
        if directory:  # if a directory was selected
            self.output = Path(directory)

    # ## model
    @property
    def model(self):
        """Get the model path for the particle segmentation."""
        return self._model

    @model.setter
    def model(self, value):
        """Set the model path for the particle segmentation."""
        self._model = value
        self.open_project_dialog.parameters["model_path"] = value

    def _on_model_changed(self, new_text: str):
        self._model = new_text

    # ## target particle size
    @property
    def target_particle_size(self):
        """Get the target particle size for the particle segmentation."""
        return self._target_particle_size

    @target_particle_size.setter
    def target_particle_size(self, value):
        """Set the target particle size for the particle segmentation."""
        self._target_particle_size = value

    # ## source particle size <- this value is important for prediction
    @property
    def source_particle_size(self):
        """Get the source particle size for the particle segmentation."""
        return self._source_particle_size

    @source_particle_size.setter
    def source_particle_size(self, value):
        """Set the source particle size for the particle segmentation."""
        self._source_particle_size = value
        self.open_project_dialog.parameters["average_particle_size_mm"] = value

    def _on_particle_size_box_changed(self, new_value):
        self.source_particle_size = new_value

    # ## target spacing
    @property
    def target_spacing(self):
        """Get the target spacing for the particle segmentation."""
        return self._target_spacing

    @target_spacing.setter
    def target_spacing(self, value):
        """Set the target spacing for the particle segmentation."""
        self._target_spacing = value

    # ## source spacing <- this value is important for prediction
    @property
    def source_spacing(self):
        """Get the source spacing for the particle segmentation."""
        return self._source_spacing

    @source_spacing.setter
    def source_spacing(self, value):
        """Set the source spacing for the particle segmentation."""
        self._source_spacing = value
        self.open_project_dialog.parameters["voxel_size_mm"] = value

    def _on_source_spacing_changed(self, new_value: str):
        self.source_spacing = float(new_value)

    # ## save tiff
    @property
    def save_tiff(self):
        """Get whether to save the segmentation labels as TIFF."""
        return self._save_tiff

    @save_tiff.setter
    def save_tiff(self, value):
        """Set whether to save the segmentation labels as TIFF."""
        self._save_tiff = value
        self.open_project_dialog.parameters["save_seg_labels"] = value

    def _on_save_label_changed(self, new_value):
        self.save_tiff = new_value

    def link_buttons(self):
        """Link the buttons in the ParticleSeg3D dialog to their respective methods."""
        self.particle_seg_window_ui.save_label_path.clicked.connect(
            self._on_output_clicked
        )
        self.particle_seg_window_ui.input_image_button.clicked.connect(
            self._on_input_clicked
        )
        self.particle_seg_window_ui.save_label.stateChanged.connect(
            self._on_save_label_changed
        )
        self.particle_seg_window_ui.particle_size_box.valueChanged.connect(
            self._on_particle_size_box_changed
        )
        self.particle_seg_window_ui.voxel_size_box.valueChanged.connect(
            self._on_source_spacing_changed
        )
        self.particle_seg_window_ui.model_name_box.currentTextChanged.connect(
            self._on_model_changed
        )

        # OK and Cancel button
        self.particle_seg_window_ui.pushButton_2.clicked.connect(
            self._run_particlseSeg3d_solution
        )
        self.particle_seg_window_ui.pushButton_3.clicked.connect(
            self.particle_seg_window.reject
        )


class UI_ParticleSeg3DAdvancedController(UI_ParticleSeg3DBaseController):
    """Controller for the advanced parameters of the ParticleSeg3D solution in the ari3d application."""

    def __init__(
        self,
        parent: QWidget,
        album_api: AlbumController,
        open_project_dialog: OpenProjectController,
        image_view_controller: ImageViewController,
    ):
        """Initialize the ParticleSeg3D advanced parameters controller with the necessary parameters."""
        super().__init__(parent, album_api, open_project_dialog, image_view_controller)
        self.particle_seg_window_ui = UI_ParticleSeg3DAdvanced()

    def setup_ui(self):
        """Set up the UI for the ParticleSeg3D advanced parameters dialog."""
        self.particle_seg_window_ui.setupUi(self.particle_seg_window)
        self.particle_seg_window.setWindowTitle("ParticleSeg3D Advanced Parameters")

    @property
    def input(self):  # noqa: A003
        """Get the input path for the particle segmentation."""
        # take from open image if it is loaded else from the input field
        if self.open_project_dialog.project_path is not None:
            return self.open_project_dialog.project_path

        return self._input

    @property
    def output(self):
        """Get the output path for the particle segmentation."""
        return self._output

    @property
    def model(self):
        """Get the model path for the particle segmentation."""
        return self._model

    @property
    def name(self):
        """Get the name of the particle segmentation."""
        return self._name

    @property
    def zscore(self):
        """Get the z-score for the particle segmentation."""
        return self._zscore

    @property
    def target_particle_size(self):
        """Get the target particle size for the particle segmentation."""
        return self._target_particle_size

    @property
    def target_spacing(self):
        """Get the target spacing for the particle segmentation."""
        return self._target_spacing

    @property
    def fold(self):
        """Get the fold for the particle segmentation."""
        return self._fold

    @property
    def batch_size(self):
        """Get the batch size for the particle segmentation."""
        return self._batch_size

    @property
    def processes(self):
        """Get the number of processes for the particle segmentation."""
        return self._processes

    @property
    def min_rel_particle_size(self):
        """Get the minimum relative particle size for the particle segmentation."""
        return self._min_rel_particle_size

    @property
    def save_tiff(self):
        """Get whether to save the segmentation labels as TIFF."""
        return self._save_tiff
