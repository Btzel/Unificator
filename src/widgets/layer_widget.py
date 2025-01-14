from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                           QFrame, QVBoxLayout, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QDrag, QCursor

class LayerWidget(QWidget):
    """Individual layer widget that can be dragged and reordered."""
    
    layerMoved = pyqtSignal(int, int)  # from_index, to_index
    layerVisibilityChanged = pyqtSignal(int, bool)  # layer_index, is_visible
    layerDeleted = pyqtSignal(int)  # layer_index
    dragStarted = pyqtSignal(int)  # dragged_index
    
    def __init__(self, name, index, thumbnail=None, parent=None):
        super().__init__(parent)
        self.index = index
        self.is_visible = True
        self.pixmap = thumbnail
        self._setup_ui(name, thumbnail)
        self.setAcceptDrops(True)
        self.drag_start_position = None
        
    def _setup_ui(self, name, thumbnail):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Visibility toggle button with improved styling
        self.visibility_btn = QPushButton("👁")
        self.visibility_btn.setFixedSize(24, 24)
        self.visibility_btn.clicked.connect(self._toggle_visibility)
        layout.addWidget(self.visibility_btn)
        
        # Thumbnail with border
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(40, 40)
        self.thumbnail_label.setStyleSheet("border: 1px solid #3d3d3d;")
        self.set_thumbnail(thumbnail)
        layout.addWidget(self.thumbnail_label)
        
        # Layer name with elision
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("padding-left: 5px;")
        layout.addWidget(self.name_label, stretch=1)
        
        # Delete button with improved styling
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(24, 24)
        delete_btn.clicked.connect(self._delete_layer)
        layout.addWidget(delete_btn)
        
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border-radius: 4px;
            }
            QPushButton {
                border: none;
                border-radius: 3px;
                background-color: #3d3d3d;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QLabel {
                font-size: 12px;
            }
        """)

    def set_thumbnail(self, pixmap):
        if pixmap:
            scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            empty_pixmap = QPixmap(40, 40)
            empty_pixmap.fill(QColor(80, 80, 80))
            self.thumbnail_label.setPixmap(empty_pixmap)

    def _toggle_visibility(self):
        self.is_visible = not self.is_visible
        self.visibility_btn.setText("👁" if self.is_visible else "⊘")
        self.layerVisibilityChanged.emit(self.index, self.is_visible)
        
    def _delete_layer(self):
        self.layerDeleted.emit(self.index)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or not self.drag_start_position:
            return
            
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # Create drag preview
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        pixmap.setDevicePixelRatio(2.0)  # For better quality
        
        # Make semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 180))
        painter.end()

        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.index))
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        self.dragStarted.emit(self.index)
        
        # Execute drag
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet(self.styleSheet() + """
                QWidget {
                    border: 2px solid #4a9eff;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("border: 2px solid #4a9eff;", ""))

    def dropEvent(self, event):
        from_index = int(event.mimeData().text())
        to_index = self.index
        
        if from_index != to_index:
            self.layerMoved.emit(from_index, to_index)
            
        self.setStyleSheet(self.styleSheet().replace("border: 2px solid #4a9eff;", ""))
        event.acceptProposedAction()