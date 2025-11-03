from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QListWidget,
                               QDialog, QLabel, QDialogButtonBox, QMessageBox,
                               QComboBox, QStatusBar, QScrollArea)

from PySide6.QtCore import Qt, QTimer, QSize

from load_and_scale_image import load_and_scale_image
import xml.etree.ElementTree as ET


class MovieInfoDialog(QDialog):

    def __init__(self, movie_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle('影片详情')
        self.setMinimumSize(500, 600)
        self.movie_info = movie_info
        self.setup_ui()
        QTimer.singleShot(50, self.load_poster)
        QTimer.singleShot(50, self.load_nfo_content)

    def setup_ui(self):

        layout = QVBoxLayout(self)

        self.scroll_container = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_container)

        self.scroll_container.setMinimumSize(450, 2000)

        title = QLabel()
        title.setText("title:" + self.movie_info['title'])
        title.setWordWrap(True)

        year = QLabel()
        year.setText("year:" + self.movie_info['year'])
        year.setWordWrap(True)

        rating = QLabel()
        rating.setText("rating:" + self.movie_info['rating'])
        rating.setWordWrap(True)

        resolution = QLabel()
        resolution.setText("resolution:" + self.movie_info['resolution'])
        resolution.setWordWrap(True)

        self.poster_container = QWidget()
        self.poster_container.setFixedSize(208, 312)
        self.poster_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 12px;
            }
        """)

        # 海报图片
        self.poster_label = QLabel(self.poster_container)
        self.poster_label.setFixedSize(208, 312)
        # self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("""
            QLabel {
                border: none;
                border-radius: 12px;
            }
        """)

        self.outline = QLabel()
        self.outline.setText("")
        self.outline.setWordWrap(True)

        scroll_layout.addWidget(title)
        scroll_layout.addWidget(year)
        scroll_layout.addWidget(rating)
        scroll_layout.addWidget(resolution)

        scroll_layout.addWidget(self.outline)
        scroll_layout.addWidget(self.poster_container)
        scroll_layout.addStretch(1)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.scroll_container)
        layout.addWidget(self.scroll)

        self.setStyleSheet("""
                    QListWidget {
                        background-color: #222;
                        color: white;
                        border: 1px solid #333;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QListWidget::item {
                        padding: 5px;
                        border-radius: 2px;
                    }
                    QListWidget::item:selected {
                        background-color: #444;
                    }
                    QListWidget::item:hover {
                        background-color: #333;
                    }
                    QPushButton {
                        background-color: #333;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #444;
                    }
                    QLabel {
                        color: black;
                    }
                """)

    def load_poster(self):
        """加载海报图片"""
        if self.movie_info['poster_path']:
            scaled_pixmap = load_and_scale_image(
                self.movie_info['poster_path'],
                self.poster_label.width(),
                self.poster_label.height()
            )
            if scaled_pixmap:
                self.poster_label.setPixmap(scaled_pixmap)
            else:
                self.show_no_poster()
        else:
            self.show_no_poster()

    def show_no_poster(self):
        """显示无海报状态"""
        self.poster_label.setText("无海报")
        self.poster_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 15px;
                font-family: "Segoe UI", Arial;
                border: 1px solid #333;
                border-radius: 12px;
                background-color: #222;
            }
        """)

    def load_nfo_content(self):
        # 解析 XML
        tree = ET.parse(Path(self.movie_info["nfo_path"]))
        root = tree.getroot()

        outline = None

        # 尝试读取评分
        rating_elem = root.find('outline')
        if rating_elem is not None and rating_elem.text:
            outline = rating_elem.text

        self.outline.setText("outline:" + outline)
