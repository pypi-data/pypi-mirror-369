"""Controller for managing the help and information features of the ari3d application."""
import webbrowser

from PyQt6.QtWidgets import QMessageBox, QWidget

from ari3d import __version__
from ari3d.resources.default_values import DefaultValues


class HelpController:
    """Controller class for managing help and information features in the ari3d application."""

    def __init__(self, parent: QWidget):
        """Initialize the HelpController with a parent widget."""
        self.parent = parent

    def show_about(self):
        """Show the about dialog with project information."""
        text = f"""
        <html>
        <head/>
        <body>
            <p>{DefaultValues.project_description.value}</p>
            <p><b>Version:</b> {__version__}</p>
            <p><b>License:</b> GNU GENERAL PUBLIC LICENSE v3</p>
            <p><b>Developed by:</b> {DefaultValues.developed_by.value}</p>
        </body>
        </html>
        """
        QMessageBox.about(
            self.parent,
            "ARI3D",
            text,
        )

    def open_code_repository(self):
        """Open the code repository in a web browser."""
        webbrowser.open(DefaultValues.repo_link.value)

    def open_documentation(self):
        """Open the documentation in a web browser."""
        webbrowser.open(DefaultValues.documentation_link.value)

    def open_tutorial(self):
        """Open the tutorial in a web browser."""
        webbrowser.open(DefaultValues.tutorial_link.value)

    def open_article(self):
        """Open the article in a web browser."""
        webbrowser.open(DefaultValues.article_link.value)
