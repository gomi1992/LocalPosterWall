"""
海报墙组件模块

本模块实现了电影海报墙的核心UI组件，包括：
- RatingLabel: 电影评分显示标签
- ResolutionLabel: 分辨率显示标签  
- MoviePoster: 单个电影海报组件
- PosterWall: 海报墙滚动容器组件

这些组件负责以美观的方式展示电影信息，包括海报图片、标题、评分、分辨率等，
并提供交互功能如播放电影、查看详细信息等。

Author: LocalPosterWall Team
Version: 0.0.1
"""

import time
from PySide6.QtWidgets import (QWidget, QGridLayout, QLabel,
                               QScrollArea, QVBoxLayout, QPushButton)
from PySide6.QtCore import Qt, QTimer, QSize, QPoint
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter, QPainterPath, QMouseEvent
import subprocess
from pathlib import Path
from functools import lru_cache

from movie_info_dialog import MovieInfoDialog
from load_and_scale_image import load_and_scale_image
from loguru import logger


class RatingLabel(QLabel):
    """
    电影评分显示标签
    
    在海报左上角显示电影评分，使用金色渐变背景，
    数字格式化为保留一位小数的形式。
    """

    def __init__(self, rating, parent=None):
        """
        初始化评分标签
        
        Args:
            rating (float/str): 电影评分，支持数字或字符串
            parent (QWidget, optional): 父组件
        """
        super().__init__(parent)
        logger.debug(f"创建评分标签，评分: {rating}")

        try:
            # 尝试解析为浮点数并格式化
            rating_value = float(rating)
            rating_text = f"{rating_value:.1f}"
            logger.debug(f"评分格式化成功: {rating} -> {rating_text}")
        except (ValueError, TypeError):
            # 如果转换失败，直接使用原始字符串
            rating_text = str(rating)
            logger.warning(f"评分格式化为字符串: {rating} -> {rating_text}")

        # 设置显示文本
        self.setText(rating_text)
        logger.debug(f"评分标签文本设置完成: {rating_text}")

        # 应用评分标签样式
        self._apply_rating_style()

        # 设置居中对齐
        self.setAlignment(Qt.AlignCenter)
        logger.debug("评分标签初始化完成")

    def _apply_rating_style(self):
        """应用评分标签的样式"""
        logger.debug("应用评分标签样式")

        style = """
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
        """

        self.setStyleSheet(style)
        logger.debug("评分标签样式应用完成")


class ResolutionLabel(QLabel):
    """
    电影分辨率显示标签
    
    在海报右上角显示电影分辨率，使用蓝色渐变背景，
    用于标识视频质量信息。
    """

    def __init__(self, text, parent=None):
        """
        初始化分辨率标签
        
        Args:
            text (str): 分辨率文本（如"1080p", "4K"等）
            parent (QWidget, optional): 父组件
        """
        super().__init__(text, parent)
        logger.debug(f"创建分辨率标签，文本: {text}")

        # 应用分辨率标签样式
        self._apply_resolution_style()

        # 设置居中对齐
        self.setAlignment(Qt.AlignCenter)
        logger.debug("分辨率标签初始化完成")

    def _apply_resolution_style(self):
        """应用分辨率标签的样式"""
        logger.debug("应用分辨率标签样式")

        style = """
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
        """

        self.setStyleSheet(style)
        logger.debug("分辨率标签样式应用完成")


