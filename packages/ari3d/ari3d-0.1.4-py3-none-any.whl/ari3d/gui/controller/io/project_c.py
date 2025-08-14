"""Controller for managing the opening and creation of projects in ari3d."""
from __future__ import annotations

import glob
import os
import shutil
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.gui.model.decorators import fallback
from ari3d.resources.default_values import DefaultValues
from ari3d.utils.conversion import glob_re, tiffs2zarr
from ari3d.utils.operations.file_operations import (
    create_path_recursively,
    get_dict_from_yml,
    write_dict_to_yml,
)

CURR_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


class OpenProjectController:
    """Controller class for managing the opening and creation of projects in ari3d."""

    def __init__(self, parent: QWidget):
        """Initialize the OpenProjectController."""
        self.logger = Ari3dLogger()
        self.parent = parent
        self.project_path = None
        self.project_files_path = None
        self.gray_path = None
        self.masks_folder = None
        self.report_path = None
        self.analysis_path = None
        self.active_zarr_file = None
        self.active_zarr_file_altered = None
        self.particle_seg_path = None
        self.particle_seg_image_path = None
        self.parameters = None
        self.load_parameters(
            CURR_PATH.parent.parent.parent.joinpath("resources", "parameters.yml")
        )

    def open_project(self, project_path: Path = None, interactive=True):
        """Open a project from the given path."""
        self.logger.log.info("Opening project...")
        self.set_project_path(project_path)

        if not self.project_path:
            return

        # check if zarr file in zarr folder
        zarr_files = glob.glob(str(self.project_files_path.joinpath("*.zarr")))

        # remove "_altered" from zarr files as they are not the original files
        zarr_files = [f for f in zarr_files if "_altered.zarr" not in f]
        self.logger.log.debug("Zarr files: %s" % zarr_files)

        zarr_files_altered = glob.glob(
            str(self.project_files_path) + os.sep + "*_altered.zarr"
        )
        self.logger.log.debug("Zarr files altered: %s" % zarr_files_altered)

        # if no zarr files in folder, assume tiff files present and convert them to zarr to create a new project
        if len(zarr_files) == 0:
            if interactive:
                # message: seems like this is not a project folder, do you want to create a new project?
                QMessageBox.information(
                    self.parent,
                    "No Project Found",
                    "No project found in the given folder.",
                )
            self.project_path = None
            return

        if len(zarr_files) == 1:
            # check whether tiff files in grey folder exist
            tiff_files = list(
                glob_re(
                    r".*\.(tif|tiff|TIF|TIFF)$", os.listdir(path=str(self.gray_path))
                )
            )
            if len(tiff_files) == 0:
                self.logger.log.error(
                    "No tiff files in the grey folder %s that should have"
                    " been created during project creation. Cannot open project."
                    % str(self.project_path)
                )
                self.project_path = None
                return

            self.logger.log.info("Zarr file found: %s" % zarr_files[0])
            self.active_zarr_file = Path(zarr_files[0])
            self.logger.log.info(
                "Set active zarr file to %s" % str(self.active_zarr_file)
            )
        else:
            self.logger.log.error(
                "More than one zarr file in the given folder %s" % self.project_path
            )
            self.project_path = None
            return

        if len(zarr_files_altered) == 1:
            self.active_zarr_file_altered = Path(zarr_files_altered[0])
            self.logger.log.info(
                "Set active zarr file to %s" % str(self.active_zarr_file_altered)
            )
        elif len(zarr_files_altered) > 1:
            self.logger.log.error(
                "More than one altered zarr file in the given folder %s. Cannot open project."
                % str(self.project_path)
            )
            self.project_path = None
            return

        # ensure all necessary folders exist
        create_path_recursively(self.gray_path)
        create_path_recursively(self.project_files_path)
        create_path_recursively(self.report_path)
        create_path_recursively(self.analysis_path)
        create_path_recursively(self.masks_folder)
        create_path_recursively(self.particle_seg_path)
        create_path_recursively(self.particle_seg_image_path)

        # load parameters
        if self.report_path.joinpath("parameters.yml").exists():
            self.logger.log.info(
                "Parameters file found: %s"
                % str(self.report_path.joinpath("parameters.json"))
            )
            self.load_parameters(self.report_path.joinpath("parameters.yml"))
        else:
            # save default parameters file to report folder
            self.logger.log.info(
                "Parameters file not found. Copying default parameters file to report folder..."
            )
            self.save_parameters()

        self.logger.log.info("Project opened successfully!")

    def load_parameters(self, parameters_file: Path):
        """Load parameters from a YAML file."""
        self.logger.log.info("Loading parameters from %s" % str(parameters_file))
        self.parameters = get_dict_from_yml(parameters_file)
        self.logger.log.info("Parameters loaded successfully!")

    def save_parameters(self):
        """Save the current parameters to a YAML file in the report folder."""
        self.logger.log.debug(
            "Saving parameters to %s "
            % str(self.report_path.joinpath("parameters.yml"))
        )
        write_dict_to_yml(
            str(self.report_path.joinpath("parameters.yml")), self.parameters
        )

    @fallback(lambda self: self.fallback_routine())
    def create_project(self, fallback_routine):
        """Create a new project by selecting a directory."""
        project_path = QFileDialog.getExistingDirectory(self.parent, "Select Directory")

        return self._create_project(project_path)

    def _create_project(self, project_path, interactive=True):
        if not project_path:
            return
        self.set_project_path(project_path)

        # check if tiff files exist in the project folder
        images_files = list(
            glob_re(
                r".*\.(tif|tiff|TIF|TIFF)$", os.listdir(path=str(self.project_path))
            )
        )
        if len(images_files) == 0:
            self.logger.log.error(
                "No image files in the given folder %s. Cannot create Project."
                % str(self.project_path)
            )
            self.project_path = None
            return

        # ensure moving tiff files is OK with the user
        if interactive:
            reply = QMessageBox.question(
                self.parent,
                "Confirm Move",
                "Do you want to move TIFF files to the grey folder? Cannot create project without moving files.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
        else:
            reply = QMessageBox.StandardButton.Yes

        if reply == QMessageBox.StandardButton.No:
            self.logger.log.info("User cancelled moving TIFF files.")
            self.project_path = None
            return

        # make sure the folders exist if not create them
        self.logger.log.debug("Creating necessary folders...")
        create_path_recursively(self.gray_path)
        create_path_recursively(self.project_files_path)
        create_path_recursively(self.report_path)
        create_path_recursively(self.analysis_path)
        create_path_recursively(self.masks_folder)
        create_path_recursively(self.particle_seg_path)
        create_path_recursively(self.particle_seg_image_path)
        self.logger.log.info("Converting tiff files to zarr...")
        self.active_zarr_file = Path(
            tiffs2zarr(
                str(self.project_path),
                str(self.project_files_path),
                DefaultValues.n_jobs.value,
            )
        )
        self.logger.log.info("Set active zarr file to %s" % str(self.active_zarr_file))
        assert (
            self.active_zarr_file.exists()
        ), "Zarr file not created. Check logs for errors."
        self.logger.log.info("Moving tiff files to grey folder...")

        for image_file in images_files:
            os.rename(
                str(self.project_path.joinpath(image_file)),
                str(self.gray_path.joinpath(image_file)),
            )

        self.logger.log.info("Project created successfully!")
        self.open_project(self.project_path, interactive)

        # create output file for snakemake
        output_file = self.project_files_path.joinpath("project_created.txt")
        with open(output_file, "w") as f:
            f.write(f"Project created successfully at {self.project_path}\n")
            f.write(f"Active Zarr file: {self.active_zarr_file}\n")
            f.write(f"Date: {str(datetime.now().strftime('%Y%m%d_%H%M%S'))}")

        return

    def fallback_routine(self):
        """Fallback routine to execute when an error occurs."""
        self.logger.log.info("Executing fallback routine...")
        self.project_path = None

        # remove the project folder if it was created
        if self.gray_path is not None and self.gray_path.exists():
            shutil.rmtree(str(self.gray_path))

        if self.project_files_path is not None and self.project_files_path.exists():
            shutil.rmtree(str(self.project_files_path))

        if self.report_path is not None and self.report_path.exists():
            shutil.rmtree(str(self.report_path))

        if self.analysis_path is not None and self.analysis_path.exists():
            shutil.rmtree(str(self.analysis_path))

        if self.masks_folder is not None and self.masks_folder.exists():
            shutil.rmtree(str(self.masks_folder))

    def set_project_path(self, folder_path: Path = None):
        """Set the project path and initialize related paths."""
        self.logger.log.debug("Opening project...")
        if not folder_path:
            folder_path = QFileDialog.getExistingDirectory(
                self.parent, "Select Directory", str(Path.home())
            )

        if not folder_path:
            return  # user cancelled

        if Path(folder_path).stem in DefaultValues.forbidden_project_names.value:
            self.logger.log.error(
                "Project folder cannot be named %s !" % Path(folder_path).stem
            )
            return

        self.logger.log.info("Set project path to %s" % folder_path)
        self.logger.log.info(
            "Set gray path to %s"
            % Path(folder_path).joinpath(DefaultValues.gray_folder_name.value)
        )
        self.logger.log.info(
            "Set project files output path to %s"
            % Path(folder_path).joinpath(DefaultValues.project_files_folder_name.value)
        )
        self.logger.log.info(
            "Set report output path to %s"
            % Path(folder_path).joinpath(DefaultValues.report_folder_name.value)
        )
        self.logger.log.info(
            "Set analysis output path to %s"
            % Path(folder_path).joinpath(DefaultValues.analysis_folder_name.value)
        )
        self.logger.log.debug(
            "Set segmentation output path to %s"
            % Path(folder_path).joinpath(DefaultValues.segmentation_folder_name.value)
        )
        self.logger.log.debug(
            "Set particle seg image path to %s"
            % Path(folder_path).joinpath(
                DefaultValues.segmentation_folder_name.value,
                DefaultValues.segmentation_input_folder_name.value,
            )
        )

        self.project_path = Path(folder_path)
        self.gray_path = Path(self.project_path).joinpath(
            DefaultValues.gray_folder_name.value
        )
        self.analysis_path = Path(self.project_path).joinpath(
            DefaultValues.analysis_folder_name.value
        )
        self.project_files_path = Path(self.project_path).joinpath(
            DefaultValues.project_files_folder_name.value
        )
        self.report_path = Path(self.project_path).joinpath(
            DefaultValues.report_folder_name.value
        )
        self.masks_folder = Path(self.project_path).joinpath(
            DefaultValues.masks_folder_name.value
        )
        self.particle_seg_path = Path(self.project_files_path).joinpath(
            DefaultValues.segmentation_folder_name.value
        )
        self.particle_seg_image_path = Path(self.particle_seg_path).joinpath(
            DefaultValues.segmentation_input_folder_name.value
        )
