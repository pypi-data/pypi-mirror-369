"""Module for defining a file watcher for label files in the ari3d GUI model."""
from __future__ import annotations

import numpy as np
from napari.utils import DirectLabelColormap
from watchdog.events import FileSystemEventHandler

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.resources.default_values import DefaultValues


class FileWatcher(FileSystemEventHandler):
    """File watcher class to monitor changes in label files and update the viewer accordingly."""

    def __init__(self, file_path: str, caller: ImageViewController):  # noqa: F821
        """Initialize the file watcher with the file path and caller."""
        self.logger = Ari3dLogger()
        self.file_path = file_path
        self.caller = caller
        self._is_processing = False
        self._diff_deleted = None

        # load file to memory
        self.load_file()

    def on_modified(self, event):
        """Handle file modification events."""
        self.logger.log.debug(f"Event detected: {event}")
        # trigger loading changed file to memory
        if not event.is_directory and not self._is_processing:
            if event.src_path == self.file_path:
                self.logger.log.debug(f"File {self.file_path} has been modified!")
                _label_list_new, _diff_deleted = self.load_file()

                # highlight labels in viewer
                if self.caller.viewer is not None:
                    if "segmentation" in self.caller.viewer.layers:
                        layer = self.caller.viewer.layers["segmentation"]
                        # highlight labels
                        self.caller.highlight_labels_color(_label_list_new)

                        # display in highlighted particles list in viewer
                        self.caller.particle_highlight_widget.set_index_list(
                            _label_list_new
                        )

                        # restore labels
                        if _diff_deleted is not None and len(_diff_deleted) > 0:
                            self.caller.reset_labels_color(_diff_deleted)

                        direct_color_map = DirectLabelColormap(
                            color_dict=self.caller.current_colors
                        )
                        layer.colormap = direct_color_map

                del _diff_deleted
                del _label_list_new

    def load_file(self):
        """Load the label file into memory and return the updated label list."""
        # load file to memory
        self._is_processing = True
        _label_list_new = []

        # get the old label list
        _label_list_before = np.unique(self.caller._clicked_old)

        # update content and get the new label list
        _label_list_new = np.unique(
            self.caller.parse_labels_file()[
                DefaultValues.label_list_label_index.value
            ].to_numpy()
        )

        # compare old and new content
        diff_deleted = np.setdiff1d(_label_list_before, _label_list_new)
        self.logger.log.debug(
            f"Deleted elements between old and new content: {diff_deleted}"
        )

        # store diff to memory
        self._diff_deleted = diff_deleted

        self._is_processing = False

        return _label_list_new, diff_deleted

    def is_processing(self):
        """Check if the file watcher is currently processing a file modification."""
        return self._is_processing
