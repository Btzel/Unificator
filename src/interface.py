import sys
import os
import cv2
import res_rc
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QToolButton, QMessageBox, QColorDialog
from PyQt5.QtCore import QPropertyAnimation, QRect, QRectF, QPointF
from PyQt5.QtGui import QImage, QPixmap, QCursor, QPainter, QBrush, QColor
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QSize

class ImageVisualizer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(ImageVisualizer, self).__init__(parent)
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        # Set workspace background to rgb(57, 57, 57)
        self.setBackgroundBrush(QBrush(QColor(57, 57, 57)))

        # Create a large scene for the workspace
        self.scene = QtWidgets.QGraphicsScene(self)
        self.workspace_size = QRectF(-2000, -2000, 4000, 4000)
        self.scene.setSceneRect(self.workspace_size)
        self.setScene(self.scene)

        # Create canvas (transparent with outline)
        self.canvas_size = QtCore.QSizeF(800, 600)
        self.canvas_rect = self.scene.addRect(
            -self.canvas_size.width() / 2,
            -self.canvas_size.height() / 2,
            self.canvas_size.width(),
            self.canvas_size.height(),
            QtGui.QPen(QColor(200, 200, 200)),  # Light gray border
            QtGui.QBrush(QtCore.Qt.transparent)  # Transparent fill
        )

        self._drag_start_pos = None
        self.layers = []  # List to store layers (image items)
        self.current_scale = 1.0
        self.is_panning = False

        # Set initial zoom level (zoom out further than fit-to-view)
        self.set_initial_zoom()

    def set_initial_zoom(self):
        """Set the initial zoom level for a more zoomed-out view."""
        initial_zoom_factor = 0.5  # Adjust this value for more or less zoom-out
        self.resetTransform()
        self.scale(initial_zoom_factor, initial_zoom_factor)
        self.current_scale = initial_zoom_factor
        self.centerOn(0, 0)

    def drawBackground(self, painter, rect):
        # Draw checkered pattern for the entire workspace
        dark_gray = QColor(80, 80, 80)  # Darker gray
        darker_gray = QColor(60, 60, 60)  # Even darker gray
        grid_size = 20

        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # Draw the checkered pattern
        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                if ((x // grid_size + y // grid_size) % 2) == 0:
                    painter.fillRect(x, y, grid_size, grid_size, dark_gray)
                else:
                    painter.fillRect(x, y, grid_size, grid_size, darker_gray)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_panning = True
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self._drag_start_pos = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_panning and event.buttons() & QtCore.Qt.LeftButton:
            delta = event.pos() - self._drag_start_pos
            self._drag_start_pos = event.pos()

            scrollbar_h = self.horizontalScrollBar()
            scrollbar_v = self.verticalScrollBar()
            scrollbar_h.setValue(scrollbar_h.value() - delta.x())
            scrollbar_v.setValue(scrollbar_v.value() - delta.y())

            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()

    def wheelEvent(self, event):
        # Get the position of the mouse in scene coordinates before scaling
        mouse_pos = self.mapToScene(event.pos())

        # Calculate zoom factor
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        new_scale = self.current_scale * zoom_factor

        # Apply zoom limits
        if 0.1 <= new_scale <= 5.0:
            # Store the viewport center in scene coordinates
            viewport_center = self.mapToScene(self.viewport().rect().center())

            # Apply the scale
            self.scale(zoom_factor, zoom_factor)
            self.current_scale = new_scale

            # Get the new position of the mouse in scene coordinates
            new_mouse_pos = self.mapToScene(event.pos())

            # Calculate the offset
            delta = new_mouse_pos - mouse_pos

            # Move the scene to maintain the mouse position
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() + delta.x())
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() + delta.y())
            )

        event.accept()

    def set_image(self, image):
        """Set background layer."""
        self.clear_layers()  # Clear existing layers before setting a new image
        
        scaled_pixmap = image.scaled(
            self.canvas_size.toSize(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        background_item = self.scene.addPixmap(scaled_pixmap)
        self.layers.append(background_item)  # Add background as the first layer
        
        x_offset = -scaled_pixmap.width() / 2
        y_offset = -scaled_pixmap.height() / 2
        background_item.setPos(x_offset, y_offset)

        self.resetTransform()
        self.current_scale = 1.0
        self.centerOn(0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.centerOn(0, 0)

    def add_layer(self, image):
        """Add a new image as a layer on top of the existing ones."""
        if image is None:
            return
        
        scaled_pixmap = image.scaled(
            self.canvas_size.toSize(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        layer_item = self.scene.addPixmap(scaled_pixmap)
        self.layers.append(layer_item)  # Add new image as a layer

        x_offset = -scaled_pixmap.width() / 2
        y_offset = -scaled_pixmap.height() / 2
        layer_item.setPos(x_offset, y_offset)

    def clear_layers(self):
        """Clear all image layers."""
        for layer in self.layers:
            self.scene.removeItem(layer)
        self.layers.clear()

class DraggableLayerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None, layer_index=0):
        super(DraggableLayerWidget, self).__init__(parent)
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.original_pos = self.pos()  # Initialize original_pos
        self.drag_start_pos = None
        self.is_dragging = False
        self.layer_index = layer_index
        
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(150)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.original_pos = self.pos()  # Update original_pos
            self.is_dragging = True
            self.raise_()
            self.shadow.setBlurRadius(20)
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & QtCore.Qt.LeftButton:
            new_pos = self.mapToParent(event.pos() - self.drag_start_pos)
            new_pos.setX(self.pos().x())  # Use current x position instead of original
            self.move(new_pos)
            self.check_swap_position()
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.shadow.setBlurRadius(0)
            self.finalize_position()
            event.accept()
            
    def check_swap_position(self):
        if not self.parent() or not self.main_window:
            return
            
        current_pos = self.geometry().center().y()
        widgets = self.parent().findChildren(DraggableLayerWidget)
        widgets.sort(key=lambda w: w.geometry().y())
        
        for widget in widgets:
            if widget is not self:
                widget_pos = widget.geometry().center().y()
                if abs(current_pos - widget_pos) < self.height() / 2:
                    self.swap_with_widget(widget)
                    break
                    
    def swap_with_widget(self, other_widget):
        if not self.main_window:
            return
            
        layout = self.parent().layout()
        widgets = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, DraggableLayerWidget):
                widgets.append(widget)
        
        widgets.sort(key=lambda w: w.geometry().y())
        
        for idx, widget in enumerate(widgets):
            widget.layer_index = len(widgets) - 1 - idx
        
        layers = self.main_window.custom_visualizer.layers
        new_layers = []
        for widget in widgets:
            if 0 <= widget.layer_index < len(layers):
                new_layers.append(layers[widget.layer_index])
        
        self.main_window.custom_visualizer.layers = new_layers
        for i, layer in enumerate(new_layers):
            layer.setZValue(len(new_layers) - i)
        
        for widget in widgets:
            layout.removeWidget(widget)
        for widget in reversed(widgets):
            layout.addWidget(widget)
        
        self.main_window.custom_visualizer.scene.update()
                    
    def finalize_position(self):
        if not self.parent() or not self.main_window:
            return
            
        layout = self.parent().layout()
        widgets = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, DraggableLayerWidget):
                widgets.append(widget)
                widget.original_pos = widget.pos()  # Update original_pos for all widgets
        
        widgets.sort(key=lambda w: w.geometry().y())
        
        # Update indices and rearrange widgets
        for idx, widget in enumerate(widgets):
            widget.layer_index = len(widgets) - 1 - idx
            target_y = idx * (widget.height() + layout.spacing())
            
            # Use current x position for animation
            current_x = widget.pos().x()
            widget.pos_animation.setStartValue(widget.pos())
            widget.pos_animation.setEndValue(QtCore.QPoint(current_x, target_y))
            widget.pos_animation.start()
        
        # Update the visualizer layers
        layers = self.main_window.custom_visualizer.layers
        new_layers = []
        for widget in widgets:
            if 0 <= widget.layer_index < len(layers):
                new_layers.append(layers[widget.layer_index])
        
        self.main_window.custom_visualizer.layers = new_layers
        for i, layer in enumerate(new_layers):
            layer.setZValue(len(new_layers) - i)
        
        # Update the layout
        for widget in widgets:
            layout.removeWidget(widget)
        for widget in reversed(widgets):
            layout.addWidget(widget)
        
        self.main_window.custom_visualizer.scene.update()

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)

        # Setup custom visualizer
        self.visualizer = self.findChild(QtWidgets.QGraphicsView, 'visualizer')
        self.custom_visualizer = ImageVisualizer(self)

        # Replace the original visualizer
        layout = self.visualizer.parentWidget().layout()
        layout.replaceWidget(self.visualizer, self.custom_visualizer)
        self.visualizer.deleteLater()

        # Initial setup
        self.panel_frame.setMinimumSize(0, 0)
        self.panel_frame.setMaximumSize(0, 1000000)

        self.currentToolButton = -1
        self.animations = []

        # Replace scroll_layer_widget with layer_holder_frame
        # Initial setup for layer_holder_frame
        self.layer_holder_frame = self.findChild(QtWidgets.QFrame, 'layer_holder_frame')
        self.layer_layout = self.layer_holder_frame.layout()
        if self.layer_layout is None:
            self.layer_layout = QVBoxLayout(self.layer_holder_frame)
            self.layer_layout.setAlignment(QtCore.Qt.AlignTop)
            self.layer_holder_frame.setLayout(self.layer_layout)
        # Disable add layer button initially
        self.add_layer_push_button.setEnabled(False)

        # Handle button clicks
        self.handle_button_clicks()
        

    def handle_button_clicks(self):
        self.adjust_button.clicked.connect(
            lambda: self.handle_button_page_binds(self.adjust_button, 0))
        self.effects_button.clicked.connect(
            lambda: self.handle_button_page_binds(self.effects_button, 1))
        self.create_canvas_button.clicked.connect(self.handle_create_canvas)
        self.save_button.clicked.connect(self.handle_save_image)
        self.add_layer_push_button.clicked.connect(self.handle_add_layer)
        

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

    def handle_add_layer(self):
        """Open a file dialog to select an image and add it as a layer."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.load_layer_image(file_path)

    
    def load_layer_image(self, file_path):
        """Load an image and add it as a new layer."""
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            QMessageBox.warning(self, "Load Error",
                                "Failed to load the image. Please check the file format.")
            return

        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = image.shape
        bytes_per_line = ch * w
        format = QImage.Format_RGBA8888 if ch == 4 else QImage.Format_RGB888
        q_img = QImage(image.data, w, h, bytes_per_line, format)
        pixmap = QPixmap.fromImage(q_img)

        # Add the layer to the visualizer
        self.custom_visualizer.add_layer(pixmap)

        # Add the layer preview to the layer panel
        self.add_layer_preview(pixmap, f"Layer {len(self.custom_visualizer.layers)}")


    def add_layer_preview(self, pixmap, label_text):
        if pixmap.isNull():
            QMessageBox.warning(self, "Preview Error", "Failed to create thumbnail for the layer.")
            return
        
        layer_index = len(self.custom_visualizer.layers) - 1
        container_widget = DraggableLayerWidget(
            self.layer_holder_frame,
            main_window=self,
            layer_index=layer_index
        )
        
        layer_widget = QLabel()
        layer_widget.setPixmap(
            pixmap.scaled(QSize(100, 100), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        )
        layer_widget.setAlignment(QtCore.Qt.AlignCenter)
        container_widget.layout.addWidget(layer_widget)
        
        text_label = QLabel(label_text)
        text_label.setAlignment(QtCore.Qt.AlignCenter)
        container_widget.layout.addWidget(text_label)
        
        self.layer_layout.insertWidget(0, container_widget)
        container_widget.original_pos = container_widget.pos()  # Set initial original_pos
        self.custom_visualizer.layers[layer_index].setZValue(len(self.custom_visualizer.layers) - layer_index)

    def handle_create_canvas(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.create_canvas(file_path)

    def create_canvas(self, file_path):
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            QMessageBox.warning(self, "Load Error", 
                                "Failed to load the image. Please check the file format.")
            return

        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = image.shape
        bytes_per_line = ch * w
        format = QImage.Format_RGBA8888 if ch == 4 else QImage.Format_RGB888
        q_img = QImage(image.data, w, h, bytes_per_line, format)
        pixmap = QPixmap.fromImage(q_img)

        # Reset the visualizer and layer previews
        self.custom_visualizer.clear_layers()  # Clear all layers, including any background
        self.clear_layer_previews()           # Clear all layer previews in the panel

        # Set the image as the canvas background
        self.custom_visualizer.set_image(pixmap)

        # Enable "Add Layer" button
        self.add_layer_push_button.setEnabled(True)

        # Add canvas background to the layer panel
        self.add_layer_preview(pixmap, "Canvas Background")
    
    def clear_layer_previews(self):
        """Clear all layer previews from the layer panel."""
        while self.layer_layout.count():
            item = self.layer_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def handle_save_image(self):
        if not self.custom_visualizer.layers:  # Check if layers are empty
            QMessageBox.warning(self, "No Image", 
                                "There is no image to save. Please load an image first.")
            return

        valid_formats = ["png", "jpg", "jpeg", "bmp", "gif"]
        format_filters = ";;".join([f"{fmt.upper()} (*.{fmt})" for fmt in valid_formats])

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter(format_filters)
        file_dialog.setDefaultSuffix("png")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            selected_filter = file_dialog.selectedNameFilter()
            file_extension = selected_filter.split("(*.")[-1].strip(")")

            if not file_path.lower().endswith(f".{file_extension}"):
                file_path += f".{file_extension}"

            keep_transparency = False
            if file_extension.lower() == "png":
                response = QMessageBox.question(
                    self, "Transparency",
                    "Do you want to preserve transparency in the saved image?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                keep_transparency = (response == QMessageBox.Yes)

            if not keep_transparency:
                color = QColorDialog.getColor(QtCore.Qt.white, self, 
                                            "Choose Background Color")
                background_color = color if color.isValid() else QtCore.Qt.white
            else:
                background_color = QtCore.Qt.transparent

            # Get the canvas rectangle region
            canvas_rect = self.custom_visualizer.canvas_rect.rect()
            canvas_rect = QRectF(
                canvas_rect.x() + self.custom_visualizer.canvas_rect.pos().x(),
                canvas_rect.y() + self.custom_visualizer.canvas_rect.pos().y(),
                canvas_rect.width(),
                canvas_rect.height()
            )

            # Create a new pixmap for saving
            pixmap = QPixmap(int(canvas_rect.width()), int(canvas_rect.height()))
            pixmap.fill(background_color)

            # Temporarily hide the canvas_rect from the scene
            self.custom_visualizer.canvas_rect.setVisible(False)

            # Render only the content of the scene within the canvas bounds
            painter = QPainter(pixmap)
            self.custom_visualizer.scene.render(
                painter,
                QRectF(pixmap.rect()),
                canvas_rect
            )
            painter.end()

            # Restore the visibility of the canvas_rect
            self.custom_visualizer.canvas_rect.setVisible(True)

            if pixmap.save(file_path, file_extension.upper()):
                QMessageBox.information(self, "Success", 
                                        f"Image saved successfully as {file_path}")
            else:
                QMessageBox.warning(self, "Save Error", 
                                    f"Failed to save the image in {file_extension.upper()} format.")
                
    def swap_layers(self, widget1, widget2):
        """Swap two layer widgets and their corresponding image layers"""
        # Get indices
        idx1 = widget1.index
        idx2 = widget2.index
        
        # Swap visualization layers
        if 0 <= idx1 < len(self.custom_visualizer.layers) and \
           0 <= idx2 < len(self.custom_visualizer.layers):
            # Swap the actual layers in the visualizer
            self.custom_visualizer.layers[idx1], self.custom_visualizer.layers[idx2] = \
                self.custom_visualizer.layers[idx2], self.custom_visualizer.layers[idx1]
            
            # Update z-values to reflect new order
            self.custom_visualizer.layers[idx1].setZValue(idx1)
            self.custom_visualizer.layers[idx2].setZValue(idx2)
            
            # Update widget indices
            widget1.index, widget2.index = widget2.index, widget1.index
            
            # Update scene
            self.custom_visualizer.scene.update()
