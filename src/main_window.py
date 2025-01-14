from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import os
import res_rc
from widgets.canvas import Canvas
from widgets.panel_manager import PanelManager
from core.image_handler import ImageHandler

class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self._load_ui()
        self._setup_canvas()
        self._setup_panel_manager()
        self._connect_signals()

    def _load_ui(self):
        """Load the UI file."""
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)

    def _setup_canvas(self):
        """Setup the canvas widget."""
        self.visualizer = self.findChild(QtWidgets.QGraphicsView, 'visualizer')
        self.canvas = Canvas(self)
        
        layout = self.visualizer.parentWidget().layout()
        layout.replaceWidget(self.visualizer, self.canvas)
        self.visualizer.deleteLater()

    def _setup_panel_manager(self):
        """Setup the panel manager."""
        self.panel_manager = PanelManager(self.panel_frame)

    def _connect_signals(self):
        """Connect all signal handlers."""
        self.adjust_button.clicked.connect(
            lambda: self._handle_tool_button(self.adjust_button, 0))
        self.effects_button.clicked.connect(
            lambda: self._handle_tool_button(self.effects_button, 1))
        self.create_canvas_button.clicked.connect(self._handle_create_canvas)
        self.save_button.clicked.connect(self._handle_save_image)

    def _handle_tool_button(self, button, idx):
        """Handle tool button clicks."""
        self.stackedWidget_2.setCurrentIndex(idx)
        self.panel_manager.handle_panel_animation(idx, button)

    def _handle_create_canvas(self):
        """Handle creating new canvas with image."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            pixmap = ImageHandler.load_image(file_path)
            if pixmap:
                self.canvas.set_image(pixmap)
            else:
                QMessageBox.warning(self, "Load Error", 
                                  "Failed to load the image. Please check the file format.")

    def _handle_save_image(self):
        """Handle saving the canvas image."""
        if not self.canvas.image_item:
            QMessageBox.warning(self, "No Image", 
                              "There is no image to save. Please load an image first.")
            return

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;GIF (*.gif)")
        file_dialog.setDefaultSuffix("png")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)

        if file_dialog.exec_():
            self._save_dialog_accepted(file_dialog)

    def _save_dialog_accepted(self, file_dialog):
        """Handle accepted save dialog."""
        file_path = file_dialog.selectedFiles()[0]
        selected_filter = file_dialog.selectedNameFilter()
        file_extension = selected_filter.split("(*.")[-1].strip(")")

        if not file_path.lower().endswith(f".{file_extension}"):
            file_path += f".{file_extension}"

        if ImageHandler.save_image(self.canvas, file_path, file_extension):
            QMessageBox.information(self, "Success", 
                                  f"Image saved successfully as {file_path}")
        else:
            QMessageBox.warning(self, "Save Error", 
                              f"Failed to save the image in {file_extension.upper()} format.")