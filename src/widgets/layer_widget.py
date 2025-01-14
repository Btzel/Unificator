from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QScrollArea,
                           QFrame, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor

class LayerWidget(QWidget):
    """Individual layer widget that can be dragged and reordered."""
    
    layerMoved = pyqtSignal(int, int)  # from_index, to_index
    layerVisibilityChanged = pyqtSignal(int, bool)  # layer_index, is_visible
    layerDeleted = pyqtSignal(int)  # layer_index
    
    def __init__(self, name, index, thumbnail=None, parent=None):
        super().__init__(parent)
        self.index = index
        self.is_visible = True
        self.pixmap = thumbnail
        self._setup_ui(name, thumbnail)
        
    def _setup_ui(self, name, thumbnail):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Visibility toggle button
        self.visibility_btn = QPushButton("👁")
        self.visibility_btn.setFixedSize(20, 20)
        self.visibility_btn.clicked.connect(self._toggle_visibility)
        layout.addWidget(self.visibility_btn)
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(30, 30)
        self.set_thumbnail(thumbnail)
        layout.addWidget(self.thumbnail_label)
        
        # Layer name
        self.name_label = QLabel(name)
        layout.addWidget(self.name_label)
        
        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        delete_btn.clicked.connect(self._delete_layer)
        layout.addWidget(delete_btn)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: white;
            }
            QPushButton {
                border: none;
                border-radius: 2px;
                background-color: #3d3d3d;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        
    def set_thumbnail(self, pixmap):
        """Set the thumbnail for the layer."""
        if pixmap:
            scaled_pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            # Create empty thumbnail
            empty_pixmap = QPixmap(30, 30)
            empty_pixmap.fill(QColor(80, 80, 80))
            self.thumbnail_label.setPixmap(empty_pixmap)
            
    def _toggle_visibility(self):
        """Toggle layer visibility."""
        self.is_visible = not self.is_visible
        self.visibility_btn.setText("👁" if self.is_visible else "⊘")
        self.layerVisibilityChanged.emit(self.index, self.is_visible)
        
    def _delete_layer(self):
        """Delete the layer."""
        self.layerDeleted.emit(self.index)

        
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if not hasattr(self, 'drag_start_position'):
            return
            
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return
            
        # Navigate up the widget hierarchy to find the LayerManager
        parent = self.parent()
        while parent and not isinstance(parent, QScrollArea):
            parent = parent.parent()
            
        if parent and parent.parent():
            layer_manager = parent.parent()
            if hasattr(layer_manager, 'drag_layer'):
                layer_manager.drag_layer(self.index, event.globalPos())
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release after dragging."""
        if hasattr(self, 'drag_start_position'):
            delattr(self, 'drag_start_position')