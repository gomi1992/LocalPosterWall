from PySide6.QtWidgets import (QWidget, QGridLayout, QLabel,
                               QScrollArea, QVBoxLayout, QPushButton)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter, QPainterPath
import subprocess
from pathlib import Path
from functools import lru_cache

from movie_info_dialog import MovieInfoDialog
from load_and_scale_image import load_and_scale_image


class RatingLabel(QLabel):
    """评分标签"""

    def __init__(self, rating, parent=None):
        super().__init__(parent)
        # 格式化评分，保留一位小数
        try:
            rating_value = float(rating)
            rating_text = f"{rating_value:.1f}"
        except (ValueError, TypeError):
            rating_text = str(rating)

        self.setText(rating_text)
        self.setStyleSheet("""
            QLabel {
                color: #ffcc33;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(0, 0, 0, 0.9), 
                    stop:1 rgba(0, 0, 0, 0.6));
                padding: 3px 8px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
            }
        """)
        self.setAlignment(Qt.AlignCenter)


class ResolutionLabel(QLabel):
    """分辨率标签"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                color: #00ccff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(0, 0, 0, 0.9), 
                    stop:1 rgba(0, 0, 0, 0.6));
                padding: 3px 8px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
            }
        """)
        self.setAlignment(Qt.AlignCenter)


class MoviePoster(QWidget):
    def __init__(self, movie_info, config_manager):
        super().__init__()
        self.movie_info = movie_info
        self.config_manager = config_manager
        self.setup_ui()
        QTimer.singleShot(50, self.load_poster)

    def setup_ui(self):
        """设置海报UI"""
        self.setFixedSize(220, 380)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 海报容器
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
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("""
            QLabel {
                border: none;
                border-radius: 12px;
            }
        """)

        # 评分标签
        if self.movie_info.get('rating'):
            self.rating_label = RatingLabel(self.movie_info['rating'],
                                            self.poster_container)
            # 左上角位置
            self.rating_label.move(10, 10)

        # 分辨率标签
        if self.movie_info.get('resolution'):
            self.res_label = ResolutionLabel(self.movie_info['resolution'],
                                             self.poster_container)
            # 右上角位置，需要在标签创建后计算
            self.res_label.adjustSize()  # 确保标签大小已计算
            self.res_label.move(
                self.poster_container.width() - self.res_label.width() - 10,
                10
            )

        # 电影标题
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 4, 0, 0)
        title_layout.setSpacing(2)

        self.title_label = QLabel(self.movie_info['title'])
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(44)

        # 年份
        year = self.movie_info.get('year', '')
        self.year_label = QLabel(str(year) if year else '')
        self.year_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 13px;
                font-family: "Segoe UI", Arial;
            }
        """)
        self.year_label.setAlignment(Qt.AlignCenter)

        self.play_button = QPushButton("播放")
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #2ecc71;
                color: #2ecc71;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2ecc71;
                color: white;
            }
            
            QPushButton:pressed {
                background-color: #27ae60;
                border-color: #27ae60;
            }
        """)
        self.play_button.clicked.connect(self.play_movie)

        # 添加到标题容器
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.year_label)
        title_layout.addWidget(self.play_button)

        # 添加所有组件到主布局
        layout.addWidget(self.poster_container)
        layout.addWidget(title_container)
        layout.addStretch()

        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

    def paintEvent(self, event):
        """自定义绘制事件，添加阴影和悬停效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制阴影
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(self.poster_container.geometry(), 12, 12)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 40))

        # 如果鼠标悬停，绘制发光效果
        if self.underMouse():
            glow_path = QPainterPath()
            glow_path.addRoundedRect(self.poster_container.geometry(), 12, 12)
            painter.fillPath(glow_path, QColor(255, 255, 255, 15))

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.update()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.update()

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

    def mousePressEvent(self, event):
        """处理点击事件"""
        # if event.button() == Qt.LeftButton:
        #     self.play_movie()
        movie_info_dialog = MovieInfoDialog(self.movie_info)
        movie_info_dialog.exec()

    def play_movie(self):
        """播放电影"""
        config = self.config_manager.load_config()
        player_path = config.get('player_path')
        if player_path and Path(player_path).exists():
            try:
                subprocess.Popen([player_path, self.movie_info['video_path']])
            except Exception as e:
                print(f"Error playing movie: {e}")


class PosterWall(QScrollArea):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.current_movies = []
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.delayed_resize)
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #111;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #222;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #444;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
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

        # 创建内容窗口
        self.content = QWidget()
        self.content.setStyleSheet("background-color: #111;")
        self.setWidget(self.content)

        # 创建网格布局
        self.grid_layout = QGridLayout(self.content)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        self.content.setLayout(self.grid_layout)

    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        self.resize_timer.start(150)

    def delayed_resize(self):
        """延迟处理大小改变"""
        if self.current_movies:
            self.update_posters(self.current_movies)

    def calculate_layout(self):
        """计算布局参数"""
        available_width = self.width() - 48  # 考虑边距
        poster_width = 236  # 220 + 16(间距)
        cols = max(1, available_width // poster_width)
        return cols

    def update_posters(self, movies):
        """更新海报墙"""
        self.current_movies = movies

        # 清除现有内容
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 计算列数
        max_cols = self.calculate_layout()

        # 批量创建海报
        row = col = 0
        for movie in movies:
            poster = MoviePoster(movie, self.config_manager)
            self.grid_layout.addWidget(poster, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def clear_posters(self):
        item_list = reversed(range(self.grid_layout.count()))

        for i in item_list:
            item = self.grid_layout.itemAt(i)
            self.grid_layout.removeItem(item)
            # if item.widget():
            #     item.widget().deleteLater()
