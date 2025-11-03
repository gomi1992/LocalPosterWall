from PySide6.QtWidgets import (QWidget, QGridLayout, QLabel,
                               QScrollArea, QVBoxLayout, QPushButton)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter, QPainterPath
import subprocess
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=100)
def load_and_scale_image(image_path, width, height):
    """加载并缩放图片（带缓存）"""
    image = QImage(image_path)
    if not image.isNull():
        return QPixmap.fromImage(
            image.scaled(
                QSize(width, height),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
    return None
