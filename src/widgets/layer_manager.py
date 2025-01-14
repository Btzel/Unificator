from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QScrollArea, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .layer_widget import LayerWidget

class LayerManager(QFrame):
    """Manages the layer stack with Pixlr-style vertical reordering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.main_window = parent
        self.start_index = 1  # Initialize the starting index
        self._setup_ui()
        
    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Scroll area with custom styling
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for layers
        self.layer_container = QWidget()
        self.layer_layout = QVBoxLayout(self.layer_container)
        self.layer_layout.setAlignment(Qt.AlignTop)
        self.layer_layout.setSpacing(1)
        self.layer_layout.setContentsMargins(2, 2, 2, 2)
        
        self.scroll_area.setWidget(self.layer_container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Enhanced styling
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
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4d4d4d;
                min-height: 20px;
                border-radius: 5px;
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

    def add_layer(self, pixmap=None):
        """Add a new layer with automatic sequential naming."""
        layer_name = f"Layer {self.start_index}"
        layer_widget = LayerWidget(layer_name, len(self.layers), pixmap, self.layer_container)
        layer_widget.layerMoved.connect(self._handle_layer_moved)
        layer_widget.layerVisibilityChanged.connect(self._handle_visibility_changed)
        layer_widget.layerDeleted.connect(self._handle_layer_deleted)
        
        self.layers.insert(0, layer_widget)
        self.layer_layout.insertWidget(0, layer_widget)
        self._update_layer_indices()
        self._update_canvas()
        self.scroll_area.ensureWidgetVisible(layer_widget)
        self.start_index += 1

    def _update_layer_indices(self):
        """Update indices after reordering."""
        for i, layer in enumerate(self.layers):
            layer.index = len(self.layers) - 1 - i

    def _handle_layer_moved(self, from_index, to_index):
        """Handle layer reordering."""
        if from_index == to_index:
            return

        from_pos = None
        to_pos = None
        for i, layer in enumerate(self.layers):
            if layer.index == from_index:
                from_pos = i
            elif layer.index == to_index:
                to_pos = i
            if from_pos is not None and to_pos is not None:
                break

        if from_pos is None or to_pos is None:
            return

        moving_layer = self.layers.pop(from_pos)
        self.layer_layout.removeWidget(moving_layer)
        
        self.layers.insert(to_pos, moving_layer)
        self.layer_layout.insertWidget(to_pos, moving_layer)
        
        self._update_layer_indices()
        self._update_canvas()

    def _handle_visibility_changed(self, index, is_visible):
        """Handle layer visibility toggle."""
        self._update_canvas()

    def _handle_layer_deleted(self, index):
        """Handle layer deletion with dynamic renaming."""
        layer_to_delete = None
        deleted_layer_number = None
        
        # Find the layer to delete and its number
        for layer in self.layers:
            if layer.index == index:
                layer_to_delete = layer
                deleted_layer_number = int(layer.name_label.text().split()[1])
                break
                
        if layer_to_delete:
            self.layers.remove(layer_to_delete)
            self.layer_layout.removeWidget(layer_to_delete)
            layer_to_delete.deleteLater()
            
            # Rename layers with numbers greater than the deleted layer
            for layer in self.layers:
                current_number = int(layer.name_label.text().split()[1])
                if current_number > deleted_layer_number:
                    layer.name_label.setText(f"Layer {current_number - 1}")
            
            self._update_layer_indices()
            self._update_canvas()
            self.start_index -= 1  # Decrease the start_index for next layer addition

    def _update_canvas(self):
        """Update the canvas with current layer stack."""
        if hasattr(self.main_window, 'canvas'):
            canvas = self.main_window.canvas
            canvas.clear_scene()
            
            for layer in reversed(self.layers):
                if layer.is_visible and hasattr(layer, 'pixmap'):
                    canvas.add_image_layer(layer.pixmap)