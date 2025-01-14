from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap
from PyQt5.QtCore import QRectF, Qt, QPointF, QSizeF, QTimer

class Canvas(QtWidgets.QGraphicsView):
    """Custom canvas widget for image visualization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_canvas()
        self._init_variables()
        self._create_scene()
        self._setup_canvas_rect()
        self.set_initial_zoom()

    def _setup_canvas(self):
        """Initialize canvas properties."""
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(QColor(57, 57, 57)))

    def _init_variables(self):
        """Initialize instance variables."""
        self._drag_start_pos = None
        self.current_scale = 1.0
        self.is_panning = False
        self.image_items = []  # Store all image items
        self.canvas_size = QSizeF(800, 600)
        self._center_requested = False  # Flag to track centering request

    def _create_scene(self):
        """Create and setup the graphics scene."""
        self.scene = QtWidgets.QGraphicsScene(self)
        self.workspace_size = QRectF(-2000, -2000, 4000, 4000)
        self.scene.setSceneRect(self.workspace_size)
        self.setScene(self.scene)

    def _setup_canvas_rect(self):
        """Setup the canvas rectangle."""
        self.canvas_rect = self.scene.addRect(
            -self.canvas_size.width() / 2,
            -self.canvas_size.height() / 2,
            self.canvas_size.width(),
            self.canvas_size.height(),
            QtGui.QPen(QColor(200, 200, 200)),
            QtGui.QBrush(Qt.transparent)
        )

    def set_initial_zoom(self):
        """Set the initial zoom level and center the canvas."""
        # Set initial zoom to 50%
        initial_zoom_factor = 0.5
        self.resetTransform()
        self.scale(initial_zoom_factor, initial_zoom_factor)
        self.current_scale = initial_zoom_factor
        
        # Calculate the center point of the canvas
        center_point = QPointF(0, 0)  # Since our canvas rect is centered around (0,0)
        
        # Center on this point
        self.centerOn(center_point)
        
        # Ensure the canvas is visible and centered after Qt finishes layout
        QTimer.singleShot(0, self._ensure_centered)

    def drawBackground(self, painter, rect):
        """Draw checkered pattern for the entire workspace."""
        dark_gray = QColor(80, 80, 80)
        darker_gray = QColor(60, 60, 60)
        grid_size = 20

        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                if ((x // grid_size + y // grid_size) % 2) == 0:
                    painter.fillRect(x, y, grid_size, grid_size, dark_gray)
                else:
                    painter.fillRect(x, y, grid_size, grid_size, darker_gray)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.is_panning = True
            self.setCursor(Qt.ClosedHandCursor)
            self._drag_start_pos = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.is_panning and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self._drag_start_pos
            self._drag_start_pos = event.pos()

            scrollbar_h = self.horizontalScrollBar()
            scrollbar_v = self.verticalScrollBar()
            scrollbar_h.setValue(scrollbar_h.value() - delta.x())
            scrollbar_v.setValue(scrollbar_v.value() - delta.y())

            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        mouse_pos = self.mapToScene(event.pos())

        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        new_scale = self.current_scale * zoom_factor

        if 0.1 <= new_scale <= 5.0:
            viewport_center = self.mapToScene(self.viewport().rect().center())
            self.scale(zoom_factor, zoom_factor)
            self.current_scale = new_scale
            new_mouse_pos = self.mapToScene(event.pos())
            delta = new_mouse_pos - mouse_pos
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() + delta.x()))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() + delta.y()))

        event.accept()

    def clear_scene(self):
        """Clear all items from the scene."""
        if hasattr(self, 'scene'):
            self.scene.clear()
            self._setup_canvas_rect()
            self.image_items.clear()

    def add_image_layer(self, pixmap):
        """Add an image layer to the scene."""
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                self.canvas_size.toSize(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            image_item = self.scene.addPixmap(scaled_pixmap)
            x_offset = -scaled_pixmap.width() / 2
            y_offset = -scaled_pixmap.height() / 2
            image_item.setPos(x_offset, y_offset)
            self.image_items.append(image_item)

    def has_layers(self):
        """Check if canvas has any layers."""
        return len(self.image_items) > 0
        
    def _ensure_centered(self):
        """Ensure the canvas is centered in the viewport."""
        if not self._center_requested:
            self._center_requested = True
            self.fitInView(self.canvas_rect, Qt.KeepAspectRatio)
            # Reset to our desired 50% zoom
            self.resetTransform()
            self.scale(0.5, 0.5)
            self.current_scale = 0.5
            # Center on the canvas rect
            self.centerOn(0, 0)
            
    def resizeEvent(self, event):
        """Handle resize events to maintain centering."""
        super().resizeEvent(event)
        if not self._center_requested:
            self._ensure_centered()