class MoviePoster(QWidget):
    """
    单个电影海报组件
    
    封装单个电影的完整显示界面，包括：
    - 海报图片显示
    - 评分和分辨率标签
    - 电影标题和年份
    - 播放按钮
    - 交互功能（点击查看详情、播放电影）
    
    支持鼠标悬停效果和阴影效果。
    """

    def __init__(self, movie_info, config_manager):
        """
        初始化电影海报组件
        
        Args:
            movie_info (dict): 电影信息字典
            config_manager: 配置管理器实例
        """
        super().__init__()

        # 保存电影信息和配置管理器
        self.movie_info = movie_info
        self.config_manager = config_manager

        logger.info(f"创建电影海报: {movie_info.get('title', 'Unknown')}")
        logger.debug(f"电影信息: {movie_info}")

        # 设置UI界面
        self.setup_ui()

        # 延迟加载海报图片，避免初始化时卡顿
        QTimer.singleShot(50, self.load_poster)
        logger.debug("海报组件初始化完成，延迟加载图片")

    def setup_ui(self):
        """
        设置海报组件的用户界面
        
        创建所有UI元素并设置布局，包括：
        - 海报容器
        - 评分和分辨率标签
        - 标题和年份显示
        - 播放按钮
        """
        logger.debug("开始设置电影海报UI")

        # 设置海报组件的固定尺寸
        self.setFixedSize(220, 380)
        logger.debug(f"海报组件尺寸设置为: 220x380")

        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        logger.debug("主布局创建完成")

        # 创建海报容器
        self._create_poster_container(layout)

        # 创建标题区域
        self._create_title_section(layout)

        # 应用整体样式
        self._apply_overall_style()

        logger.debug("电影海报UI设置完成")

    def _create_poster_container(self, parent_layout):
        """
        创建海报图片容器
        
        Args:
            parent_layout (QVBoxLayout): 父布局管理器
        """
        logger.debug("创建海报容器")

        # 海报容器部件
        self.poster_container = QWidget()
        self.poster_container.setFixedSize(208, 312)
        self.poster_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 12px;
            }
        """)
        logger.debug("海报容器创建完成，尺寸: 208x312")

        # 海报图片显示标签
        self.poster_label = QLabel(self.poster_container)
        self.poster_label.setFixedSize(208, 312)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("""
            QLabel {
                border: none;
                border-radius: 12px;
            }
        """)
        logger.debug("海报图片标签创建完成")

        # 添加评分标签
        self._add_rating_label()

        # 添加分辨率标签
        self._add_resolution_label()

        # 添加海报容器到布局
        parent_layout.addWidget(self.poster_container)
        logger.debug("海报容器已添加到布局")

    def _add_rating_label(self):
        """添加评分标签到海报容器"""
        logger.debug("添加评分标签")

        rating = self.movie_info.get('rating')
        if rating:
            logger.debug(f"电影有评分信息: {rating}")
            self.rating_label = RatingLabel(rating, self.poster_container)
            # 定位到左上角
            self.rating_label.move(10, 10)
            logger.debug("评分标签已定位到左上角")
        else:
            logger.debug("电影没有评分信息")
            self.rating_label = None

    def _add_resolution_label(self):
        """添加分辨率标签到海报容器"""
        logger.debug("添加分辨率标签")

        resolution = self.movie_info.get('resolution')
        if resolution:
            logger.debug(f"电影有分辨率信息: {resolution}")
            self.res_label = ResolutionLabel(resolution, self.poster_container)

            # 计算右上角位置
            self.res_label.adjustSize()  # 确保标签大小已计算
            container_width = self.poster_container.width()
            label_width = self.res_label.width()

            x_pos = container_width - label_width - 10  # 右边距10像素
            y_pos = 10  # 顶部距离10像素

            self.res_label.move(x_pos, y_pos)
            logger.debug(f"分辨率标签已定位到右上角: ({x_pos}, {y_pos})")
        else:
            logger.debug("电影没有分辨率信息")
            self.res_label = None

    def _create_title_section(self, parent_layout):
        """
        创建标题显示区域
        
        Args:
            parent_layout (QVBoxLayout): 父布局管理器
        """
        logger.debug("创建标题显示区域")

        # 标题容器
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 4, 0, 0)
        title_layout.setSpacing(2)

        # 电影标题
        title = self.movie_info.get('title', 'Unknown')
        logger.debug(f"设置电影标题: {title}")

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
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
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(44)
        logger.debug("电影标题标签创建完成")

        # 电影导演
        director = self.movie_info.get('director', 'Unknown')
        logger.debug(f"设置电影导演: {director}")

        self.director_label = QLabel(str(director))
        self.director_label.setStyleSheet("""
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
        self.director_label.setAlignment(Qt.AlignCenter)
        self.director_label.setWordWrap(True)
        self.director_label.setMaximumHeight(44)
        logger.debug("电影导演标签创建完成")

        # 电影演员
        actors = self.movie_info.get('actors', [])
        logger.debug(f"设置电影演员: {actors}")
        
        # 处理演员列表
        if isinstance(actors, list):
            actor_text = ', '.join(actors[:3])  # 最多显示前3个演员
            # 如果演员数量超过3个，添加省略号
            if len(actors) > 3:
                actor_text += '...'
        else:
            actor_text = str(actors) if actors else 'Unknown'

        self.actor_label = QLabel(actor_text)
        self.actor_label.setStyleSheet("""
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
        self.actor_label.setAlignment(Qt.AlignCenter)
        self.actor_label.setWordWrap(True)
        self.actor_label.setMaximumHeight(44)
        logger.debug("电影演员标签创建完成")

        # 年份显示
        year = self.movie_info.get('year', '')
        year_text = str(year) if year else ''
        logger.debug(f"设置电影年份: {year_text}")

        self.year_label = QLabel(year_text)
        self.year_label.setStyleSheet("""
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
        self.year_label.setAlignment(Qt.AlignCenter)
        logger.debug("电影年份标签创建完成")

        # 播放按钮
        self.play_button = QPushButton("播放")
        self._style_play_button()
        self.play_button.clicked.connect(self.play_movie)
        logger.debug("播放按钮创建完成")

        # 添加所有组件到标题布局
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.year_label)
        title_layout.addWidget(self.director_label)
        title_layout.addWidget(self.actor_label)
        title_layout.addWidget(self.play_button)

        # 添加标题容器到主布局
        parent_layout.addWidget(title_container)
        parent_layout.addStretch()
        logger.debug("标题显示区域创建完成")

    def _style_play_button(self):
        """设置播放按钮样式"""
        logger.debug("设置播放按钮样式")

        style = """
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
        """

        self.play_button.setStyleSheet(style)
        logger.debug("播放按钮样式设置完成")

    def _apply_overall_style(self):
        """应用海报组件整体样式"""
        logger.debug("应用海报组件整体样式")

        style = """
            QWidget {
                background-color: transparent;
            }
        """

        self.setStyleSheet(style)
        logger.debug("海报组件整体样式应用完成")

    def paintEvent(self, event):
        """
        自定义绘制事件，添加阴影和悬停效果
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        logger.debug("执行海报组件绘制事件")

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制阴影效果
        self._draw_shadow(painter)

        # 如果鼠标悬停，绘制发光效果
        if self.underMouse():
            logger.debug("鼠标悬停，绘制发光效果")
            self._draw_glow_effect(painter)

    def _draw_shadow(self, painter):
        """
        绘制阴影效果
        
        Args:
            painter (QPainter): 绘图器
        """
        logger.debug("绘制阴影效果")

        shadow_path = QPainterPath()
        # 获取海报容器几何信息
        geometry = self.poster_container.geometry()
        shadow_path.addRoundedRect(geometry, 12, 12)

        # 使用半透明黑色填充
        shadow_color = QColor(0, 0, 0, 40)  # 40/255 的透明度
        painter.fillPath(shadow_path, shadow_color)
        logger.debug("阴影效果绘制完成")

    def _draw_glow_effect(self, painter):
        """
        绘制发光效果（悬停时）
        
        Args:
            painter (QPainter): 绘图器
        """
        logger.debug("绘制发光效果")

        glow_path = QPainterPath()
        # 获取海报容器几何信息
        geometry = self.poster_container.geometry()
        glow_path.addRoundedRect(geometry, 12, 12)

        # 使用半透明白色填充创建发光效果
        glow_color = QColor(255, 255, 255, 15)  # 15/255 的透明度
        painter.fillPath(glow_path, glow_color)
        logger.debug("发光效果绘制完成")

    def enterEvent(self, event):
        """
        鼠标进入事件
        
        Args:
            event (QEvent): 进入事件
        """
        logger.debug("鼠标进入海报组件")
        self.update()  # 触发重绘以显示悬停效果

    def leaveEvent(self, event):
        """
        鼠标离开事件
        
        Args:
            event (QEvent): 离开事件
        """
        logger.debug("鼠标离开海报组件")
        self.update()  # 触发重绘以隐藏悬停效果

    def load_poster(self):
        """
        加载海报图片
        
        异步加载电影海报图片，如果加载失败则显示默认状态。
        使用定时器延迟调用，避免初始化时阻塞UI。
        """
        logger.info(f"开始加载电影海报: {self.movie_info.get('title', 'Unknown')}")
        start_time = time.time()

        poster_path = self.movie_info.get('poster_path')
        if not poster_path:
            logger.warning("电影海报路径为空，显示无海报状态")
            self.show_no_poster()
            return

        logger.debug(f"海报文件路径: {poster_path}")

        try:
            # 检查海报文件是否存在
            if not Path(poster_path).exists():
                logger.warning(f"海报文件不存在: {poster_path}")
                self.show_no_poster()
                return

            # 加载并缩放图片
            logger.debug("开始加载和缩放海报图片")
            scaled_pixmap = load_and_scale_image(
                poster_path,
                self.poster_label.width(),
                self.poster_label.height()
            )

            if scaled_pixmap:
                logger.info("海报图片加载成功")
                self.poster_label.setPixmap(scaled_pixmap)

                load_time = time.time() - start_time
                logger.debug(f"海报加载耗时: {load_time:.3f}秒")
            else:
                logger.warning("海报图片缩放失败，显示无海报状态")
                self.show_no_poster()

        except Exception as e:
            logger.exception(f"加载海报图片失败: {str(e)}")
            self.show_no_poster()

    def show_no_poster(self):
        """
        显示无海报状态
        
        当海报加载失败或不存在时，显示默认的占位符。
        """
        logger.debug("显示无海报状态")

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
        logger.debug("无海报状态显示完成")

    def mousePressEvent(self, event):
        """
        处理鼠标点击事件
        
        左键点击海报时打开电影详细信息对话框。
        
        Args:
            event (QMouseEvent): 鼠标事件
        """
        logger.info(f"用户点击电影海报: {self.movie_info.get('title', 'Unknown')}")

        if event.button() == Qt.LeftButton:
            logger.debug("左键点击，打开电影信息对话框")
            try:
                # 创建并显示电影信息对话框
                movie_info_dialog = MovieInfoDialog(self.movie_info)
                logger.debug("电影信息对话框创建成功，显示对话框")
                movie_info_dialog.exec()
                logger.debug("电影信息对话框已关闭")
            except Exception as e:
                logger.exception(f"打开电影信息对话框失败: {str(e)}")
        else:
            logger.debug(f"非左键点击，忽略事件: {event.button()}")

    def play_movie(self):
        """
        播放电影
        
        使用配置的播放器播放电影视频文件。
        先检查播放器路径是否有效，然后启动播放进程。
        """
        logger.info(f"开始播放电影: {self.movie_info.get('title', 'Unknown')}")

        try:
            # 获取配置文件
            config = self.config_manager.load_config()
            player_path = config.get('player_path')

            if not player_path:
                logger.warning("未配置播放器路径")
                return

            # 检查播放器文件是否存在
            if not Path(player_path).exists():
                logger.error(f"播放器文件不存在: {player_path}")
                return

            # 获取视频文件路径
            video_path = self.movie_info.get('video_path')
            if not video_path:
                logger.error("电影视频文件路径为空")
                return

            # 检查视频文件是否存在
            if not Path(video_path).exists():
                logger.error(f"视频文件不存在: {video_path}")
                return

            logger.info(f"使用播放器播放电影")
            logger.debug(f"播放器路径: {player_path}")
            logger.debug(f"视频路径: {video_path}")

            # 启动播放器进程
            process = subprocess.Popen([player_path, video_path])
            logger.info(f"播放器进程启动成功，PID: {process.pid}")

        except Exception as e:
            logger.exception(f"播放电影失败: {str(e)}")


class PosterWall(QScrollArea):
    """
    海报墙滚动容器组件
    
    继承自QScrollArea，提供可滚动的海报网格布局。
    自动计算列数并重新排列海报，适应窗口大小变化。
    支持动态更新海报列表和延迟重排布局。
    """

    def __init__(self, config_manager):
        """
        初始化海报墙容器
        
        Args:
            config_manager: 配置管理器实例
        """
        super().__init__()

        # 保存配置管理器
        self.config_manager = config_manager

        # 存储当前显示的电影列表
        self.current_movies = []

        # 延迟重排定时器，避免频繁重排造成性能问题
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)  # 单次触发
        self.resize_timer.timeout.connect(self.delayed_resize)

        logger.info("海报墙容器初始化完成")

        # 设置UI界面
        self.setup_ui()

    def setup_ui(self):
        """
        设置海报墙的用户界面
        
        配置滚动区域的样式，创建内容容器和网格布局。
        """
        logger.debug("设置海报墙UI")

        # 配置滚动区域属性
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        logger.debug("滚动区域属性设置完成")

        # 应用滚动区域样式
        self._apply_scroll_area_style()

        # 创建内容容器和网格布局
        self._create_content_container()

        logger.debug("海报墙UI设置完成")

    def _apply_scroll_area_style(self):
        """应用滚动区域样式"""
        logger.debug("应用滚动区域样式")

        style = """
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
        """

        self.setStyleSheet(style)
        logger.debug("滚动区域样式应用完成")

    def _create_content_container(self):
        """创建内容容器和网格布局"""
        logger.debug("创建内容容器")

        # 创建内容部件
        self.content = QWidget()
        self.content.setStyleSheet("background-color: #111;")
        self.setWidget(self.content)
        logger.debug("内容部件创建完成")

        # 创建网格布局
        self.grid_layout = QGridLayout(self.content)
        self.grid_layout.setSpacing(16)  # 海报间距
        self.grid_layout.setContentsMargins(16, 16, 16, 16)  # 边距
        self.content.setLayout(self.grid_layout)

        logger.debug("网格布局创建完成")

    def resizeEvent(self, event):
        """
        处理窗口大小改变事件
        
        当窗口大小改变时，延迟触发布局重排，避免频繁重排。
        
        Args:
            event (QResizeEvent): 大小改变事件
        """
        logger.debug(f"海报墙窗口大小改变: {event.oldSize()} -> {event.size()}")

        # 调用父类的事件处理
        super().resizeEvent(event)

        # 启动延迟重排定时器
        self.resize_timer.start(150)  # 150ms延迟
        logger.debug("启动延迟重排定时器")

    def delayed_resize(self):
        """
        延迟处理大小改变
        
        当窗口大小稳定后，重新计算布局并重排海报。
        """
        logger.debug("执行延迟布局重排")

        if self.current_movies:
            logger.info(f"重新排列 {len(self.current_movies)} 个海报")
            self.update_posters(self.current_movies)
        else:
            logger.debug("当前没有电影海报，无需重排")

    def calculate_layout(self):
        """
        计算布局参数
        
        根据当前窗口宽度自动计算可以显示的列数。
        
        Returns:
            int: 可以显示的列数
        """
        logger.debug("计算海报墙布局参数")

        # 可用宽度 = 窗口宽度 - 滚动条和边距
        available_width = self.width() - 48  # 考虑左右边距和滚动条
        poster_width = 236  # 海报组件宽度 (220 + 16间距)

        # 计算最大列数，最少1列
        cols = max(1, available_width // poster_width)

        logger.debug(f"计算布局参数:")
        logger.debug(f"  可用宽度: {available_width}")
        logger.debug(f"  海报宽度: {poster_width}")
        logger.debug(f"  计算列数: {cols}")

        return cols

    def update_posters(self, movies):
        """
        更新海报墙显示
        
        清空现有海报，重新计算布局并显示新的电影列表。
        
        Args:
            movies (list): 电影信息列表
        """
        logger.info("=" * 40)
        logger.info(f"开始更新海报墙，共 {len(movies)} 部电影")
        start_time = time.time()

        # 保存当前电影列表
        self.current_movies = movies
        logger.debug(f"保存电影列表，Count: {len(movies)}")

        try:
            # 清除现有海报
            self._clear_existing_posters()

            # 计算最大列数
            max_cols = self.calculate_layout()
            logger.info(f"计算得到的列数: {max_cols}")

            # 批量创建并添加海报
            self._batch_create_posters(movies, max_cols)

            update_time = time.time() - start_time
            logger.info(f"海报墙更新完成，耗时: {update_time:.2f}秒")
            logger.info("=" * 40)

        except Exception as e:
            logger.exception(f"更新海报墙失败: {str(e)}")

    def _clear_existing_posters(self):
        """清除现有的海报组件"""
        logger.debug("清除现有海报组件")

        poster_count = 0
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                self.grid_layout.removeItem(item)
                widget.deleteLater()
                poster_count += 1

        logger.debug(f"已清除 {poster_count} 个海报组件")

    def _batch_create_posters(self, movies, max_cols):
        """
        批量创建海报组件
        
        Args:
            movies (list): 电影信息列表
            max_cols (int): 最大列数
        """
        logger.debug(f"开始批量创建 {len(movies)} 个海报组件")

        row = col = 0

        for i, movie in enumerate(movies, 1):
            try:
                logger.debug(f"创建第 {i}/{len(movies)} 个海报: {movie.get('title', 'Unknown')}")

                # 创建海报组件
                poster = MoviePoster(movie, self.config_manager)

                # 添加到网格布局
                self.grid_layout.addWidget(poster, row, col)
                logger.debug(f"海报已添加到位置: 行{row}, 列{col}")

                # 更新行列索引
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            except Exception as e:
                logger.exception(f"创建第 {i} 个海报失败: {str(e)}")
                continue

        logger.info(f"海报组件批量创建完成，布局: {row + 1}行 x {max_cols}列")

    def clear_posters(self):
        """
        清除所有海报
        
        清空海报墙中的所有海报组件和布局项。
        """
        logger.info("清除海报墙中的所有海报")

        try:
            # 获取所有布局项并反向遍历（从后往前删除）
            item_list = list(range(self.grid_layout.count()))

            removed_count = 0
            for i in reversed(item_list):
                item = self.grid_layout.itemAt(i)
                if item:
                    # 从布局中移除项
                    self.grid_layout.removeItem(item)

                    # 如果有对应的组件，删除它
                    if item.widget():
                        item.widget().deleteLater()
                        removed_count += 1

            # 清空电影列表
            self.current_movies = []

            logger.info(f"已清除 {removed_count} 个海报组件")

        except Exception as e:
            logger.exception(f"清除海报时发生错误: {str(e)}")
