"""Controller for managing the extraction solution of projects in ari3d."""
from __future__ import annotations

import os
from datetime import datetime

from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QDialog, QMessageBox, QWidget
from qtpy import QtCore

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.gui.controller.io.album_c import AlbumController
from ari3d.gui.model.tasks import RunSolutionTask
from ari3d.gui.view.solutions.export_properties_ui import ExportPropertiesDialog


class ExtractPropertiesDialogController:
    """Controller for managing the Extract Properties dialog in ari3d."""

    def _check_project_path(self):
        if self.project_controller.project_path is None:
            raise ValueError("Project path is not set")

    def __init__(
        self,
        parent: QWidget,
        album_api: AlbumController,
        project_controller: OpenProjectController,  # noqa: F821
        interactive: bool = True,
    ):
        """Initialize the Extract Properties dialog controller."""
        self.parent = parent
        self.project_controller = project_controller
        self.output_path = self.project_controller.project_path
        self.album_api = album_api
        self.logger = Ari3dLogger()
        self.extract_histogram = QDialog()
        self.extract_histogram_ui = ExportPropertiesDialog()
        self.interactive = interactive
        self.task = None

        # private attributes
        self._voxel_size = None
        self._background = None
        self._feret_angle = None
        self._mesh_spacing = None
        self._start_slice = None
        self._end_slice = None
        self._remove_small = None
        self._num_threads = None
        self._inertia = None
        self._ferets = None
        self._entropy = None
        self._mean_max = None
        self._aspect_ratio = None
        self._moments = None
        self._euler = None
        self._solidity = None
        self._histograms = None
        self._basic_properties = None
        self._select_all = None

        self.set_defaults_by_parameters()

    def setup_ui(self):
        """Set up the UI for the Extract Properties dialog."""
        self.extract_histogram_ui.setupUi(self.extract_histogram)
        self.extract_histogram.setWindowTitle("Extract Properties")

        self.set_ui_defaults_by_parameters()

        # initialize private attributes with default values from the view
        self._voxel_size = self.extract_histogram_ui.spinBox_5.value()
        self._background = self.extract_histogram_ui.spinBox_6.value()
        self._feret_angle = self.extract_histogram_ui.spinBox_8.value()
        self._mesh_spacing = self.extract_histogram_ui.spinBox_7.value()
        self._start_slice = self.extract_histogram_ui.spinBox_9.value()
        self._end_slice = self.extract_histogram_ui.spinBox_10.value()
        self._remove_small = self.extract_histogram_ui.spinBox_3.value()
        self._num_threads = self.extract_histogram_ui.spinBox_4.value()
        self._inertia = self.extract_histogram_ui.checkBox_34.isChecked()
        self._ferets = self.extract_histogram_ui.checkBox_35.isChecked()
        self._entropy = self.extract_histogram_ui.checkBox_27.isChecked()
        self._mean_max = self.extract_histogram_ui.checkBox_29.isChecked()
        self._aspect_ratio = self.extract_histogram_ui.checkBox_21.isChecked()
        self._moments = self.extract_histogram_ui.checkBox_33.isChecked()
        self._euler = self.extract_histogram_ui.checkBox_36.isChecked()
        self._solidity = self.extract_histogram_ui.checkBox_31.isChecked()

        self.connect_buttons()

    def set_defaults_by_parameters(self):
        """Set the default values for the dialog from the project parameters."""
        if "voxel_size" in self.project_controller.parameters:
            self.voxel_size = self.project_controller.parameters["voxel_size"]

        if "background" in self.project_controller.parameters:
            self.background = self.project_controller.parameters["background"]

        if "feret_angle" in self.project_controller.parameters:
            self.feret_angle = self.project_controller.parameters["feret_angle"]

        if "mesh_spacing" in self.project_controller.parameters:
            self.mesh_spacing = self.project_controller.parameters["mesh_spacing"]

        if "start_slice" in self.project_controller.parameters:
            self.start_slice = self.project_controller.parameters["start_slice"]

        if "end_slice" in self.project_controller.parameters:
            self.end_slice = self.project_controller.parameters["end_slice"]

        if "remove_small" in self.project_controller.parameters:
            self.remove_small = self.project_controller.parameters["remove_small"]

        if "num_threads" in self.project_controller.parameters:
            self.num_threads = self.project_controller.parameters["num_threads"]

        if "inertia" in self.project_controller.parameters:
            self.inertia = self.project_controller.parameters["inertia"]

        if "ferets" in self.project_controller.parameters:
            self.ferets = self.project_controller.parameters["ferets"]

        if "entropy" in self.project_controller.parameters:
            self.entropy = self.project_controller.parameters["entropy"]

        if "mean_max" in self.project_controller.parameters:
            self.mean_max = self.project_controller.parameters["mean_max"]

        if "aspect_ratio" in self.project_controller.parameters:
            self.aspect_ratio = self.project_controller.parameters["aspect_ratio"]

        if "moments" in self.project_controller.parameters:
            self.moments = self.project_controller.parameters["moments"]

        if "euler" in self.project_controller.parameters:
            self.euler = self.project_controller.parameters["euler"]

        if "solidity" in self.project_controller.parameters:
            self.solidity = self.project_controller.parameters["solidity"]

        if "histograms" in self.project_controller.parameters:
            self.histograms = self.project_controller.parameters["histograms"]

        if "basic_properties" in self.project_controller.parameters:
            self.basic_properties = self.project_controller.parameters[
                "basic_properties"
            ]

        if "select_all" in self.project_controller.parameters:
            self.select_all = self.project_controller.parameters["select_all"]

    def set_ui_defaults_by_parameters(self):
        """Set the default values for the dialog UI from the project parameters."""
        if "voxel_size" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_5.setValue(
                self.project_controller.parameters["voxel_size"]
            )

        if "background" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_6.setValue(
                self.project_controller.parameters["background"]
            )

        if "feret_angle" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_8.setValue(
                self.project_controller.parameters["feret_angle"]
            )

        if "mesh_spacing" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_7.setValue(
                self.project_controller.parameters["mesh_spacing"]
            )

        if "start_slice" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_9.setValue(
                self.project_controller.parameters["start_slice"]
            )

        if "end_slice" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_10.setValue(
                self.project_controller.parameters["end_slice"]
            )

        if "remove_small" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_3.setValue(
                self.project_controller.parameters["remove_small"]
            )

        if "num_threads" in self.project_controller.parameters:
            self.extract_histogram_ui.spinBox_4.setValue(
                self.project_controller.parameters["num_threads"]
            )

        if "inertia" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_34.setChecked(
                self.project_controller.parameters["inertia"]
            )

        if "ferets" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_35.setChecked(
                self.project_controller.parameters["ferets"]
            )

        if "entropy" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_27.setChecked(
                self.project_controller.parameters["entropy"]
            )

        if "mean_max" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_29.setChecked(
                self.project_controller.parameters["mean_max"]
            )

        if "aspect_ratio" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_21.setChecked(
                self.project_controller.parameters["aspect_ratio"]
            )

        if "moments" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_33.setChecked(
                self.project_controller.parameters["moments"]
            )

        if "euler" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_36.setChecked(
                self.project_controller.parameters["euler"]
            )

        if "solidity" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_31.setChecked(
                self.project_controller.parameters["solidity"]
            )

        if "histograms" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_37.setChecked(
                self.project_controller.parameters["histograms"]
            )

        if "basic_properties" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_38.setChecked(
                self.project_controller.parameters["basic_properties"]
            )

        if "select_all" in self.project_controller.parameters:
            self.extract_histogram_ui.checkBox_23.setChecked(
                self.project_controller.parameters["select_all"]
            )

    @property
    def voxel_size(self):
        """Get the voxel size."""
        return self._voxel_size

    @voxel_size.setter
    def voxel_size(self, value):
        """Set the voxel size and update the project parameters."""
        self._voxel_size = value
        self.project_controller.parameters["voxel_size"] = value

    @property
    def background(self):
        """Get the background value."""
        return self._background

    @background.setter
    def background(self, value):
        """Set the background value and update the project parameters."""
        self._background = value
        self.project_controller.parameters["background"] = value

    @property
    def feret_angle(self):
        """Get the feret angle."""
        return self._feret_angle

    @feret_angle.setter
    def feret_angle(self, value):
        """Set the feret angle and update the project parameters."""
        self._feret_angle = value
        self.project_controller.parameters["feret_angle"] = value

    @property
    def mesh_spacing(self):
        """Get the mesh spacing."""
        return self._mesh_spacing

    @mesh_spacing.setter
    def mesh_spacing(self, value):
        """Set the mesh spacing and update the project parameters."""
        self._mesh_spacing = value
        self.project_controller.parameters["mesh_spacing"] = value

    @property
    def start_slice(self):
        """Get the start slice."""
        return self._start_slice

    @start_slice.setter
    def start_slice(self, value):
        """Set the start slice and update the project parameters."""
        self._start_slice = value
        self.project_controller.parameters["start_slice"] = value

    @property
    def end_slice(self):
        """Get the end slice."""
        return self._end_slice

    @end_slice.setter
    def end_slice(self, value):
        """Set the end slice and update the project parameters."""
        self._end_slice = value
        self.project_controller.parameters["end_slice"] = value

    @property
    def remove_small(self):
        """Get the remove small value."""
        return self._remove_small

    @remove_small.setter
    def remove_small(self, value):
        """Set the remove small value and update the project parameters."""
        self._remove_small = value
        self.project_controller.parameters["remove_small"] = value

    @property
    def num_threads(self):
        """Get the number of threads."""
        return self._num_threads

    @num_threads.setter
    def num_threads(self, value):
        """Set the number of threads and update the project parameters."""
        self._num_threads = value
        self.project_controller.parameters["num_threads"] = value

    @property
    def inertia(self):
        """Get the inertia property."""
        return self._inertia

    @inertia.setter
    def inertia(self, value):
        """Set the inertia property and update the project parameters."""
        self._inertia = value
        self.project_controller.parameters["inertia"] = value

    @property
    def ferets(self):
        """Get the ferets property."""
        return self._ferets

    @ferets.setter
    def ferets(self, value):
        """Set the ferets property and update the project parameters."""
        self._ferets = value
        self.project_controller.parameters["ferets"] = value

    @property
    def entropy(self):
        """Get the entropy property."""
        return self._entropy

    @entropy.setter
    def entropy(self, value):
        """Set the entropy property and update the project parameters."""
        self._entropy = value
        self.project_controller.parameters["entropy"] = value

    @property
    def mean_max(self):
        """Get the mean max property."""
        return self._mean_max

    @mean_max.setter
    def mean_max(self, value):
        """Set the mean max property and update the project parameters."""
        self._mean_max = value
        self.project_controller.parameters["mean_max"] = value

    @property
    def aspect_ratio(self):
        """Get the aspect ratio property."""
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        """Set the aspect ratio property and update the project parameters."""
        self._aspect_ratio = value
        self.project_controller.parameters["aspect_ratio"] = value

    @property
    def moments(self):
        """Get the moments property."""
        return self._moments

    @moments.setter
    def moments(self, value):
        """Set the moments property and update the project parameters."""
        self._moments = value
        self.project_controller.parameters["moments"] = value

    @property
    def euler(self):
        """Get the Euler number property."""
        return self._euler

    @euler.setter
    def euler(self, value):
        """Set the Euler number property and update the project parameters."""
        self._euler = value
        self.project_controller.parameters["euler"] = value

    @property
    def solidity(self):
        """Get the solidity property."""
        return self._solidity

    @solidity.setter
    def solidity(self, value):
        """Set the solidity property and update the project parameters."""
        self._solidity = value
        self.project_controller.parameters["solidity"] = value

    @property
    def histograms(self):
        """Get the histograms property."""
        return self._histograms

    @histograms.setter
    def histograms(self, value):
        """Set the histograms property and update the project parameters."""
        self._histograms = value
        self.project_controller.parameters["histograms"] = value

    @property
    def basic_properties(self):
        """Get the basic properties flag."""
        return self._basic_properties

    @basic_properties.setter
    def basic_properties(self, value):
        """Set the basic properties flag and update the project parameters."""
        self._basic_properties = value
        self.project_controller.parameters["basic_properties"] = value

    @property
    def select_all(self):
        """Get the select all flag."""
        return self._select_all

    @select_all.setter
    def select_all(self, value):
        """Set the select all flag and update the project parameters."""
        self._select_all = value
        self.project_controller.parameters["select_all"] = value

    # ## Inputs Changes ###

    def on_voxel_size_change(self, value):
        """Handle changes to the voxel size input."""
        self.voxel_size = value

    def on_background_change(self, value):
        """Handle changes to the background input."""
        self.background = value

    def on_feret_angle_change(self, value):
        """Handle changes to the feret angle input."""
        self.feret_angle = value

    def on_mesh_spacing_change(self, value):
        """Handle changes to the mesh spacing input."""
        self.mesh_spacing = value

    def on_start_slice_change(self, value):
        """Handle changes to the start slice input."""
        self.start_slice = value

    def on_end_slice_change(self, value):
        """Handle changes to the end slice input."""
        self.end_slice = value

    def on_remove_small_change(self, value):
        """Handle changes to the remove small input."""
        self.remove_small = value

    def on_num_threads_change(self, value):
        """Handle changes to the number of threads input."""
        self.num_threads = value

    def _check_input(self):
        if self.project_controller.project_path is None:
            return False

        return True

    # ### Input Button Clicks ####
    def on_extract_properties_click(self):
        """Handle the click event for the extract properties button."""
        if not self._check_input():
            self.logger.log.error("No Project opened! Cannot extract properties!")
            if self.interactive:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Please open a project first!")
                msg.setWindowTitle("Error")
                msg.exec()
            return

        self.logger.log.info("Extracting properties...")

        if (
            self._start_slice != -1
            and self._end_slice == -1
            or self._start_slice == -1
            and self._end_slice != -1
        ):
            self.logger.log.error("Both start and end slice must be set")
            if self.interactive:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Both start and end slice must be set")
                msg.setWindowTitle("Error")
                msg.exec()
            return

        # build the arguments for the solution
        args_dict = {
            "path": self.project_controller.project_path,
            "Size_threshold": self._remove_small,
            "numberTreads": self._num_threads,
            "Stepsize": self._mesh_spacing,
            # "voxel_spacing": self._mesh_spacing,
            "Angle_spacing": self._feret_angle,
            "Voxel_size": self._voxel_size,
            "Background_mean": self._background,
            "start_slice": self._start_slice,
            "end_slice": self._end_slice,
            "properties_list": "label,area,min_intensity,max_intensity,equivalent_diameter,mean_intensity,bbox,centroid",  # noqa: E501
        }

        argv = [str(os.path.dirname(os.path.realpath(__file__)))]

        # iterate through dict and add key value pairs to argv
        for key, value in args_dict.items():
            argv.append(f"--{key}={value}")

        # build the arguments for the solution
        self.logger.log.debug("Creating solution task...")
        solution = "de.mdc:property_extraction:0.1.0"
        self.task = RunSolutionTask(self.album_api, solution, argv)

        # Connect the error signal to the handle_error method
        self.task.on_error = self.handle_error

        # connect the finished signal to the handle_segmentation_result method
        self.task.on_finished = self.handle_properties_result

        self.logger.log.debug("Running task...")

        if self.interactive:
            self.extract_histogram_ui.pushButton_2.setEnabled(False)

        QThreadPool().globalInstance().start(self.task)

    def handle_properties_result(self):
        """Handle the result of the properties extraction task."""
        self.logger.log.info("Properties extraction finished")
        self.project_controller.save_parameters()

        if self.interactive:
            self.extract_histogram_ui.pushButton_2.setEnabled(True)

        self.task = None

        # create results file for snakemake
        output_file = self.project_controller.project_files_path.joinpath(
            "histogram_created.txt"
        )
        with open(output_file, "w") as f:
            f.write(
                f"Segmentation extracted histograms at {self.project_controller.analysis_path}\n"
            )
            f.write(f"Active Zarr file: {self.project_controller.active_zarr_file}\n")
            f.write(f"Date: {str(datetime.now().strftime('%Y%m%d_%H%M%S'))}")

    def handle_error(self, e: Exception):
        """Handle errors that occur during the extraction process."""
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
            self.extract_histogram_ui.pushButton_2.setEnabled(True)

    def on_cancel_click(self):
        """Handle the click event for the cancel button."""
        self.extract_histogram.close()

    # ## Property Checkboxes ###

    def on_inertia_change(self, value):
        """Handle changes to the inertia checkbox."""
        self.inertia = value

    def on_ferets_change(self, value):
        """Handle changes to the ferets checkbox."""
        self.ferets = value

    def on_entropy_change(self, value):
        """Handle changes to the entropy checkbox."""
        self.entropy = value

    def on_mean_max_change(self, value):
        """Handle changes to the mean max checkbox."""
        self.mean_max = value

    def on_aspect_ratio_change(self, value):
        """Handle changes to the aspect ratio checkbox."""
        self.aspect_ratio = value

    def on_moments_change(self, value):
        """Handle changes to the moments checkbox."""
        self.moments = value

    def on_euler_change(self, value):
        """Handle changes to the Euler number checkbox."""
        self.euler = value

    def on_solidity_change(self, value):
        """Handle changes to the solidity checkbox."""
        self.solidity = value

    # ### Checkbox Clicks ####

    def on_basic_properties_click(self, state):
        """Handle changes to the basic properties checkbox."""
        self.basic_properties = state == QtCore.Qt.CheckState.Checked

    def on_histograms_click(self, state):
        """Handle changes to the histograms checkbox."""
        self.histograms = state == QtCore.Qt.CheckState.Checked

    def on_select_all_click(self, state):
        """Handle changes to the select all checkbox."""
        self.select_all = state
        checkboxes = [
            (self.extract_histogram_ui.checkBox_34, self.on_inertia_change),
            (self.extract_histogram_ui.checkBox_35, self.on_ferets_change),
            (self.extract_histogram_ui.checkBox_27, self.on_entropy_change),
            (self.extract_histogram_ui.checkBox_29, self.on_mean_max_change),
            (self.extract_histogram_ui.checkBox_21, self.on_aspect_ratio_change),
            (self.extract_histogram_ui.checkBox_33, self.on_moments_change),
            (self.extract_histogram_ui.checkBox_36, self.on_euler_change),
            (self.extract_histogram_ui.checkBox_31, self.on_solidity_change),
        ]
        for checkbox, change_function in checkboxes:
            checkbox.setChecked(state)
            change_function(state)

    def connect_buttons(self):
        """Connect the buttons and checkboxes to their respective methods."""
        # ## Name to function mapping
        # input
        # spinBox_5 = voxel_size
        # spinBox_6 = background
        # spinBox_8 = feret_angle
        # spinBox_7 = mesh_spacing
        # spinBox_9 = start_slice
        # spinBox_10 = end_slice
        # spinBox_3 = remove_small
        # spinBox_4 = num_threads

        # checkBox_24 = save_labels
        # checkBox_5 = inclusions

        # output
        # checkBox_34 = inertia
        # checkBox_35 = ferets
        # checkBox_27 = entropy
        # checkBox_29 = mean_max
        # checkBox_21 = aspect_ratio
        # checkBox_33 = moments
        # checkBox_36 = euler
        # checkBox_31 = solidity

        # checkBox_37 = histograms
        # checkBox_38 = basic_properties
        # checkBox_23 = select_all

        # buttons
        # pushButton = subdataset
        # pushButton_2 = all_data
        # pushButton_3 = cancel

        # Input SpinBoxes
        self.extract_histogram_ui.spinBox_5.valueChanged.connect(
            self.on_voxel_size_change
        )
        self.extract_histogram_ui.spinBox_6.valueChanged.connect(
            self.on_background_change
        )
        self.extract_histogram_ui.spinBox_8.valueChanged.connect(
            self.on_feret_angle_change
        )
        self.extract_histogram_ui.spinBox_7.valueChanged.connect(
            self.on_mesh_spacing_change
        )
        self.extract_histogram_ui.spinBox_9.valueChanged.connect(
            self.on_start_slice_change
        )
        self.extract_histogram_ui.spinBox_10.valueChanged.connect(
            self.on_end_slice_change
        )
        self.extract_histogram_ui.spinBox_3.valueChanged.connect(
            self.on_remove_small_change
        )
        self.extract_histogram_ui.spinBox_4.valueChanged.connect(
            self.on_num_threads_change
        )

        # Input Buttons
        # self.extract_histogram_ui.pushButton.clicked.connect(self.on_subdataset_click)
        self.extract_histogram_ui.pushButton_2.clicked.connect(
            self.on_extract_properties_click
        )
        self.extract_histogram_ui.pushButton_3.clicked.connect(self.on_cancel_click)

        # Checkboxes
        self.extract_histogram_ui.checkBox_34.stateChanged.connect(
            self.on_inertia_change
        )
        self.extract_histogram_ui.checkBox_35.stateChanged.connect(
            self.on_ferets_change
        )
        self.extract_histogram_ui.checkBox_27.stateChanged.connect(
            self.on_entropy_change
        )
        self.extract_histogram_ui.checkBox_29.stateChanged.connect(
            self.on_mean_max_change
        )
        self.extract_histogram_ui.checkBox_21.stateChanged.connect(
            self.on_aspect_ratio_change
        )
        self.extract_histogram_ui.checkBox_33.stateChanged.connect(
            self.on_moments_change
        )
        self.extract_histogram_ui.checkBox_36.stateChanged.connect(self.on_euler_change)
        self.extract_histogram_ui.checkBox_31.stateChanged.connect(
            self.on_solidity_change
        )

        # Checkboxes that affect other checkboxes
        self.extract_histogram_ui.checkBox_37.stateChanged.connect(
            self.on_histograms_click
        )
        self.extract_histogram_ui.checkBox_38.stateChanged.connect(
            self.on_basic_properties_click
        )
        self.extract_histogram_ui.checkBox_23.stateChanged.connect(
            self.on_select_all_click
        )
