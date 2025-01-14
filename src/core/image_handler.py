import cv2
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtWidgets import QMessageBox

class ImageHandler:
    """Handles image loading, processing and saving operations."""
    
    @staticmethod
    def load_image(file_path):
        """Load and process an image file."""
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            return None
            
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        h, w, ch = image.shape
        bytes_per_line = ch * w
        format = QImage.Format_RGBA8888 if ch == 4 else QImage.Format_RGB888
        q_img = QImage(image.data, w, h, bytes_per_line, format)
        return QPixmap.fromImage(q_img)

    @staticmethod
    def save_image(canvas, file_path, file_extension):
        """Save the image to disk."""
        canvas_rect = canvas.canvas_rect.rect()
        canvas_rect = QRectF(
            canvas_rect.x() + canvas.canvas_rect.pos().x(),
            canvas_rect.y() + canvas.canvas_rect.pos().y(),
            canvas_rect.width(),
            canvas_rect.height()
        )

        pixmap = QPixmap(int(canvas_rect.width()), int(canvas_rect.height()))
        pixmap.fill(Qt.transparent)

        canvas.canvas_rect.setVisible(False)
        painter = QPainter(pixmap)
        canvas.scene.render(
            painter,
            QRectF(pixmap.rect()),
            canvas_rect
        )
        painter.end()
        canvas.canvas_rect.setVisible(True)

        return pixmap.save(file_path, file_extension.upper())