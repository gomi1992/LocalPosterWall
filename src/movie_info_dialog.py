"""
电影信息对话框模块

本模块实现电影详细信息查看对话框，用于显示电影的完整信息。
对话框以模态窗口形式展示电影的详细信息，包括海报、基本信息、
剧情简介等内容。

主要功能：
- 显示电影完整信息（标题、年份、评分、分辨率等）
- 展示电影海报图片
- 解析并显示NFO文件内容（剧情简介等）
- 支持滚动显示大量内容
- 美观的UI界面设计

UI特性：
- 暗色主题界面
- 可滚动的详情区域
- 海报图片自适应显示
- 响应式布局设计

Author: LocalPosterWall Team
Version: 0.0.1
"""

import time
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QListWidget,
                               QDialog, QLabel, QDialogButtonBox, QMessageBox,
                               QComboBox, QStatusBar, QScrollArea)

from PySide6.QtCore import Qt, QTimer, QSize

from load_and_scale_image import load_and_scale_image
import xml.etree.ElementTree as ET

from loguru import logger


class MovieInfoDialog(QDialog):
    """
    电影信息详细对话框
    
    以模态对话框形式显示电影的完整信息，包括：
    - 电影基本信息（标题、年份、评分、分辨率）
    - 电影海报图片
    - NFO文件解析的剧情简介等内容
    - 支持滚动查看完整内容
    
    使用延迟加载机制优化性能，海报和NFO内容异步加载。
    """
    
    def __init__(self, movie_info, parent=None):
        """
        初始化电影信息对话框
        
        Args:
            movie_info (dict): 电影信息字典
            parent (QWidget, optional): 父窗口组件
        """
        logger.info(f"创建电影信息对话框: {movie_info.get('title', 'Unknown')}")
        start_time = time.time()
        
        super().__init__(parent)
        
        # 保存电影信息
        self.movie_info = movie_info
        logger.debug(f"电影信息: {movie_info}")
        
        # 设置对话框属性
        self._setup_dialog_properties()
        
        # 设置用户界面
        self.setup_ui()
        
        # 延迟加载海报和NFO内容，避免界面卡顿
        QTimer.singleShot(50, self.load_poster)
        QTimer.singleShot(50, self.load_nfo_content)
        
        init_time = time.time() - start_time
        logger.debug(f"电影信息对话框初始化完成，耗时: {init_time:.3f}秒")
    
    def _setup_dialog_properties(self):
        """设置对话框基本属性"""
        logger.debug("设置对话框属性")
        
        # 设置窗口标题
        title = self.movie_info.get('title', '未知电影')
        self.setWindowTitle(f'影片详情 - {title}')
        logger.debug(f"窗口标题: {self.windowTitle()}")
        
        # 设置最小尺寸
        self.setMinimumSize(500, 600)
        logger.debug("对话框最小尺寸设置: 500x600")
        
        # 设置为模态对话框
        self.setModal(True)
        logger.debug("设置为模态对话框")
    
    def setup_ui(self):
        """
        设置用户界面
        
        创建对话框的完整UI布局，包括：
        - 滚动容器
        - 电影信息标签
        - 海报显示区域
        - 样式设置
        """
        logger.debug("设置电影信息对话框UI")
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        logger.debug("主布局创建完成")
        
        # 创建滚动容器
        self._create_scroll_container(layout)
        
        # 应用对话框样式
        self._apply_dialog_style()
        
        logger.debug("电影信息对话框UI设置完成")
    
    def _create_scroll_container(self, parent_layout):
        """
        创建滚动容器和内容
        
        Args:
            parent_layout (QVBoxLayout): 父布局管理器
        """
        logger.debug("创建滚动容器")
        
        # 创建滚动内容容器
        self.scroll_container = QWidget()
        self.scroll_container.setMinimumSize(450, 2000)
        
        # 创建滚动内容的布局
        scroll_layout = QVBoxLayout(self.scroll_container)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(15)
        logger.debug("滚动容器创建完成")
        
        # 创建信息标签
        self._create_info_labels(scroll_layout)
        
        # 创建海报显示区域
        self._create_poster_area(scroll_layout)
        
        # 创建滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.scroll_container)
        self.scroll.setWidgetResizable(True)
        parent_layout.addWidget(self.scroll)
        logger.debug("滚动区域创建完成")
    
    def _create_info_labels(self, layout):
        """
        创建电影信息标签
        
        Args:
            layout (QVBoxLayout): 要添加标签的布局管理器
        """
        logger.debug("创建电影信息标签")
        
        # 电影标题
        title_text = self.movie_info.get('title', '未知标题')
        title = QLabel(f"标题: {title_text}")
        title.setWordWrap(True)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 5px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        """)
        layout.addWidget(title)
        logger.debug(f"标题标签创建: {title_text}")
        
        # 发行年份
        year_text = self.movie_info.get('year', '未知')
        year = QLabel(f"年份: {year_text}")
        year.setWordWrap(True)
        year.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 3px;
            }
        """)
        layout.addWidget(year)
        logger.debug(f"年份标签创建: {year_text}")
        
        # 评分
        rating_text = self.movie_info.get('rating', '无评分')
        rating = QLabel(f"评分: {rating_text}")
        rating.setWordWrap(True)
        rating.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 3px;
            }
        """)
        layout.addWidget(rating)
        logger.debug(f"评分标签创建: {rating_text}")
        
        # 分辨率
        resolution_text = self.movie_info.get('resolution', '未知分辨率')
        resolution = QLabel(f"分辨率: {resolution_text}")
        resolution.setWordWrap(True)
        resolution.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 3px;
            }
        """)
        layout.addWidget(resolution)
        logger.debug(f"分辨率标签创建: {resolution_text}")
    
    def _create_poster_area(self, layout):
        """
        创建海报显示区域
        
        Args:
            layout (QVBoxLayout): 要添加海报的布局管理器
        """
        logger.debug("创建海报显示区域")
        
        # 海报容器
        self.poster_container = QWidget()
        self.poster_container.setFixedSize(208, 312)
        self.poster_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 12px;
                border: 2px solid #333;
            }
        """)
        logger.debug("海报容器创建完成")
        
        # 海报图片标签
        self.poster_label = QLabel(self.poster_container)
        self.poster_label.setFixedSize(208, 312)
        self.poster_label.setStyleSheet("""
            QLabel {
                border: none;
                border-radius: 10px;
                background-color: transparent;
            }
        """)
        logger.debug("海报标签创建完成")
        
        # 剧情简介标签
        self.outline = QLabel()
        self.outline.setText("")
        self.outline.setWordWrap(True)
        self.outline.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #444;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 5px;
                line-height: 1.5;
            }
        """)
        logger.debug("剧情简介标签创建完成")
        
        # 添加到布局
        layout.addWidget(self.outline)
        layout.addWidget(self.poster_container, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        
        logger.debug("海报区域添加到布局完成")
    
    def _apply_dialog_style(self):
        """应用对话框样式"""
        logger.debug("应用对话框样式")
        
        style = """
            QDialog {
                background-color: #f5f5f5;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #ddd;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #999;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        
        self.setStyleSheet(style)
        logger.debug("对话框样式应用完成")
    
    def load_poster(self):
        """
        加载海报图片
        
        异步加载电影海报图片，如果加载失败则显示默认状态。
        使用定时器延迟调用，避免初始化时阻塞UI。
        """
        logger.info(f"加载电影海报: {self.movie_info.get('title', 'Unknown')}")
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
        
        self.poster_label.setText("暂无海报")
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 16px;
                font-family: "Segoe UI", Arial;
                border: 2px dashed #999;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
        """)
        logger.debug("无海报状态显示完成")
    
    def load_nfo_content(self):
        """
        加载NFO文件内容
        
        解析NFO文件的XML格式，提取剧情简介等详细信息。
        使用延迟加载避免阻塞UI初始化。
        """
        logger.info(f"加载NFO内容: {self.movie_info.get('title', 'Unknown')}")
        start_time = time.time()
        
        try:
            nfo_path = self.movie_info.get('nfo_path')
            if not nfo_path:
                logger.debug("没有NFO文件路径")
                self.outline.setText("暂无剧情简介")
                return
            
            logger.debug(f"NFO文件路径: {nfo_path}")
            
            # 检查NFO文件是否存在
            nfo_file = Path(nfo_path)
            if not nfo_file.exists():
                logger.warning(f"NFO文件不存在: {nfo_path}")
                self.outline.setText("暂无剧情简介")
                return
            
            # 解析NFO文件的XML
            logger.debug("开始解析NFO文件的XML")
            tree = ET.parse(nfo_file)
            root = tree.getroot()
            logger.debug("XML解析完成")
            
            # 尝试读取剧情简介
            outline = self._extract_outline(root)
            
            if outline:
                self.outline.setText(f"剧情简介:\n{outline}")
                logger.info("成功加载剧情简介")
            else:
                self.outline.setText("暂无剧情简介")
                logger.debug("未找到剧情简介信息")
            
            load_time = time.time() - start_time
            logger.debug(f"NFO内容加载耗时: {load_time:.3f}秒")
            
        except ET.ParseError as e:
            logger.exception(f"NFO文件XML解析失败: {str(e)}")
            self.outline.setText("剧情简介解析失败")
        except Exception as e:
            logger.exception(f"加载NFO内容失败: {str(e)}")
            self.outline.setText("剧情简介加载失败")
    
    def _extract_outline(self, root):
        """
        从XML根元素提取剧情简介
        
        Args:
            root (Element): XML根元素
            
        Returns:
            str/None: 剧情简介文本，如果未找到则返回None
        """
        logger.debug("从NFO文件中提取剧情简介")
        
        try:
            # 尝试多种可能的剧情简介标签
            outline_tags = ['outline', 'plot', 'plotoutline', 'synopsis', 'summary']
            
            for tag in outline_tags:
                outline_elem = root.find(tag)
                if outline_elem is not None and outline_elem.text:
                    outline_text = outline_elem.text.strip()
                    if outline_text:
                        logger.debug(f"找到剧情简介 ({tag}): {outline_text[:100]}...")
                        return outline_text
            
            # 如果直接标签没找到，尝试在特定父元素下查找
            for parent_tag in ['info', 'metadata']:
                parent_elem = root.find(parent_tag)
                if parent_elem is not None:
                    for tag in outline_tags:
                        outline_elem = parent_elem.find(tag)
                        if outline_elem is not None and outline_elem.text:
                            outline_text = outline_elem.text.strip()
                            if outline_text:
                                logger.debug(f"在{parent_tag}下找到剧情简介: {outline_text[:100]}...")
                                return outline_text
            
            logger.debug("未找到剧情简介信息")
            return None
            
        except Exception as e:
            logger.exception(f"提取剧情简介失败: {str(e)}")
            return None
