from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QPushButton, 
                           QScrollArea, QApplication)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QColor
from .layer_widget import LayerWidget

class LayerManager(QFrame):
    """Manages the layer stack and handles layer reordering with vertical stacking."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.main_window = parent
        self._setup_ui()
        
    def _setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for layers
        self.layer_container = QWidget()
        self.layer_layout = QVBoxLayout(self.layer_container)
        self.layer_layout.setAlignment(Qt.AlignTop)
        self.layer_layout.setSpacing(2)
        self.layer_layout.setContentsMargins(2, 2, 2, 2)
        
        # Set container in scroll area
        self.scroll_area.setWidget(self.layer_container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Style
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#layer_container {
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4d4d4d;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5d5d5d;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.layer_container.setObjectName("layer_container")
        
    def add_layer(self, name, pixmap=None):
        """Add a new layer to the stack."""
        layer_widget = LayerWidget(name, len(self.layers), pixmap, self.layer_container)
        layer_widget.layerMoved.connect(self._handle_layer_moved)
        layer_widget.layerVisibilityChanged.connect(self._handle_visibility_changed)
        layer_widget.layerDeleted.connect(self._handle_layer_deleted)
        
        # Insert at the top of the stack
        self.layers.append(layer_widget)
        self.layer_layout.insertWidget(0, layer_widget)
        
        # Update indices and refresh view
        self._update_layer_indices()
        self._update_canvas()
        
        # Ensure new layer is visible
        self.scroll_area.ensureWidgetVisible(layer_widget)
        
    def _update_layer_indices(self):
        """Update the indices of all layers after reordering."""
        for i, layer in enumerate(self.layers):
            layer.index = len(self.layers) - 1 - i
            
    def _handle_layer_moved(self, from_index, to_index):
        """Handle layer reordering."""
        if from_index == to_index:
            return
            
        layer = self.layers.pop(from_index)
        self.layers.insert(to_index, layer)
        
        # Update UI
        self.layer_layout.removeWidget(layer)
        self.layer_layout.insertWidget(len(self.layers) - 1 - to_index, layer)
        
        self._update_layer_indices()
        self._update_canvas()
        
    def _handle_visibility_changed(self, index, is_visible):
        """Handle layer visibility changes."""
        self._update_canvas()
        
    def _handle_layer_deleted(self, index):
        """Handle layer deletion."""
        layer_to_delete = None
        for layer in self.layers:
            if layer.index == index:
                layer_to_delete = layer
                break
                
        if layer_to_delete:
            self.layers.remove(layer_to_delete)
            self.layer_layout.removeWidget(layer_to_delete)
            layer_to_delete.deleteLater()
            self._update_layer_indices()
            self._update_canvas()
        
    def drag_layer(self, from_index, global_pos):
        """Handle layer dragging."""
        container_pos = self.layer_container.mapFromGlobal(global_pos)
        target_idx = self._get_drop_index(container_pos.y())
        
        if target_idx != from_index:
            self._handle_layer_moved(from_index, target_idx)
            
    def _get_drop_index(self, y_pos):
        """Get the target index for a layer being dragged based on Y position."""
        layer_widgets = [self.layer_layout.itemAt(i).widget() 
                        for i in range(self.layer_layout.count())]
        
        for i, layer in enumerate(layer_widgets):
            widget_pos = layer.mapTo(self.layer_container, QPoint(0, 0))
            if y_pos < widget_pos.y() + layer.height():
                return len(self.layers) - 1 - i
                
        return 0
        
    def _update_canvas(self):
        """Update the canvas with current layer stack."""
        if hasattr(self.main_window, 'canvas'):
            canvas = self.main_window.canvas
            canvas.clear_scene()
            
            # Render layers from bottom to top
            for layer in reversed(self.layers):
                if layer.is_visible and hasattr(layer, 'pixmap'):
                    canvas.add_image_layer(layer.pixmap)