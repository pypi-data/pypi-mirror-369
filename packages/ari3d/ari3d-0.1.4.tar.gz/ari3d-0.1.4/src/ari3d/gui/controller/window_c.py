"""Controller for the main window of the ari3d application."""
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QMainWindow, QMessageBox

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.gui.controller.io.album_c import AlbumController
from ari3d.gui.controller.io.help_c import HelpController
from ari3d.gui.controller.io.project_c import OpenProjectController
from ari3d.gui.controller.io.view_c import ImageViewController
from ari3d.gui.controller.solutions.extract_properties_c import (
    ExtractPropertiesDialogController,
)
from ari3d.gui.controller.solutions.particleSeg_c import (
    UI_ParticleSeg3DAdvancedController,
    UI_ParticleSeg3DPredictController,
)
from ari3d.gui.controller.solutions.streamlit_c import DataViewerDialogController
from ari3d.gui.view.MainWindow_ui import Ui_MainWindow

cur_file_path = Path(__file__).parent


class WindowController(QMainWindow):
    """Controller for the main window of the ari3d application."""

    def __init__(
        self,
    ):
        """Initialize the main window controller with the album API and logger."""
        super().__init__()
        self.album_api = AlbumController(self)
        self.logger = Ari3dLogger()
        # try to install required solutions
        self.album_api.push_install_required()
        # start sequential working on tasks
        self.album_api.start_sequential_working_on_tasks()
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.check_startup_tasks)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.poll_timer.start(1000)
        self.setWindowTitle("ARI3D - Analyse Regions in 3D X-Ray CT Images")
        self.set_window_icon()

        # Set the image of the main window
        self.set_image(
            cur_file_path.parent.parent.joinpath(
                "resources", "images", "logo", "logo_w.png"
            )
        )

        # setup instance Window controller
        self.project_controller = OpenProjectController(self)
        self.image_view_controller = ImageViewController(self, self.project_controller)
        self.particle_seg_dialog_controller = UI_ParticleSeg3DPredictController(
            self, self.album_api, self.project_controller, self.image_view_controller
        )
        self.particle_seg_dialog_advanced_controller = (
            UI_ParticleSeg3DAdvancedController(
                self,
                self.album_api,
                self.project_controller,
                self.image_view_controller,
            )
        )
        self.extract_histogram_controller = ExtractPropertiesDialogController(
            self, self.album_api, self.project_controller
        )
        self.data_viewer_controller = DataViewerDialogController(
            self, self.album_api, self.project_controller
        )
        self.help_controller = HelpController(self)

        self.set_connections()

    def set_window_icon(self):
        """Set the window icon for the main window."""
        self.setWindowIcon(
            QIcon(
                str(
                    cur_file_path.parent.parent.joinpath(
                        "resources", "images", "logo", "logo_w_xs.png"
                    )
                )
            )
        )

    def check_startup_tasks(self):
        """Check if all startup tasks are done and enable the steps menu."""
        all_done = all(task.is_done() for task in self.album_api.task_stack)

        if all_done:
            self.logger.log.debug("All startup tasks done! Steps handling enabled.")
            self.poll_timer.stop()

            # enable buttons for steps
            self.ui.menuSteps.setEnabled(True)

            # change color back to default
            self.ui.menuSteps.setStyleSheet("")

    def set_image(self, image_path: Path):
        """Set the image for the main window."""
        pixmap = QPixmap(str(image_path))
        self.ui.imageLabel.setPixmap(pixmap)

    def set_connections(self):
        """Set up the connections for the main window actions."""
        # project actions
        self.ui.actionCreate_project.triggered.connect(
            self.project_controller.create_project
        )
        self.ui.actionLoad_project.triggered.connect(
            self.project_controller.open_project
        )
        self.ui.actionQuit.triggered.connect(self.close)

        # 3d viewer actions
        self.ui.actionOpenImage.triggered.connect(self.openImage)
        self.ui.actionClose3DViewer.triggered.connect(self.closeViewer)
        self.ui.actionSegmentation.triggered.connect(self.openParticleSegWindow)

        # process actions
        self.ui.actionOpenDataViewer.triggered.connect(self.openStreamlitWindow)
        self.ui.actionExport_histograms.triggered.connect(self.extractProperties)

        # step actions
        self.ui.actionCheck_steps.triggered.connect(self.check_steps)
        self.ui.actionUpdate_steps.triggered.connect(self.update_steps)
        self.ui.actionReinstall_steps.triggered.connect(self.reinstall_steps)

        # help actions
        self.ui.actionAbout.triggered.connect(self.help_controller.show_about)
        self.ui.actionCode.triggered.connect(self.help_controller.open_code_repository)
        self.ui.actionDocumentation.triggered.connect(
            self.help_controller.open_documentation
        )
        self.ui.actionTutorial.triggered.connect(self.help_controller.open_tutorial)
        self.ui.actionArticle.triggered.connect(self.help_controller.open_article)

        # logging actions
        self.ui.actionLogNone.triggered.connect(self.logger.set_log_level_none)
        self.ui.actionLogDebug.triggered.connect(self.logger.set_log_level_debug)
        self.ui.actionLogInfo.triggered.connect(self.logger.set_log_level_info)
        self.ui.actionLogWarning.triggered.connect(self.logger.set_log_level_warning)

    def check_steps(self):
        """Check for updates of the steps in the album."""
        self.album_api.check_steps()

    def update_steps(self):
        """Update the steps in the album."""
        self.album_api.update_steps()

    def reinstall_steps(self):
        """Reinstall all steps in the album."""
        # ask again for permission
        reply = QMessageBox.question(
            self,
            "Confirm Reinstall",
            "This will re-install all steps. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.album_api.reinstall_steps()

    def openImage(self):
        """Open the image viewer window."""
        self.image_view_controller.setup_ui()
        self.image_view_controller.open_file_window.show()

    def closeViewer(self):
        """Close the image viewer window."""
        self.image_view_controller.close_viewer()

    def openParticleSegWindow(self):
        """Open the particle segmentation window."""
        self.particle_seg_dialog_controller.setup_ui()
        # self.particle_seg_dialog_controller.particle_seg_window_ui.pushButton.clicked.connect(self.openParticleSegWindowAdvanced)
        self.particle_seg_dialog_controller.particle_seg_window.show()

    def openParticleSegWindowAdvanced(self):
        """Open the advanced particle segmentation window."""
        self.particle_seg_dialog_controller.particle_seg_window.hide()

        # open the advanced particle segmentation window
        self.particle_seg_dialog_advanced_controller.setup_ui()
        self.particle_seg_dialog_advanced_controller.particle_seg_window.show()

    def openStreamlitWindow(self):
        """Open the streamlit data viewer window."""
        self.data_viewer_controller.setup_ui()
        self.data_viewer_controller.streamlit_window.show()

    def extractProperties(self):
        """Open the extract properties dialog."""
        self.extract_histogram_controller.setup_ui()
        self.extract_histogram_controller.extract_histogram.show()
