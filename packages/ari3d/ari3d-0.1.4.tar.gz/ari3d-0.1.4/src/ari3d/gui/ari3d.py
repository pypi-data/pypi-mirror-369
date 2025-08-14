"""File to run the main window and give connections to menu items."""
import sys

from PyQt6.QtWidgets import QApplication

from ari3d.gui.controller.window_c import WindowController


def run_gui():
    """Run the main GUI application."""
    app = QApplication(sys.argv)
    window = WindowController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
