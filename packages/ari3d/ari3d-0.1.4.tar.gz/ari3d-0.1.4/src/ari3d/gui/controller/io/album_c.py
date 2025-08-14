"""Controller for managing solutions for the ari3d application using Album API."""
import logging
import traceback
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Set

from album.runner.album_logging import get_active_logger
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QMessageBox, QWidget

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.gui.model.tasks import ExecuteSolutionTask, SequentialTaskRunner
from ari3d.resources.default_values import DefaultValues

cur_file_path = Path(__file__).parent

SOLUTION_IDS = [
    "de.mdc:data_viewer",
    "de.mdc:particleSeg3D-predict",
    "de.mdc:property_extraction",
]

ARI3D_BASE_PATH = Path.home().joinpath(".ari3d")
ALBUM_BASE_PATH = ARI3D_BASE_PATH.joinpath("collection")


def _handle_install_solution_result(r: bool, solution_install_file: Path):
    if r:
        # remove installation failed file if it exists
        if solution_install_file.exists():
            solution_install_file.unlink()
    else:
        # mark installation as failed
        with open(solution_install_file, "w") as f:
            f.write("Installation failed")


class AlbumController:
    """Controller class for managing solutions in the ari3d application using Album API."""

    def __init__(self, parent: QWidget, interactive: bool = True):
        """Initialize the AlbumController with the album API and logger."""
        self.parent = parent
        self._setup_album()
        self.logger = Ari3dLogger()
        self._add_logging_to_file()
        self.interactive = interactive
        self.task_stack = []

    def _setup_album(self):
        from album.api import Album

        ALBUM_BASE_PATH.mkdir(parents=True, exist_ok=True)

        self.album_api = Album.Builder().base_cache_path(ALBUM_BASE_PATH).build()
        self.album_log = logging.getLogger("album")
        self.album_api.load_or_create_collection()

        # add catalog
        try:
            self.album_api.get_catalog_by_src(str(DefaultValues.repo_link.value))
        except LookupError:
            self.album_api.add_catalog(str(DefaultValues.repo_link.value))

    def _add_logging_to_file(self):
        # get the FileHandler in ari3d_logger
        for handler in self.logger.log.handlers:
            if isinstance(handler, logging.FileHandler):
                # add album logging to the same file
                self.album_log.addHandler(handler)
                self.album_log.setLevel(self.logger.log.level)

    def show_message(self, message):
        """Show customized message."""
        QMessageBox.information(self.parent, "Information", message)

    def show_error(self, message):
        """Show customized error message."""
        QMessageBox.critical(self.parent, "Error", message)

    def _check_steps(self) -> Set[str]:
        """Check for updates of the solutions in the album catalog."""
        updates = self.album_api.upgrade(dry_run=True)

        self.logger.log.debug("All updates:" + str(updates))

        ari3d_updates = updates["ari3d"]
        ari3d_update_lit = ari3d_updates._solution_changes
        coordinate_set = {
            ":".join([x.coordinates().group(), x.coordinates().name()])
            for x in ari3d_update_lit
        }
        text = (
            "No updates available!"
            if ari3d_update_lit == []
            else (
                "Updates available for:"
                + ", ".join(coordinate_set)
                + ". Run update new steps to install them."
            )
        )

        self.logger.log.info(text)

        return coordinate_set

    def check_steps(self):
        """Check for updates of the steps in the catalog."""
        task = ExecuteSolutionTask(
            self._check_steps, "Check Steps", "Check Steps Failed"
        )
        task.signals.result.connect(self._handle_check_steps_result)
        task.signals.error.connect(self.show_error)

        QThreadPool().globalInstance().start(task)

    def _handle_check_steps_result(self, coordinate_set: Set[str]):
        """Handle the result of checking steps."""
        if coordinate_set:
            self.show_message(
                "Updates available for: "
                + ", ".join(coordinate_set)
                + ". Run update new steps to install them."
            )
        else:
            self.show_message("No updates available!")

    def _update_steps(self):
        coordinate_set = self._check_steps()
        self.album_api.upgrade()
        for solution in coordinate_set:
            self._reinstall_solution(solution)
        return coordinate_set

    def update_steps(self):
        """Update the solutions in the album."""
        task = ExecuteSolutionTask(
            self._update_steps, "Update Steps", "Update Steps Failed"
        )
        task.signals.result.connect(self._handle_update_steps_result)
        task.signals.error.connect(self.show_error)

        QThreadPool().globalInstance().start(task)

    def _handle_update_steps_result(self, coordinate_set: Set[str]):
        """Handle the result of updating steps."""
        if coordinate_set:
            self.show_message("Updated " + ", ".join(coordinate_set))
        else:
            self.show_message("No updates available!")

    def _reinstall_solution(self, solution: str):
        """Reinstall a specific solution in the album."""
        self._uninstall_solution(solution)
        self._install_solution(solution)

    def _reinstall_steps(self):
        """Reinstall all solutions in the album."""
        self._uninstall_required()
        self._try_install_required_no_question()

    def reinstall_steps(self):
        """Reinstall all solutions in the album."""
        task = ExecuteSolutionTask(
            self._reinstall_steps, "Reinstall Steps", "Reinstall Steps Failed"
        )
        task.signals.message.connect(self.show_message)
        task.signals.error.connect(self.show_error)

        QThreadPool().globalInstance().start(task)

    def _install_solution(self, solution: str) -> bool:
        """Install a specific album solution."""
        # install from catalog
        try:
            level = get_active_logger().level
            get_active_logger().setLevel("ERROR")
            if not self.album_api.is_installed(solution):
                get_active_logger().setLevel(level)
                self.logger.log.info(f"Installing {solution}")
                self.album_api.install(solution)
            self.logger.log.info(f"{solution} is ready to run!")
            get_active_logger().setLevel(level)
        except LookupError:
            self.logger.log.info(
                f"Solution {solution} not found in the catalog. Unable to run this step!"
            )
            return False
        except RuntimeError as e:
            self.logger.log.error(
                f"Failed to install {solution}: {e}. Look into logfile {str(self.logger.log_file_path)} for details. You will not be able to run this step!"
            )
            return False

        return True

    def _uninstall_solution(self, solution: str):
        """Uninstall a specific album solution."""
        try:
            level = get_active_logger().level
            get_active_logger().setLevel("ERROR")
            if self.album_api.is_installed(solution):
                get_active_logger().setLevel(level)
                self.logger.log.info(f"Uninstalling {solution}")
                self.album_api.uninstall(solution)
            self.logger.log.info(f"{solution} is uninstalled!")
            get_active_logger().setLevel(level)
        except LookupError:
            self.logger.log.info(
                f"Solution {solution} not found in the catalog. Unable to uninstall this step!"
            )

    def install_from_disk(self, solution: str):
        """Install a specific solution from disk."""
        name = solution.split(":")[1]
        try:
            if not self.album_api.is_installed(solution):
                self.logger.log.info(f"Installing {solution}")
                self.album_api.install(
                    str(cur_file_path.joinpath("..", "..", "..", "solutions", name))
                )
            self.logger.log.info(f"{solution} is ready to run")
        except LookupError:
            self.album_api.install(
                str(cur_file_path.joinpath("..", "..", "..", "solutions", name))
            )

    def run(self, solution, argv=None):
        """Run a specific solution in the album."""
        self.album_api.run(solution, argv=argv)

    def install_required(self):
        """Install all required solutions for the interactive workflow."""
        # loop to install all solutions necessary for this interactive workflow
        for solution_id in SOLUTION_IDS:
            success = self._install_solution(solution_id)
            if not success:
                self.logger.log.error(
                    f"Solution {solution_id} could not be installed. Please check the logs for details."
                )
                raise RuntimeError("Installation failed for one or more solutions.")

    def _try_install_required_no_question(self):
        """Try to install all required solutions for the interactive workflow."""
        # loop to install all solutions necessary for this interactive workflow
        for solution_id in SOLUTION_IDS:
            try:
                solution_install_file = ARI3D_BASE_PATH.joinpath(
                    solution_id.replace(":", "_")
                )
                r = self._install_solution(solution_id)
                if r:
                    # remove installation failed file if it exists
                    if solution_install_file.exists():
                        solution_install_file.unlink()
                else:
                    # mark installation as failed
                    with open(solution_install_file, "w") as f:
                        f.write("Installation failed")

            except Exception:
                self.logger.log.error(
                    f"Failed to install {solution_id}. {traceback.format_exc()} Look into logfile {str(self.logger.log_file_path)} for details.  You will not be able to run this step!"
                )

    def ask_reinstall(self, solution_id):
        """Ask the user whether to re-trigger the installation of a solution."""
        reply = QMessageBox.question(
            self.parent,
            "Re-trigger installation",
            "Installation of %s failed before. Do you want to try to install it again?"
            % solution_id,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return True if reply == QMessageBox.StandardButton.Yes else False

    def push_install_required(self):
        """Try to install all required solutions for the interactive workflow."""
        for solution_id in SOLUTION_IDS:
            solution_install_file = ARI3D_BASE_PATH.joinpath(
                solution_id.replace(":", "_")
            )

            # check if installation failed before
            if solution_install_file.exists() and self.interactive:
                # pop up a message box to the user asking whether to reinstall the solution
                reply = self.ask_reinstall(solution_id)
                if not reply:
                    self.logger.log.info(
                        f"Skipping installation of {solution_id} as per user request."
                    )
                    continue

            if not self.album_api.is_installed(solution_id):
                task = ExecuteSolutionTask(
                    self._install_solution,
                    f"{solution_id} is ready to run!",
                    f"Install Solution {solution_id} failed",
                    solution_id,
                )
                task.signals.message.connect(self.show_message)
                task.signals.error.connect(self.show_error)
                task.signals.result.connect(
                    partial(
                        _handle_install_solution_result,
                        solution_install_file=solution_install_file,
                    )
                )
                self.task_stack.append(task)
            else:
                self.logger.log.info(f"{solution_id} is already installed.")

        if len(self.task_stack) > 0:
            # display a message to the user that the installation is in progress
            self.show_message(
                "Installing required solutions in the background. This may take a while. Steps handling will be available once the installation is done."
            )

    def start_sequential_working_on_tasks(self):
        """Start working on the tasks in the task stack sequentially."""
        SequentialTaskRunner(self.task_stack).start()

    @staticmethod
    def write_install_txt(project_files_path: Path):
        """Write a file indicating that the installation of solutions is done."""
        # create results file for snakemake
        output_file = project_files_path.joinpath("installation_done.txt")
        with open(output_file, "w") as f:
            f.write("Installation of solutions done.\n")
            f.write(f"Date: {str(datetime.now().strftime('%Y%m%d_%H%M%S'))}")

    def _uninstall_required(self):
        """Uninstall all required solutions for the interactive workflow."""
        # loop to install all solutions necessary for this interactive workflow
        for solution_id in SOLUTION_IDS:
            try:
                self._uninstall_solution(solution_id)
            except Exception as e:
                print(f"Failed to uninstall {solution_id}: {e}")

    def uninstall_required(self):
        """Uninstall all required solutions for the interactive workflow."""
        task = ExecuteSolutionTask(
            self._uninstall_required,
            "Uninstall Required Solutions",
            "Uninstall Required Solutions Failed",
        )
        task.signals.message.connect(self.show_message)
        task.signals.error.connect(self.show_error)

        QThreadPool().globalInstance().start(task)
