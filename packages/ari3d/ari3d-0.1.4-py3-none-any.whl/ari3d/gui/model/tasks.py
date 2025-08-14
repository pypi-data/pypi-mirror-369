"""Module for running solutions in a separate thread using QRunnable."""
from typing import Any, List, Callable

from PyQt6.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal, QThreadPool, Qt
from ari3d.gui.ari3d_logging import Ari3dLogger


class SequentialTaskRunner(QObject):
    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.current_index = 0
        self.logger = Ari3dLogger()

    def start(self):
        self.run_next_task()

    def run_next_task(self):
        if self.current_index < len(self.tasks):
            self.logger.log.info(f"Running task {self.current_index + 1}/{len(self.tasks)}")

            task = self.tasks[self.current_index]
            self.current_index += 1
            task.signals.done.connect(lambda done: self.logger.log.info(f"Task {self.current_index - 1} done: {done}"))
            task.signals.done.connect(self.run_next_task, Qt.ConnectionType.QueuedConnection)
            QThreadPool().globalInstance().start(task)
        else:
            self.logger.log.info("All startup tasks completed!")


class WorkerSignals(QObject):
    """Defines custom signals for worker tasks."""
    message = pyqtSignal(str)
    result = pyqtSignal(object)
    error = pyqtSignal(str)
    done = pyqtSignal(bool)


class ExecuteSolutionTask(QRunnable):
    """QRunnable task for updating a solution in a separate thread."""

    def __init__(self, fkt: Callable, message, fail_message, *args, **kwargs):
        """Initialize the task with the album API and solution ID."""
        super().__init__()
        self.signals = WorkerSignals()
        self.logger = Ari3dLogger()
        self.fkt = fkt
        self.message = message
        self.fail_message = fail_message
        self.args = args
        self.kwargs = kwargs
        self._done = False

    @pyqtSlot()
    def run(self):
        """Update the solution using the album API."""
        try:
            import logging
            from album.core.utils.core_logging import push_active_logger

            self.logger.log.debug(
                f"Running function {self.fkt.__name__} with arguments: {self.args}, {self.kwargs}"
            )

            push_active_logger(
                logging.getLogger("album")
            )  # we are in a thread. push the logger again

            r = self.fkt(*self.args, **self.kwargs)

            self.signals.message.emit(f"{self.message}")  # Emit success message
            if r is not None:
                self.signals.result.emit(r)
        except Exception as e:
            self.signals.error.emit(f"{self.fail_message}: {str(e)}")  # Emit error message
            raise e
        finally:
            self._done = True
            self.signals.done.emit(self._done)

    def is_done(self):
        return self._done


def attach_handler_once(target_logger, handler_to_add):
    """Attach a handler to a logger only if it's not already there."""
    if handler_to_add not in target_logger.handlers:
        target_logger.addHandler(handler_to_add)


class RunSolutionTask(QRunnable):
    """QRunnable task for running a solution in a separate thread."""

    def __init__(self, album_api, solution: str, argv: List[Any]):
        """Initialize the task with the album API, solution ID, and arguments."""
        super().__init__()
        self.album_api = album_api
        self.logger = Ari3dLogger()
        self.solution = solution
        self.argv = argv
        # self.signals = WorkerSignalsSolution()

    @pyqtSlot()
    def run(self):
        """Run the solution using the album API."""
        try:
            import logging

            from album.core.utils.core_logging import push_active_logger

            push_active_logger(
                logging.getLogger("album")
            )  # we are in a thread. push the logger again

            self.logger.log.debug(f"Running solution {self.solution} with arguments: {self.argv}")

            self.album_api._install_solution(self.solution)
            self.album_api.run(self.solution, argv=self.argv)
            if self.on_finished:
                self.on_finished()
        except Exception as e:
            if self.on_error:
                self.on_error(e)
            else:
                raise e
