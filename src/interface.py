import sys
import os
import cv2
import res_rc
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QToolButton,QMessageBox
from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtGui import QImage, QPixmap, QCursor, QPainter


class ImageVisualizer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(ImageVisualizer, self).__init__(parent)
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._drag_start_pos = None
        self.image_item = None
        self.setRenderHint(QPainter.Antialiasing)  # Smooth rendering
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)  # Enable free dragging
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self._drag_start_pos = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            delta = event.pos() - self._drag_start_pos
            self._drag_start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()

    def wheelEvent(self, event):
        # Zoom in/out with scroll
        if self.image_item:  # Ensure image_item exists before zooming
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        event.accept()

    def zoom_in(self):
        if self.image_item:
            current_scale = self.image_item.scale()
            new_scale = current_scale * 1.1
            if new_scale <= 50:  # Max zoom limit
                self.image_item.setScale(new_scale)
                self.adjust_scene_boundaries()

    def zoom_out(self):
        if self.image_item:
            current_scale = self.image_item.scale()
            new_scale = current_scale / 1.1
            if new_scale >= 0.1:  # Min zoom limit
                self.image_item.setScale(new_scale)
                self.adjust_scene_boundaries()

    def adjust_scene_boundaries(self):
        if self.image_item:
            # Dynamically adjust the scene rect based on the image size
            new_rect = self.image_item.sceneBoundingRect()
            self.scene().setSceneRect(new_rect)


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)

        # Replace QGraphicsView with custom ImageVisualizer
        self.visualizer = self.findChild(QtWidgets.QGraphicsView, 'visualizer')
        self.custom_visualizer = ImageVisualizer(self)
        self.scene = QGraphicsScene(self)
        self.custom_visualizer.setScene(self.scene)

        # Replace the original visualizer with the custom one in the layout
        layout = self.visualizer.parentWidget().layout()
        layout.replaceWidget(self.visualizer, self.custom_visualizer)
        self.visualizer.deleteLater()

        # Initial setup
        self.panel_frame.setMinimumSize(0, 0)
        self.panel_frame.setMaximumSize(0, 1000000)

        self.currentImage = None
        self.currentToolButton = -1
        self.animations = []
        self.image_width = None
        self.image_height = None
        self.aspect_ratio = None

        self.image_item = None

        # Handle button clicks
        self.handle_button_clicks()

        # Connect Save button to the method
        

    def handle_button_clicks(self):
        self.adjust_button.clicked.connect(lambda: self.handle_button_page_binds(self.adjust_button, 0))
        self.effects_button.clicked.connect(lambda: self.handle_button_page_binds(self.effects_button, 1))
        self.add_image_push_button.clicked.connect(lambda: self.handle_add_image())
        self.save_button.clicked.connect(lambda: self.handle_save_image())

    def handle_button_page_binds(self, button, idx):
        self.stackedWidget_2.setCurrentIndex(idx)
        self.handle_panel_animation(idx)

    def handle_panel_animation(self, idx):
        clicked_button = self.sender()
        if self.currentToolButton == -1:
            self.currentToolButton = idx
            self.panel_animation("Open")
            clicked_button.setChecked(True)
        elif self.currentToolButton == idx:
            self.currentToolButton = -1
            self.panel_animation("Close")
            clicked_button.setChecked(False)
        else:
            self.currentToolButton = idx
            tool_buttons = self.findChildren(QToolButton)
            for button in tool_buttons:
                button.setChecked(False)
            clicked_button.setChecked(True)

    def panel_animation(self, which_anim):
        animation = QPropertyAnimation(self.panel_frame, b"minimumWidth")
        animation.setDuration(150)

        if which_anim == "Open":
            animation.setStartValue(0)
            animation.setEndValue(300)
        elif which_anim == "Close":
            animation.setStartValue(300)
            animation.setEndValue(0)

        self.animations.append(animation)
        animation.start()

    def handle_add_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.load_image(file_path)

    def load_image(self, file_path):
        # Load image as before
        image = cv2.imread(file_path)
        self.image_height, self.image_width, _ = image.shape
        self.aspect_ratio = self.image_width / self.image_height

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w
        q_img = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)

        if self.custom_visualizer.image_item:
            self.scene.removeItem(self.custom_visualizer.image_item)

        self.custom_visualizer.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.custom_visualizer.image_item)

        # Dynamically adjust scene rect based on new image
        self.custom_visualizer.adjust_scene_boundaries()

    def scale_to_fit(self):
        # Scale the image to fit the view while maintaining aspect ratio
        if self.custom_visualizer.image_item:
            self.custom_visualizer.image_item.setTransformationMode(QtCore.Qt.SmoothTransformation)
            self.custom_visualizer.image_item.setScale(min(self.custom_visualizer.width() / self.image_width,
                                         self.custom_visualizer.height() / self.image_height))

    def handle_save_image(self):
        """Handles saving the image with a dropdown list of valid formats."""
        if not self.custom_visualizer.image_item:  # Check if an image is loaded
            QMessageBox.warning(self, "No Image", "There is no image to save. Please load an image first.")
            return

        # List of valid formats
        valid_formats = ["png", "jpg", "jpeg", "bmp", "gif"]

        # Open file dialog
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)

        # Construct a filter string with valid formats
        format_filters = ";;".join([f"{fmt.upper()} (*.{fmt})" for fmt in valid_formats])
        file_dialog.setNameFilter(format_filters)
        file_dialog.setDefaultSuffix("png")  # Default to PNG format
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)

        if file_dialog.exec_():
            # Get the selected file path and filter
            file_path = file_dialog.selectedFiles()[0]
            selected_filter = file_dialog.selectedNameFilter()

            # Extract the extension from the selected filter
            file_extension = selected_filter.split("(*.")[-1].strip(")")

            # Validate and append the correct extension if necessary
            if not file_path.lower().endswith(f".{file_extension}"):
                file_path += f".{file_extension}"

            # Render the scene to a QPixmap
            scene_rect = self.scene.sceneRect()
            pixmap_width = int(scene_rect.width())
            pixmap_height = int(scene_rect.height())

            image = QPixmap(pixmap_width, pixmap_height)
            image.fill(QtCore.Qt.transparent)  # Transparent background
            painter = QPainter(image)
            self.scene.render(painter)  # Render scene contents onto the pixmap
            painter.end()

            # Save the QPixmap as an image file
            if image.save(file_path, file_extension.upper()):
                print(f"Image saved as {file_path} in format {file_extension.upper()}")
            else:
                QMessageBox.warning(self, "Save Error", f"Failed to save the image in {file_extension.upper()} format.")
                    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
