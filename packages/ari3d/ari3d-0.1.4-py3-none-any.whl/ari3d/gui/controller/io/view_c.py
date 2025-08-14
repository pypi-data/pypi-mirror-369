"""File to run the data viewer window and give connections to menu items."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import napari
import numpy as np
import pandas as pd
import skimage
import tifffile
import zarr
from napari.utils import DirectLabelColormap
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGraphicsScene,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSlider,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)
from watchdog.observers import Observer

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.gui.controller.io.project_c import OpenProjectController
from ari3d.gui.model.watcher import FileWatcher
from ari3d.gui.view.io.file import ImageModifierDialog
from ari3d.resources.default_values import DefaultValues
from ari3d.utils.operations.image_operations import center_crop, center_pad


class ParticleHighlight(QWidget):
    """Widget for the highlighted particles in napari viewer."""

    def __init__(self, image_view_controller, logger=None):
        """Construct the ParticleHighlight object."""
        super().__init__()
        # Set size policy to expanding
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self.logger = logger
        self.image_view_controller = image_view_controller

        # set the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scene = QGraphicsScene()

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(1)  # Set the number of columns to 1
        self.table_widget.setHorizontalHeaderLabels(
            ["Label Index"]
        )  # Set the header label
        self.table_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )

        row_height = self.table_widget.verticalHeader().defaultSectionSize()
        header_height = self.table_widget.horizontalHeader().defaultSectionSize()
        self.table_widget.setMinimumHeight(6 * row_height + header_height)

        self.label_control = QLabel("Highlighted Particles:")
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.table_widget)

        # build layout
        self._build_layout()
        self._connect()

    def _connect(self):
        self.table_widget.cellClicked.connect(self.on_table_item_click)

    def _build_layout(self):
        vbox_input = QVBoxLayout()
        vbox_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        vbox_input.addWidget(self.label_control)
        vbox_input.addWidget(self.scroll_area)

        self.layout.addLayout(vbox_input)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

    def add_index(self, index: int):
        """Add an index to the table widget."""
        self.table_widget.insertRow(self.table_widget.rowCount())
        self.table_widget.setItem(
            self.table_widget.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(str(index))
        )

    def set_index_list(self, index_list: List[int]):
        """Set the list of indices in the table widget."""
        # reset rows
        self.table_widget.setRowCount(0)

        for index in index_list:
            self.add_index(index)

    def remove_index(self, index: int):
        """Remove an index from the table widget."""
        for i in range(self.table_widget.rowCount()):
            if self.table_widget.item(i, 0).text() == str(index):
                self.table_widget.removeRow(i)
                break

    def on_table_item_click(self, row, column):
        """Handle routing when clicking on an entry in the table widget."""
        item = self.table_widget.item(row, column)
        if item:
            index = int(item.text())
            self.logger.log.info(f"Clicked on table item with index: {index}")
            # Add your routing logic here
            coordinates = self.image_view_controller.clicked_ds[
                self.image_view_controller.clicked_ds[
                    DefaultValues.label_list_label_index.value
                ]
                == index
            ][["centroid-0", "centroid-1", "centroid-2"]].to_numpy()

            # for multiple entries - choose first row
            if len(coordinates) > 1:
                coordinates = coordinates[0]

            # check if coordinates are not NaN
            if np.isnan(coordinates).any():
                self.logger.log.info("Coordinates are not given for label %s" % index)
                return

            self.image_view_controller.jump_to_location(np.squeeze(coordinates))


class ThresholdWidget(QWidget):
    """Widget for threshold based segmentation in napari viewer."""

    def __init__(
        self,
        image_view_controller,
        min_val=0,
        max_val=255,
        logger=None,
        parameters=None,
    ):
        """Construct the ThresholdWidget object."""
        super().__init__()
        self.image_view_controller = image_view_controller
        self.viewer = image_view_controller.viewer
        self.logger = logger

        # sub-layouts
        self.vbox_input = QVBoxLayout()
        self.vbox_segment = QVBoxLayout()
        self.vbox_stat = QVBoxLayout()

        # set the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scene = QGraphicsScene()
        self._slice_mask = False

        self.widgets = {
            # load segmentation button
            "label_input_load": QLabel("Loading:"),
            "button_load": QtWidgets.QPushButton("Load Instance Segmentation"),
            "button_load_from_folder": QtWidgets.QPushButton(
                "Load Instance Segmentation from Folder"
            ),
            # Threshold slider
            "label_input_segment": QLabel("Manual Segmentation:"),
            "auto_threshold_button": QtWidgets.QPushButton("Auto Threshold Slice"),
            "slider_input": QSlider(QtCore.Qt.Orientation.Horizontal),
            "threshold_value": QLabel("0"),
            "manual_input": QSpinBox(),
            "apply_threshold_button_to_slice": QtWidgets.QPushButton("Apply to Slice"),
            "instance_button": QtWidgets.QPushButton("Get Instances"),
            # erode and dilate buttons
            "erode_button": QtWidgets.QPushButton("Erode"),
            "dilate_button": QtWidgets.QPushButton("Dilate"),
            "apply_threshold_button": QtWidgets.QPushButton("Apply to Image"),
            # store to disk button
            "store_button": QtWidgets.QPushButton("Save"),
            # calculate mean and std button
            "mean_std_button": QtWidgets.QPushButton("Calc Mean + Std"),
            "mean_value": QLabel("None"),
            "std_value": QLabel("None"),
            "mean_label": QLabel("Mean:"),
            "std_label": QLabel("Std:"),
            # estimate background value
            "estimate_bg_button": QtWidgets.QPushButton("Estimate Background"),
            "bg_label": QLabel("Background:"),
            "bg_value": QLabel("None"),
        }
        # restrict range for slider
        self.widgets["slider_input"].setRange(min_val, max_val)
        self.widgets["manual_input"].setRange(min_val, max_val)

        # set initial values
        if parameters is not None:
            self.widgets["slider_input"].setValue(parameters["manual_thresholding"])
            self.widgets["threshold_value"].setText(
                str(parameters["manual_thresholding"])
            )

        # build layout
        self._build_layout()
        self._connect()

    def _connect(self):
        self.widgets["slider_input"].valueChanged.connect(self.update_threshold_value)
        self.widgets["slider_input"].valueChanged.connect(self.update_spinbox_value)
        self.widgets["manual_input"].valueChanged.connect(
            self.update_slider_value
        )  # Connect spinbox to slider
        self.widgets["apply_threshold_button"].clicked.connect(
            self.on_apply_threshold_button_to_image
        )
        self.widgets["apply_threshold_button_to_slice"].clicked.connect(
            self.on_apply_threshold_button_to_slice
        )
        self.widgets["button_load"].clicked.connect(self.on_load_click)
        self.widgets["button_load_from_folder"].clicked.connect(
            self.on_load_folder_click
        )
        self.widgets["instance_button"].clicked.connect(self.on_get_instances_click)
        self.widgets["erode_button"].clicked.connect(self.on_erode_click)
        self.widgets["dilate_button"].clicked.connect(self.on_dilate_click)
        self.widgets["auto_threshold_button"].clicked.connect(
            self.on_auto_threshold_click
        )
        self.widgets["store_button"].clicked.connect(self.on_store_click)
        self.widgets["mean_std_button"].clicked.connect(self.on_calc_mean_std_click)
        self.widgets["estimate_bg_button"].clicked.connect(self.on_calc_bg_value)

    def _build_layout(self):
        # ## Load Segmentation ###
        # load button
        vbox_input = QVBoxLayout()
        vbox_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        vbox_input.addWidget(self.widgets["label_input_load"])
        vbox_input.addWidget(self.widgets["button_load"])
        # add load layout
        self.vbox_input.addLayout(vbox_input)

        # ## Semantic Segmentation ###
        vbox_input = QVBoxLayout()
        vbox_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        vbox_input.addWidget(self.widgets["label_input_segment"])
        vbox_input.addWidget(self.widgets["auto_threshold_button"])

        # threshold slider
        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.widgets["slider_input"])
        hbox_input.addWidget(self.widgets["threshold_value"])
        hbox_input.addWidget(self.widgets["apply_threshold_button_to_slice"])
        vbox_input.addLayout(hbox_input)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.widgets["manual_input"])
        vbox_input.addLayout(hbox_input)
        # erode and dilate
        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.widgets["erode_button"])
        hbox_input.addWidget(self.widgets["dilate_button"])
        vbox_input.addLayout(hbox_input)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.widgets["apply_threshold_button"])
        vbox_input.addLayout(hbox_input)

        # add semantic segmentation layout
        self.vbox_segment.addLayout(vbox_input)

        # ## Instance Segmentation ###
        # get instances button
        vbox_input = QVBoxLayout()
        vbox_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        vbox_input.addItem(
            QtWidgets.QSpacerItem(
                20,
                20,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
        )

        vbox_input.addWidget(self.widgets["instance_button"])
        vbox_input.addWidget(self.widgets["store_button"])

        # add instance layout
        self.vbox_segment.addLayout(vbox_input)

        # ## Mean and Std and bg
        vbox_input = QVBoxLayout()
        vbox_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        vbox_input.addWidget(self.widgets["mean_std_button"])

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.widgets["mean_label"])
        hbox_input.addWidget(self.widgets["mean_value"])
        hbox_input.addWidget(self.widgets["std_label"])
        hbox_input.addWidget(self.widgets["std_value"])
        vbox_input.addLayout(hbox_input)

        vbox_input.addItem(
            QtWidgets.QSpacerItem(
                20,
                20,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
        )
        vbox_input.addWidget(self.widgets["estimate_bg_button"])
        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.widgets["bg_label"])
        hbox_input.addWidget(self.widgets["bg_value"])
        vbox_input.addLayout(hbox_input)

        # add to stat layout
        self.vbox_stat.addLayout(vbox_input)

        # add to main layout
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(self.vbox_input)
        self.layout.addItem(
            QtWidgets.QSpacerItem(
                20,
                20,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
        )
        self.layout.addLayout(self.vbox_segment)
        self.layout.addItem(
            QtWidgets.QSpacerItem(
                20,
                20,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
        )
        self.layout.addLayout(self.vbox_stat)

    def update_spinbox_value(self):
        """Update the spinbox value to match the slider value."""
        value = self.widgets["slider_input"].value()
        self.widgets["manual_input"].setValue(value)

    def update_slider_value(self):
        """Update the slider value to match the spinbox value."""
        value = self.widgets["manual_input"].value()
        self.widgets["slider_input"].setValue(value)

    def on_calc_bg_value(self):
        """Calculate the background value of the current slice."""
        if "image_array" in self.viewer.layers:
            if (
                DefaultValues.instance_segmentation_layer_name.value
                in self.viewer.layers
                or DefaultValues.semantic_segmentation_layer_name.value
                in self.viewer.layers
            ):
                self.logger.log.info("Calculating background value for slice...")

                # get the current z-view from the viewer
                z_view = self.viewer.dims.current_step[0]
                z_data = self.viewer.layers["image_array"].data[z_view]

                # get the current z-view of the segmentation
                if (
                    DefaultValues.instance_segmentation_layer_name.value
                    in self.viewer.layers
                ):
                    z_data_seg = self.viewer.layers[
                        DefaultValues.instance_segmentation_layer_name.value
                    ].data[z_view]
                else:
                    z_data_seg = self.viewer.layers[
                        DefaultValues.semantic_segmentation_layer_name.value
                    ].data[z_view]

                # make z_data_seg binary and invert
                bin_z_data_seg = np.logical_not(z_data_seg > 0)

                # multiply with z_data
                z_data_masked = z_data * bin_z_data_seg

                mean = np.mean(z_data_masked)

                self.logger.log.info("Background mean: %s " % str(mean))
                self.widgets["bg_value"].setText("%.3f" % mean)
            else:
                QMessageBox.information(
                    self,
                    "No segmentation detected!",
                    "No segmentation to differentiate foreground and background! Cannot calculate background value!",
                    QMessageBox.StandardButton.Ok,
                )
                self.logger.log.info(
                    "No segmentation to differentiate foreground and background! Cannot calculate background value!"
                )
        else:
            self.logger.log.info("No image detected!")

    def on_calc_mean_std_click(self):
        """Calculate mean and std value of the given volume."""
        if "image_array" in self.viewer.layers:
            self.logger.log.info("Calculating mean and std for slice...")

            # get the current z-view from the viewer
            z_view = self.viewer.dims.current_step[0]
            z_data = self.viewer.layers["image_array"].data[z_view]

            mean = np.mean(z_data)
            std = np.std(z_data)

            self.logger.log.info("Mean: %s " % str(mean))
            self.logger.log.info("Std: %s " % str(std))

            # set values
            self.widgets["mean_value"].setText("%.3f" % mean)
            self.widgets["std_value"].setText("%.3f" % std)
        else:
            self.logger.log.info("No image to calculate values for!")
            QMessageBox.information(
                self,
                "No Image detected!",
                "No image to calculate values for!",
                QMessageBox.StandardButton.Ok,
            )

    def on_store_click(self):
        """Store the instance segmentation to disk."""
        self.logger.log.info("Storing instance segmentation to disk...")
        # store the current instance segmentation
        if DefaultValues.instance_segmentation_layer_name.value in self.viewer.layers:
            instance_mask = self.viewer.layers[
                DefaultValues.instance_segmentation_layer_name.value
            ].data

            # convert to unint16
            instance_mask = instance_mask.astype(np.uint16)

            # get the folder to store the instance mask
            folder = QFileDialog.getExistingDirectory(
                self.viewer.window._qt_window,
                "Select folder to store instance mask",
                str(self.image_view_controller.project_controller.masks_folder),
            )

            self.logger.log.debug("Storing instance segmentation to %s" % folder)

            if folder:
                # build file_path
                file_path = Path(folder).joinpath(
                    DefaultValues.instance_segmentation_tiff_name.value
                )

                self.logger.log.debug(
                    "Storing instance segmentation as file %s" % file_path
                )

                # save as tiff
                tifffile.imwrite(file_path, instance_mask)

                self.logger.log.info("Stored instance segmentation to %s" % file_path)

    def on_auto_threshold_click(self):
        """Apply otsu threshold to the image."""
        self.logger.log.info("Applying otsu threshold...")

        # get the current z-view from the viewer
        z_view = self.viewer.dims.current_step[0]

        # apply otsu threshold
        osu_thresh = skimage.filters.threshold_otsu(
            self.viewer.layers["image_array"].data[z_view]
        )
        self.logger.log.debug("Otsu threshold: %s" % osu_thresh)

        # set slider to otsu threshold
        self.widgets["slider_input"].setValue(osu_thresh)

        # apply threshold
        self.on_apply_threshold_button(z_view=z_view)

    def on_erode_click(self):
        """Erode the semantic segmentation."""
        # check if semantic layer present
        if DefaultValues.semantic_segmentation_layer_name.value in self.viewer.layers:
            data = self.viewer.layers[
                DefaultValues.semantic_segmentation_layer_name.value
            ].data

            if self._slice_mask:
                eroded_data = data

                # get current z-view
                z_view = self.viewer.dims.current_step[0]
                self.logger.log.info(
                    "Eroding binary segmentation of slice %s..." % z_view
                )

                # do erosion
                eroded_semantic_layer_z = skimage.morphology.binary_erosion(
                    data[z_view]
                )
                eroded_data[z_view] = eroded_semantic_layer_z
            else:
                self.logger.log.info("Eroding binary segmentation of image...")

                # do erosion on each z slice
                eroded_data = skimage.morphology.binary_erosion(data)

            # remove old semantic segmentation layer
            self.viewer.layers.pop(DefaultValues.semantic_segmentation_layer_name.value)

            # add to napari
            self.viewer.add_labels(
                eroded_data, name=DefaultValues.semantic_segmentation_layer_name.value
            )

    def on_dilate_click(self):
        """Dilate the semantic segmentation."""
        # check if semantic layer present
        if DefaultValues.semantic_segmentation_layer_name.value in self.viewer.layers:
            data = self.viewer.layers[
                DefaultValues.semantic_segmentation_layer_name.value
            ].data

            if self._slice_mask:
                dilated_data = data

                # get current z-view
                z_view = self.viewer.dims.current_step[0]
                self.logger.log.info(
                    "Dilating binary segmentation of slice %s..." % z_view
                )

                # do erosion
                eroded_semantic_layer_z = skimage.morphology.binary_dilation(
                    data[z_view]
                )
                dilated_data[z_view] = eroded_semantic_layer_z
            else:
                self.logger.log.info("Dilating binary segmentation of image...")

                # do erosion over each z slice
                dilated_data = skimage.morphology.binary_dilation(data)

            # remove old semantic segmentation layer
            self.viewer.layers.pop(DefaultValues.semantic_segmentation_layer_name.value)

            # add to napari
            self.viewer.add_labels(
                dilated_data, name=DefaultValues.semantic_segmentation_layer_name.value
            )

    def on_get_instances_click(self):
        """Get the instance segmentation."""
        if DefaultValues.semantic_segmentation_layer_name.value in self.viewer.layers:
            if self._slice_mask:
                # show warning popup
                QMessageBox.information(
                    self,
                    "Slice Mask detected",
                    'Caution: Slice mask detected. Mask only for one slice. Use "Apply to Image" for entire Image!',
                    QMessageBox.StandardButton.Ok,
                )

            text = (
                "Getting instance segmentation for the image. This might take a while..."
                if not self._slice_mask
                else "Getting instance segmentation for slice..."
            )
            self.logger.log.info(text)
            instance_mask = skimage.measure.label(
                self.viewer.layers[
                    DefaultValues.semantic_segmentation_layer_name.value
                ].data
            )

            self.image_view_controller.overlay_instance_segmentation_result(
                instance_mask, load_properties=False
            )

    def update_threshold_value(self):
        """Update the label with the current slider value."""
        value = self.widgets["slider_input"].value()
        self.widgets["threshold_value"].setText(
            str(value)
        )  # Update the label with the current slider value

    def on_apply_threshold_button_to_slice(self):
        """Apply the threshold to the current slice."""
        z_view = self.viewer.dims.current_step[0]
        self.on_apply_threshold_button(z_view=z_view)

    def on_apply_threshold_button_to_image(self):
        """Apply the threshold to the entire image."""
        self.on_apply_threshold_button(z_view=None)

    def on_apply_threshold_button(self, z_view=None):
        """Apply the threshold to the image."""
        threshold = self.widgets["slider_input"].value()

        self.logger.log.info(
            "Applying threshold segmentation with threshold %s to %s..."
            % (threshold, "slice %s" % z_view if z_view is not None else "image")
        )

        # add segmentation layer
        if DefaultValues.semantic_segmentation_layer_name.value in self.viewer.layers:
            # remove old segmentation layer
            self.viewer.layers.pop(DefaultValues.semantic_segmentation_layer_name.value)

        data = self.viewer.layers["image_array"].data

        mask = np.zeros(data.shape, dtype=bool)
        if z_view is not None:
            mask[z_view] = data[z_view] > threshold
            self._slice_mask = True
        else:
            mask = data > threshold
            self._slice_mask = False

        self.viewer.add_labels(
            mask, name=DefaultValues.semantic_segmentation_layer_name.value
        )

    def on_load_click(self):
        """Load the instance segmentation from disk."""
        self.logger.log.info("Loading instance segmentation...")
        # open file dialog
        file_path = QFileDialog.getOpenFileName(
            self.viewer.window._qt_window,
            "Select instance segmentation file",
            filter="*.tiff",
            directory=str(self.image_view_controller.project_controller.masks_folder),
        )[0]

        self.logger.log.debug("Loading instance segmentation from %s" % file_path)

        if file_path:
            # load the instance mask
            instance_mask = tifffile.imread(file_path)

            # add to napari
            self.image_view_controller.overlay_instance_segmentation_result(
                instance_mask
            )

    def on_load_folder_click(self):
        """Load the instance segmentation from a folder."""
        self.logger.log.info("Loading instance segmentation from folder...")
        # open file dialog
        folder = QFileDialog.getExistingDirectory(
            self.viewer.window._qt_window,
            "Select folder with instance segmentation files",
            str(self.image_view_controller.project_controller.masks_folder),
        )

        self.logger.log.debug("Loading instance segmentation from folder %s" % folder)

        if folder:
            # get all tiffs in the folder
            list_tiles = list(Path(folder).glob("*.tiff"))

            if not list_tiles:
                self.logger.log.error("No tiff files found in folder %s" % folder)
                return

            if DefaultValues.instance_segmentation_layer_name.value in list_tiles:
                list_tiles.remove(DefaultValues.instance_segmentation_layer_name.value)

            # load the instance mask
            instance_mask = np.stack(
                [tifffile.imread(file) for file in Path(folder).glob("*.tiff")], axis=0
            )

            # store the instance mask
            self.logger.log.info("Storing stacked instance segmentation to disk...")
            tifffile.imwrite(
                Path(folder).joinpath(
                    DefaultValues.instance_segmentation_tiff_name.value
                ),
                instance_mask,
            )

            # add to napari
            self.image_view_controller.overlay_instance_segmentation_result(
                instance_mask
            )


class ImageViewController:
    """Controller for the ImageModifierDialog.

    This class is responsible for the logic of the dialog. It is the
    connection between the UI and the data manipulation.
    """

    def __init__(
        self,
        parent: QWidget,
        project_controller: OpenProjectController,
        interactive: bool = True,
    ):
        """Construct the ImageViewController."""
        self.logger = Ari3dLogger()
        self.project_controller = project_controller
        self.parent = parent
        self.interactive = interactive
        self.open_file_window = None
        self.open_file_ui = ImageModifierDialog()
        self._clicked = []
        self._clicked_old = []
        self.clicked_ds = pd.DataFrame(columns=DefaultValues.label_list_header.value)
        self._original_colors = []
        self._assigned_colors = []
        self.current_colors = []
        self.event_handler = (
            None  # observer for communication between streamlit and napari
        )
        self._file = None
        self._properties = None
        self._crop_shape = None
        self._pad_shape = None

        # observer for communication between streamlit and napari
        self.observer = Observer()
        self._started = False

        self.zarr_file = None
        self.zarr_file_altered = None
        self.loaded_image = None
        self.viewer = None
        self.threshold_widget = None
        self.particle_highlight_widget = None

        self._closing = False

    def menuOpen(self):
        """Open the image modifier dialog."""
        self.open_file_window.show()

    def setup_ui(self):
        """Set up the UI for the ImageModifierDialog."""
        self.open_file_window = QDialog()
        self.open_file_ui.setupUi(self.open_file_window)
        self.open_file_window.setWindowTitle("Open new window")
        self.set_links()
        self.set_default_values()

    def set_default_values(self):
        """Set default values for the dialog."""
        if self.project_controller.active_zarr_file is not None:
            self.zarr_file = self.project_controller.active_zarr_file
            self.open_file_ui.lineSetPath.setText(str(self.zarr_file))

        if self.project_controller.active_zarr_file_altered is not None:
            self.zarr_file_altered = self.project_controller.active_zarr_file_altered

    def set_links(self):
        """Set the links for the dialog."""
        self.open_file_ui.linkButtonSetpath.clicked.connect(self.set_image_path)
        self.open_file_ui.buttonBox.accepted.connect(self.crop_convert_safe_open)

    def set_image_path(self):
        """Set the image path for the dialog."""
        zarr_image_path = QFileDialog.getExistingDirectory(
            self.open_file_window,
            "Select zarr container",
            str(self.project_controller.active_zarr_file),
        )
        if zarr_image_path:
            self.open_file_ui.lineSetPath.setText(zarr_image_path)
        else:
            return  # user canceled

        self.zarr_file = Path(zarr_image_path)

    def show_image(self, image_array):
        """Show the image in the napari viewer."""
        self.logger.log.info("Showing image in napari viewer...")
        # Create a new napari viewer
        viewer = napari.view_image(image_array)

        min_val = image_array.min()
        max_val = image_array.max()

        # disable buttons on the lower left
        # viewer.window._qt_viewer.viewerButtons.hide()

        # disable menue
        # viewer.window.main_menu.hide()
        # viewer.window.help_menu.hide()
        # viewer.window.view_menu.hide()

        # Store the viewer asd instance for later use
        self.viewer = viewer

        self.threshold_widget = ThresholdWidget(
            self,
            max_val=max_val,
            min_val=min_val,
            logger=self.logger,
            parameters=self.project_controller.parameters,
        )

        # add the threshold widget
        viewer.window.add_dock_widget(
            self.threshold_widget, name="Threshold based Segmentation"
        )

        self.particle_highlight_widget = ParticleHighlight(self, logger=self.logger)

        # add the particle highlight widget
        viewer.window.add_dock_widget(
            self.particle_highlight_widget, name="Highlighted Particles"
        )

    def close_viewer(self):
        """Close the napari viewer."""
        if self.viewer is not None:
            if self._closing:
                return
            self._closing = True
            self.logger.log.info("Closing napari viewer...")
            try:
                self.viewer.close()
            except RuntimeError:
                pass
            self.viewer = None  # reset viewer
            self._closing = False
        else:
            self.logger.log.info("No viewer to close")

    def _assign_colors(self, labels, cyclic_colors) -> Dict[int, np.ndarray[int]]:
        color_d = {
            label: cyclic_colors[i % len(cyclic_colors)]
            for i, label in enumerate(labels)
        }
        color_d[0] = np.array([0.0, 0.0, 0.0, 0.0])
        color_d[None] = np.array([0.0, 0.0, 0.0, 1.0])

        return color_d

    def overlay_instance_segmentation_result(self, image, load_properties=True):
        """Overlay the instance segmentation result on the napari viewer."""
        self.logger.log.info("Overlaying instance segmentation result...")

        # Convert the image to labels and add it to the viewer
        labels = image.astype(int)  # Example conversion to binary labels

        # crop if necessary
        if self._crop_shape is not None:
            self.logger.log.info(
                "Cropping instance segmentation to shape %s" % str(self._crop_shape)
            )
            labels = self._center_crop(self._crop_shape, labels)

        # pad if necessary
        if self._pad_shape is not None:
            self.logger.log.info(
                "Padding instance segmentation to shape %s" % str(self._pad_shape)
            )
            labels = self._center_pad(self._pad_shape, labels)

        if load_properties:
            self.load_properties()
            labels = self.filter_labels(labels)
        else:
            if self.project_controller.analysis_path.joinpath(
                DefaultValues.properties_file_name.value
            ).exists():
                msg = (
                    "You seem to have loaded a new instance segmentation. "
                    "The properties file might not match this segmentation. Do you want to load the properties file? "
                    "CAUTION: Saving the labels file might destroy matching of properties and labels!"
                )
                reply = QMessageBox.question(
                    self.viewer.window._qt_window,
                    "Load properties file?",
                    msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.load_properties()
                    labels = self.filter_labels(labels)

        # remove layer if already present
        if DefaultValues.instance_segmentation_layer_name.value in self.viewer.layers:
            self.viewer.layers.pop(DefaultValues.instance_segmentation_layer_name.value)

        self.viewer.add_labels(
            labels, name=DefaultValues.instance_segmentation_layer_name.value
        )

        layer = self.viewer.layers[DefaultValues.instance_segmentation_layer_name.value]

        self._original_colors = layer.colormap.colors.copy()
        color_d = self._assign_colors(np.unique(labels), self._original_colors)

        self._file = self.project_controller.analysis_path.joinpath(
            DefaultValues.label_list_file_name.value
        )

        # save labels to memory to restore them later
        self._assigned_colors = color_d.copy()
        self.current_colors = color_d.copy()

        # color all labels in _file red
        self.parse_labels_file()
        self._clicked = np.unique(
            self.clicked_ds[DefaultValues.label_list_label_index.value].to_numpy()
        )
        [self.particle_highlight_widget.add_index(val) for val in self._clicked]

        # color all labels in _file red
        self.highlight_labels_color(self._clicked)

        # set new colormap
        self.logger.log.debug("Setting new colormap...")
        direct_color_map = DirectLabelColormap(color_dict=self.current_colors)
        layer.colormap = direct_color_map

        if self.event_handler is None:
            self.logger.log.info("Starting observer for file %s" % self._file)
            # schedule the observer
            self.event_handler = FileWatcher(str(self._file), self)
            self.observer.schedule(
                self.event_handler, path=str(self._file.parent), recursive=False
            )
            self.observer.start()
            self._started = True

        @layer.mouse_drag_callbacks.append
        def get_mouse_click_label(image_layer, event):
            """Define callback for mouse click on the image layer."""
            data_coordinates = image_layer.world_to_data(event.position)
            # cords = np.round(data_coordinates).astype(int)
            val = image_layer.get_value(data_coordinates)
            self.logger.log.debug("Clicked on label %s" % val)

            # exclude background
            if val == 0 or val is None:
                return

            # get the clicked array from the dataset
            self._clicked = np.unique(
                self.clicked_ds[DefaultValues.label_list_label_index.value].to_numpy()
            )

            if len(self._clicked) == 6:
                if val in self._clicked:
                    self._update_labels(val)
                else:
                    self.logger.log.info(
                        "Maximum number of labels selected. Deselect label by again click on it."
                    )

                return

            self._update_labels(val)

    def filter_labels(self, labels):
        """Filter the labels based on the properties file."""
        # if properties.csv is present, filter the labels
        if self._properties is not None:
            # filter labels
            self.logger.log.debug("Filtering labels...")
            labels = np.where(
                np.isin(
                    labels,
                    self._properties[
                        DefaultValues.properties_file_label_index.value
                    ].to_numpy(),
                ),
                labels,
                0,
            )

        return labels

    def load_properties(self):
        """Load the properties file from the analysis path."""
        if DefaultValues.properties_file_name.value in [
            Path(x).name for x in list(self.project_controller.analysis_path.iterdir())
        ]:
            self.logger.log.info("Properties file found. Loading labels...")
            self._properties = pd.read_csv(
                self.project_controller.analysis_path.joinpath(
                    DefaultValues.properties_file_name.value
                )
            )

    def _update_labels(self, val):
        self._clicked_old = self._clicked.copy()
        # update the clicked array
        if val in self._clicked:
            self._clicked = np.delete(self._clicked, np.where(self._clicked == val))
            self.particle_highlight_widget.remove_index(val)
        else:
            self._clicked = np.append(self._clicked, val)
            self.particle_highlight_widget.add_index(val)
        self.logger.log.debug("Selected labels: %s" % self._clicked)

        # wait until the observer has finished processing
        while self.event_handler.is_processing():
            pass

        # store altered clicked array to disk as csv - triggering re-coloring
        self.write_labels_file()
        self.logger.log.debug("Stored altered labels to file: %s" % self._file)

    def write_labels_file(self):
        """Write the clicked labels to the labels file."""
        self.logger.log.debug("Writing labels to file...")

        if self._properties is not None:
            # get the properties for the clicked labels
            file_ds = self._properties[
                self._properties[DefaultValues.properties_file_label_index.value].isin(
                    self._clicked
                )
            ]
            # replace headers with the correct ones
            file_ds = file_ds.rename(
                columns={
                    DefaultValues.properties_file_label_index.value: DefaultValues.label_list_label_index.value,
                }
            )
            # throw away all other columns that are not necessary
            file_ds = file_ds[DefaultValues.label_list_header.value]
        else:
            file_ds = pd.DataFrame(columns=DefaultValues.label_list_header.value)
            # write without additional properties
            file_ds[DefaultValues.label_list_label_index.value] = self._clicked

        # write to file
        file_ds.to_csv(self._file, index=False)

        # update the clicked dataset
        self.clicked_ds = file_ds
        self.logger.log.debug("File content: %s" % file_ds.head())

    def parse_labels_file(self):
        """Parse the labels file and return the dataset."""
        file_ds = pd.DataFrame(columns=DefaultValues.label_list_header.value)
        if Path(self._file).exists():
            try:
                file_ds = pd.read_csv(self._file)
            except Exception as e:
                if self.logger is not None:
                    self.logger.log.error(f"Error while parsing file {self._file}: {e}")
                return np.array([])

            if file_ds.empty:
                if self.logger is not None:
                    self.logger.log.debug(f"File {self._file} is empty")
            else:
                file_ds[DefaultValues.label_list_label_index.value].astype(
                    int
                )  # ensure labels are integers

            if self.logger is not None:
                self.logger.log.debug(f"Parsed file content: {file_ds.head()}")

        # set the new clicked dataset
        self.clicked_ds = file_ds
        self._clicked = np.unique(
            file_ds[DefaultValues.label_list_label_index.value].to_numpy()
        )
        self._clicked_old = self._clicked.copy()

        return file_ds

    def highlight_labels_color(self, labels):
        """Highlight the labels in the viewer with red color."""
        # color label red
        for label in labels:
            self.logger.log.debug("Highlighting label %s" % label)
            self.current_colors[label] = np.array([1.0, 0.0, 0.0, 1.0])

    def reset_labels_color(self, labels):
        """Reset the color of the labels to their original color."""
        # color label back
        for label in labels:
            self.logger.log.debug("Resetting label %s" % label)
            self.current_colors[label] = self._assigned_colors[label]

    def _center_crop(self, shape: List[int], image_array: np.ndarray):
        self._crop_shape = None  # reset crop shape
        self.logger.log.info("Cropping image to %s" % str(shape))
        arr, shape = center_crop(image_array, shape)
        self._crop_shape = shape

        return arr

    def _center_pad(self, shape: List[int], image_array: np.ndarray):
        self._pad_shape = None
        self.logger.log.debug("Padding image to %s" % str(shape))
        arr, pad_shape = center_pad(image_array, shape)
        self._pad_shape = pad_shape

        return arr

    def jump_to_location(self, location):
        """Jump to a certain location and set the view to it.

        Parameters:
        location (tuple): A tuple of coordinates (z, y, x) to jump to.
        """
        if self.viewer is not None:
            self.viewer.dims.set_point(0, location[0])  # Set the z dimension
            self.viewer.dims.set_point(1, location[1])  # Set the y dimension
            self.viewer.dims.set_point(2, location[2])  # Set the x dimension
            self.logger.log.info(f"Jumped to location: {location}")
        else:
            self.logger.log.info("Viewer is not initialized.")

    def _convert_8_bit(self, image_array):
        # convert to 8 bit
        image_array = (image_array / image_array.max() * 255).astype(np.uint8)
        return image_array

    def crop_convert_safe_open(self):
        """Crop, convert and save the image."""
        self.logger.log.info(
            "Opening image. Depending on the size this can take a while..."
        )
        # zarr file
        image_array = np.array(zarr.open(self.zarr_file))

        d1 = self.open_file_ui.lineEdit_3.text()
        d2 = self.open_file_ui.lineEdit_2.text()
        d3 = self.open_file_ui.lineEdit.text()

        altered = False
        if d1 != "" and d2 != "" and d3 != "":
            image_array = self._center_crop([int(d1), int(d2), int(d3)], image_array)
            altered = True

        # shape of
        s1 = self.open_file_ui.lineEdit_6.text()
        s2 = self.open_file_ui.lineEdit_5.text()
        s3 = self.open_file_ui.lineEdit_4.text()

        if s1 != "" and s2 != "" and s3 != "":
            image_array = self._center_pad([int(s1), int(s2), int(s3)], image_array)
            altered = True

        if self.open_file_ui.checkBox.isChecked():
            self.logger.log.info("Converting image to 8-bit")
            image_array = self._convert_8_bit(image_array)
            altered = True

        self.loaded_image = image_array
        self.show_image(image_array)

        # safe the altered image as an independent zarr file
        if altered:
            self._safe_crop()

    def _safe_crop(self):
        self.zarr_file_altered = Path(self.zarr_file).parent.joinpath(
            Path(self.zarr_file).stem + "_altered.zarr"
        )
        self.logger.log.info(
            "Saving altered image as zarr under %s ..." % self.zarr_file_altered
        )
        self.project_controller.active_zarr_file_altered = self.zarr_file_altered
        self.logger.log.info("Set active zarr file to %s" % self.zarr_file_altered)

        # safe the cropped image
        zarr.save(str(self.zarr_file_altered), self.loaded_image)

    def __del__(self):
        """Destruct the observer."""
        if self._started:
            self.logger.log.info("Stopping observer...")
            self.observer.stop()
            self.observer.join()
