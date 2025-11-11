"""
本地电影海报墙应用程序

本模块实现了一个基于PySide6的本地电影海报墙应用程序，用于扫描本地文件夹中的电影文件，
并以海报墙的形式展示。用户可以管理电影文件夹、配置播放器、按不同方式排序电影列表等。

主要功能：
- 扫描本地文件夹中的电影文件
- 自动获取电影信息和海报
- 支持多种排序方式（年份、标题等）
- 可配置本地播放器
- 缓存机制提高性能

Author: LocalPosterWall Team
Version: 0.0.1
"""

import sys
import os
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QListWidget,
                               QDialog, QLabel, QDialogButtonBox, QMessageBox,
                               QComboBox, QStatusBar, QLineEdit)
from PySide6.QtCore import Qt
from pathlib import Path
from config_manager import ConfigManager
from movie_scanner import MovieScanner
from poster_wall import PosterWall
import re
from pypinyin import lazy_pinyin

from status_message_manager import StatusMessageManager
from loguru import logger

from folder_list_dialog import FolderListDialog


# 配置日志记录器
# 每天轮转一次日志文件，保留3天的日志
# logger.add("movie_wall.log", rotation="1 day", retention=3, level="INFO")


class MovieWallApp(QMainWindow):
    """
    电影海报墙主应用程序窗口类
    
    继承自QMainWindow，是整个应用的主界面，包含：
    - 工具栏和菜单
    - 电影海报墙显示区域
    - 状态栏
    - 各种控制功能
    """

    def __init__(self):
        """
        初始化电影海报墙应用程序
        
        创建主窗口实例，初始化各个组件和配置。
        设置窗口基本属性，创建UI界面，并加载配置。
        """
        super().__init__()
        logger.info("=" * 50)
        logger.info("正在初始化电影海报墙应用程序")
        start_time = time.time()

        try:
            # 初始化配置管理器
            self.config_manager = ConfigManager()
            logger.info("配置管理器初始化完成")

            # 存储当前显示的电影列表
            self.current_movies = []
            # 存储原始电影列表（用于搜索功能）
            self.original_movies = []
            logger.info("电影列表初始化完成")

            # 初始化用户界面
            self.init_ui()

            # 显示初始化完成消息
            init_time = time.time() - start_time
            logger.info(f"应用程序初始化完成，耗时: {init_time:.2f}秒")
            self.status_bar.showMessage(f"初始化完成 - {init_time:.2f}秒", 3000)

        except Exception as e:
            logger.exception(f"应用程序初始化失败: {str(e)}")
            raise

    def init_ui(self):
        """
        初始化用户界面
        
        创建和配置主窗口的用户界面，包括：
        - 设置窗口标题和大小
        - 应用暗色主题样式
        - 创建控制栏（文件夹管理、播放器配置、刷新按钮）
        - 创建排序控制
        - 创建海报墙显示区域
        - 初始化状态栏
        """
        logger.info("正在初始化用户界面")

        # 设置窗口基本属性
        self.setWindowTitle('本地电影海报墙 v0.0.1')
        self.setMinimumSize(1200, 800)
        logger.debug("窗口基本属性设置完成")

        # 应用暗色主题样式表
        self._apply_dark_theme()
        logger.debug("暗色主题样式应用完成")

        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        logger.debug("主布局创建完成")

        # 创建顶部控制栏
        control_layout = self._create_control_bar()
        main_layout.addLayout(control_layout)
        logger.debug("控制栏创建完成")

        # 创建海报墙组件
        self.poster_wall = PosterWall(self.config_manager)
        main_layout.addWidget(self.poster_wall)
        logger.debug("海报墙组件创建完成")

        # 初始化状态栏
        self._init_status_bar()
        logger.debug("状态栏初始化完成")

        # 初始化消息管理器
        status_message_manager = StatusMessageManager.instance(self.status_bar)
        logger.debug("状态消息管理器初始化完成")

        # 初始化电影扫描器
        self.movie_scanner = MovieScanner()
        logger.debug("电影扫描器初始化完成")

        # 加载配置并扫描电影
        self.load_config()
        logger.info("用户界面初始化完成")

    def _apply_dark_theme(self):
        """
        应用暗色主题样式
        
        为整个应用程序设置统一的暗色主题样式，
        包括按钮、标签、列表框等控件的外观。
        """
        logger.debug("应用暗色主题样式")

        theme_styles = """
            QMainWindow {
                background-color: #1a1a1a;
            }
            QPushButton, QComboBox {
                background-color: #333;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover, QComboBox:hover {
                background-color: #444;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                color: white;
                font-size: 12px;
            }
            QComboBox::down-arrow:on {
                top: 1px;
                left: 1px;
            }
            QComboBox {
                padding-right: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: white;
                selection-background-color: #444;
                border: none;
            }
        """

        self.setStyleSheet(theme_styles)
        logger.debug("暗色主题样式应用成功")

    def _create_control_bar(self):
        """
        创建顶部控制栏
        
        创建包含文件夹管理、播放器配置、刷新按钮的顶部控制栏，
        以及右侧的排序选项控制。
        
        Returns:
            QHBoxLayout: 包含所有控制元素的水平布局
        """
        logger.debug("创建控制栏")

        control_layout = QHBoxLayout()

        # 左侧按钮组
        left_buttons = QHBoxLayout()

        # 文件夹管理按钮
        manage_folders_btn = QPushButton('管理文件夹')
        manage_folders_btn.clicked.connect(self.manage_folders)
        manage_folders_btn.setToolTip("管理电影文件夹路径")
        left_buttons.addWidget(manage_folders_btn)
        logger.debug("文件夹管理按钮创建完成")

        # 播放器配置按钮
        select_player_btn = QPushButton('选择播放器')
        select_player_btn.clicked.connect(self.configure_player)
        select_player_btn.setToolTip("配置本地视频播放器")
        left_buttons.addWidget(select_player_btn)
        logger.debug("播放器配置按钮创建完成")

        # 刷新列表按钮
        refresh_btn = QPushButton('刷新列表')
        refresh_btn.clicked.connect(self.refresh_movies)
        refresh_btn.setToolTip("重新扫描电影文件夹")
        left_buttons.addWidget(refresh_btn)
        logger.debug("刷新按钮创建完成")

        # 右侧排序选项
        right_controls = QHBoxLayout()

        sort_label = QLabel('排序方式：')
        sort_label.setStyleSheet('color: white;')
        sort_label.setToolTip("选择电影的排序方式")
        right_controls.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['按年份降序', '按年份升序', '按标题升序', '按标题降序', '按导演升序', '按导演降序', '按演员升序', '按演员降序'])
        self.sort_combo.currentTextChanged.connect(self.sort_movies)
        self.sort_combo.setToolTip("选择排序方式将立即应用到当前电影列表")
        right_controls.addWidget(self.sort_combo)
        logger.debug("排序控件创建完成")

        # 创建搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel('搜索：')
        search_label.setStyleSheet('color: white;')
        search_label.setToolTip("搜索电影标题、年份、导演或演员")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索...")
        self.search_input.setStyleSheet('background-color: #333; color: white; padding: 8px; border-radius: 4px;')
        self.search_input.textChanged.connect(self.search_movies)
        self.search_input.setMinimumWidth(250)
        search_layout.addWidget(self.search_input)
        
        # 添加到控制栏布局
        control_layout.addLayout(left_buttons)
        control_layout.addLayout(search_layout)
        control_layout.addStretch()
        control_layout.addLayout(right_controls)

        logger.debug("控制栏创建完成")
        return control_layout

    def _init_status_bar(self):
        """
        初始化状态栏
        
        创建和配置应用程序底部状态栏，显示版本信息。
        """
        logger.debug("初始化状态栏")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
        QLabel {
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(0, 0, 0, 0.9), 
                    stop:1 rgba(0, 0, 0, 0.6));
                padding: 3px 8px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
            }
            QStatusBar { 
             color: white;
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

        # 创建版本标签
        self.version_label = QLabel('版本: 0.0.1')
        self.version_label.setToolTip("本地电影海报墙版本信息")
        self.status_bar.addPermanentWidget(self.version_label)
        logger.debug("状态栏初始化完成")

    def load_config(self):
        """
        加载配置信息
        
        从配置管理器加载应用程序配置，包括：
        - 电影文件夹路径
        - 播放器路径
        其他配置项
        
        如果存在电影文件夹配置，优先从缓存加载电影列表，
        如果缓存为空或过期，则重新扫描文件夹。
        """
        logger.info("=" * 30)
        logger.info("开始加载配置")
        start_time = time.time()

        try:
            # 加载配置文件
            config = self.config_manager.load_config()
            logger.debug(f"配置文件内容: {config}")

            # 检查是否有配置的电影文件夹
            movie_folders = config.get('movie_folders', [])

            if movie_folders:
                logger.info(f"找到 {len(movie_folders)} 个电影文件夹配置")

                # 尝试从缓存加载电影列表
                logger.info("尝试从缓存加载电影列表")
                cached_movies = self.movie_scanner.cache_manager.get_cache()

                if cached_movies and len(cached_movies) > 0:
                    logger.info(f"缓存中找到 {len(cached_movies)} 部电影")
                    self.current_movies = cached_movies
                    self.original_movies = cached_movies.copy()  # 保存原始列表用于搜索
                    # 应用当前选择的排序方式
                    current_sort = self.sort_combo.currentText()
                    logger.info(f"应用排序方式: {current_sort}")
                    self.sort_movies(current_sort)
                else:
                    logger.info("缓存为空或无效，开始扫描电影文件夹")
                    self.scan_movies(movie_folders)
            else:
                logger.warning("未找到电影文件夹配置，请用户添加文件夹")
                self.status_bar.showMessage("请先添加电影文件夹", 3000)

            load_time = time.time() - start_time
            logger.info(f"配置加载完成，耗时: {load_time:.2f}秒")

        except Exception as e:
            logger.exception(f"加载配置失败: {str(e)}")
            self.status_bar.showMessage(f"加载配置失败: {str(e)}", 5000)

    def manage_folders(self):
        """
        管理电影文件夹
        
        打开文件夹管理对话框，允许用户添加、删除、编辑电影文件夹路径。
        用户确认后，更新配置并重新扫描电影列表。
        """
        logger.info("=" * 30)
        logger.info("开始管理电影文件夹")
        start_time = time.time()

        try:
            # 获取当前配置的文件夹
            config = self.config_manager.load_config()
            current_folders = config.get('movie_folders', [])
            logger.info(f"当前配置的文件夹数量: {len(current_folders)}")

            # 打开文件夹管理对话框
            dialog = FolderListDialog(current_folders, self)
            logger.info("文件夹管理对话框已打开，等待用户操作")

            if dialog.exec() == QDialog.Accepted:
                # 用户确认了更改
                new_folders = dialog.folders
                logger.info(f"用户确认的新文件夹列表: {new_folders}")
                logger.info(f"文件夹数量变化: {len(current_folders)} -> {len(new_folders)}")

                # 更新配置文件
                self.config_manager.update_config({'movie_folders': new_folders})
                logger.info("配置文件已更新")

                # 重新扫描电影文件夹
                logger.info("开始重新扫描电影文件夹")
                self.scan_movies(new_folders)

                manage_time = time.time() - start_time
                logger.info(f"文件夹管理完成，耗时: {manage_time:.2f}秒")
            else:
                logger.info("用户取消了文件夹管理操作")

        except Exception as e:
            logger.exception(f"管理文件夹失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'管理文件夹失败：{str(e)}')
            self.status_bar.showMessage("文件夹管理失败", 3000)

    def configure_player(self):
        """
        配置播放器
        
        打开文件选择对话框，让用户选择本地视频播放器程序。
        验证所选文件的合法性后，保存到配置中。
        """
        logger.info("=" * 30)
        logger.info("开始配置播放器")

        try:
            # 打开文件选择对话框
            player_path, file_filter = QFileDialog.getOpenFileName(
                self,
                '选择视频播放器程序',
                "",  # 起始目录为空，使用系统默认目录
                "可执行文件 (*.exe);;所有文件 (*.*)"
            )

            if player_path:
                logger.info(f"用户选择的播放器路径: {player_path}")
                logger.debug(f"文件过滤器: {file_filter}")

                # 检查文件是否存在
                path = Path(player_path)
                if not path.exists():
                    error_msg = f"所选播放器程序不存在: {path}"
                    logger.error(error_msg)
                    QMessageBox.warning(self, '提示', '所选播放器程序不存在！')
                    return

                if not path.is_file():
                    error_msg = f"所选路径不是文件: {path}"
                    logger.error(error_msg)
                    QMessageBox.warning(self, '提示', '所选路径不是有效的文件！')
                    return

                # 检查文件是否可执行（在Windows上主要是检查扩展名）
                if not path.suffix.lower() in ['.exe', '.bat', '.cmd', '.com']:
                    logger.warning(f"文件可能不是可执行程序: {path.suffix}")

                # 保存到配置
                self.config_manager.update_config({'player_path': player_path})
                logger.info("播放器路径配置已保存")

                success_msg = f'播放器设置已更新！\n路径: {player_path}'
                logger.info(success_msg)
                QMessageBox.information(self, '提示', success_msg)
                self.status_bar.showMessage("播放器配置已更新", 3000)

            else:
                logger.info("用户取消了播放器选择操作")

        except Exception as e:
            logger.exception(f"配置播放器失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'设置播放器失败：{str(e)}')
            self.status_bar.showMessage("播放器配置失败", 3000)

    def refresh_movies(self):
        """
        刷新电影列表
        
        清除当前显示的海报，重新扫描配置的电影文件夹，
        并重新加载和排序电影列表。
        """
        logger.info("=" * 30)
        logger.info("开始刷新电影列表")
        start_time = time.time()

        # 显示开始刷新的状态消息
        self.status_bar.showMessage("正在刷新电影列表...", 0)  # 0表示不自动消失
        logger.info("状态栏显示: 正在刷新电影列表...")

        try:
            # 清除当前海报显示
            logger.info("清除当前海报显示")
            self.poster_wall.clear_posters()

            # 加载配置
            config = self.config_manager.load_config()
            movie_folders = config.get('movie_folders', [])

            if movie_folders:
                logger.info(f"找到 {len(movie_folders)} 个电影文件夹，开始重新扫描")
                self.scan_movies(movie_folders)

                refresh_time = time.time() - start_time
                logger.info(f"电影列表刷新完成，耗时: {refresh_time:.2f}秒")
                self.status_bar.showMessage(f"刷新完成 - {refresh_time:.1f}秒", 3000)
            else:
                logger.warning("未配置电影文件夹，提示用户添加")
                QMessageBox.information(self, '提示', '请先添加电影文件夹！')
                self.status_bar.showMessage("请先添加电影文件夹", 3000)

        except Exception as e:
            logger.exception(f"刷新电影列表失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'刷新失败：{str(e)}')
            self.status_bar.showMessage("刷新失败", 3000)

    def get_pinyin_key(self, title):
        """
        获取标题的拼音首字母
        
        用于按标题、导演或演员排序时，将中文转换为拼音首字母，
        确保中文能够按拼音正确排序。
        
        Args:
            title: 可以是字符串(标题、导演)或列表(演员列表)
            
        Returns:
            str: 拼音首字母字符串
        """
        logger.debug(f"获取拼音: {title}")

        try:
            # 处理列表类型（如演员列表）
            if isinstance(title, list):
                # 如果是列表且非空，使用第一个元素
                if title:
                    title = title[0]
                else:
                    return ''
            
            # 确保是字符串类型
            if not isinstance(title, str):
                title = str(title)
            
            # 移除括号内的内容（如年份、版本信息等）
            clean_title = re.sub(r'\([^)]*\)', '', title).strip()
            logger.debug(f"清理后的文本: {clean_title}")

            # 如果清理后为空，返回空字符串
            if not clean_title:
                return ''
            
            # 获取拼音列表
            pinyin_list = lazy_pinyin(clean_title)
            logger.debug(f"拼音列表: {pinyin_list}")

            # 提取首字母并转为小写
            pinyin_key = ''.join([p[0].lower() if p else '' for p in pinyin_list])
            logger.debug(f"拼音首字母: {pinyin_key}")

            return pinyin_key

        except Exception as e:
            logger.exception(f"获取拼音首字母失败: {str(e)}")
            # 如果拼音转换失败，使用空字符串
            return ''

    def search_movies(self, search_text):
        """
        根据搜索文本过滤电影列表
        
        支持在电影标题、年份、导演和演员中进行模糊搜索。
        当搜索文本为空时，显示完整的电影列表。
        
        Args:
            search_text (str): 用户输入的搜索文本
        """
        logger.info(f"开始搜索电影，关键词: '{search_text}'")
        start_time = time.time()
        
        try:
            # 如果搜索文本为空，恢复原始电影列表
            if not search_text.strip():
                logger.debug("搜索文本为空，恢复原始电影列表")
                self.current_movies = self.original_movies.copy()
            else:
                # 转换搜索文本为小写，用于不区分大小写的搜索
                search_text_lower = search_text.lower().strip()
                logger.debug(f"搜索文本(小写): '{search_text_lower}'")
                
                # 过滤电影列表
                filtered_movies = []
                for movie in self.original_movies:
                    # 检查标题
                    title = movie.get('title', '').lower()
                    # 检查年份（将年份转换为字符串进行比较）
                    year = str(movie.get('year', '')).lower()
                    # 检查导演（将导演列表转换为字符串）
                    director = movie.get('director', [])
                    if isinstance(director, list):
                        director_str = ' '.join(director).lower()
                    else:
                        director_str = str(director or '').lower()
                    # 检查演员（将演员列表转换为字符串）
                    actors = movie.get('actors', [])
                    actors_str = ' '.join(actors).lower()
                    
                    # 判断是否匹配搜索文本
                    if (search_text_lower in title or 
                        search_text_lower in year or 
                        search_text_lower in director_str or 
                        search_text_lower in actors_str):
                        filtered_movies.append(movie)
                
                self.current_movies = filtered_movies
            
            # 应用当前选择的排序方式
            current_sort = self.sort_combo.currentText()
            logger.debug(f"搜索后应用排序方式: {current_sort}")
            self.sort_movies(current_sort)
            
            search_time = time.time() - start_time
            movie_count = len(self.current_movies)
            logger.info(f"搜索完成，找到 {movie_count} 部匹配的电影，耗时: {search_time:.3f}秒")
            
            # 更新状态栏消息
            if search_text.strip():
                self.status_bar.showMessage(f"搜索结果: {movie_count} 部电影匹配 '{search_text}'", 3000)
            else:
                self.status_bar.showMessage(f"显示全部 {movie_count} 部电影", 2000)
                
        except Exception as e:
            logger.exception(f"搜索电影失败: {str(e)}")
            self.status_bar.showMessage("搜索失败", 3000)
    
    def sort_movies(self, sort_method):
        """
        根据选择的方法对电影进行排序
        
        支持多种排序方式：
        - 按年份降序/升序
        - 按标题拼音升序/降序
        
        排序后自动更新海报墙显示。
        
        Args:
            sort_method (str): 排序方式
        """
        logger.info(f"=" * 30)
        logger.info(f"开始排序电影列表，排序方式: {sort_method}")
        start_time = time.time()

        if not self.current_movies:
            logger.warning("当前电影列表为空，无法排序")
            return

        logger.info(f"待排序电影数量: {len(self.current_movies)}")

        try:
            if sort_method == '按年份降序':
                logger.debug("使用年份降序排序")
                self.current_movies.sort(
                    key=lambda x: (x.get('year', '0000'), x.get('title', '')),
                    reverse=True
                )
            elif sort_method == '按年份升序':
                logger.debug("使用年份升序排序")
                self.current_movies.sort(
                    key=lambda x: (x.get('year', '9999'), x.get('title', ''))
                )
            elif sort_method == '按标题升序':
                logger.debug("使用标题拼音升序排序")
                self.current_movies.sort(
                    key=lambda x: self.get_pinyin_key(x.get('title', ''))
                )
            elif sort_method == '按标题降序':
                logger.debug("使用标题拼音降序排序")
                self.current_movies.sort(
                    key=lambda x: self.get_pinyin_key(x.get('title', '')),
                    reverse=True
                )
            elif sort_method == '按导演升序':
                logger.debug("使用导演拼音升序排序")
                self.current_movies.sort(
                    key=lambda x: self.get_pinyin_key(x.get('director', '') or '')
                )
            elif sort_method == '按导演降序':
                logger.debug("使用导演拼音降序排序")
                self.current_movies.sort(
                    key=lambda x: self.get_pinyin_key(x.get('director', '') or ''),
                    reverse=True
                )
            elif sort_method == '按演员升序':
                logger.debug("使用演员拼音升序排序")
                self.current_movies.sort(
                    key=lambda x: self.get_pinyin_key(x.get('actors', []))
                )
            elif sort_method == '按演员降序':
                logger.debug("使用演员拼音降序排序")
                self.current_movies.sort(
                    key=lambda x: self.get_pinyin_key(x.get('actors', [])),
                    reverse=True
                )
            else:
                logger.warning(f"未知的排序方式: {sort_method}")
                return

            # 更新海报墙显示
            logger.info("排序完成，更新海报墙显示")
            self.poster_wall.update_posters(self.current_movies)

            sort_time = time.time() - start_time
            logger.info(f"排序完成，耗时: {sort_time:.3f}秒")

            # 更新状态栏
            movie_count = len(self.current_movies)
            self.status_bar.showMessage(f"已排序 {movie_count} 部电影 - {sort_method}", 2000)

        except Exception as e:
            logger.exception(f"排序电影列表失败: {str(e)}")
            self.status_bar.showMessage("排序失败", 3000)

    def scan_movies(self, folders):
        """
        扫描多个电影文件夹
        
        扫描指定的所有文件夹，收集电影信息，并缓存结果。
        扫描完成后自动应用当前选择的排序方式。
        
        Args:
            folders (list): 电影文件夹路径列表
        """
        logger.info("=" * 40)
        logger.info(f"开始扫描电影文件夹，共 {len(folders)} 个文件夹")
        start_time = time.time()

        try:
            all_movies = []
            folder_count = len(folders)

            # 逐个扫描文件夹
            for i, folder in enumerate(folders, 1):
                logger.info(f"正在扫描第 {i}/{folder_count} 个文件夹: {folder}")

                try:
                    # 扫描单个文件夹
                    movies = self.movie_scanner.scan_folder(folder)
                    all_movies.extend(movies)

                    logger.info(f"文件夹 '{folder}' 扫描完成，找到 {len(movies)} 部电影")

                except Exception as e:
                    logger.exception(f"扫描文件夹失败 '{folder}': {str(e)}")
                    # 继续扫描其他文件夹，不中断整个过程

            # 更新电影列表
            self.current_movies = all_movies
            self.original_movies = all_movies.copy()  # 保存原始列表用于搜索
            total_movies = len(all_movies)

            logger.info(f"所有文件夹扫描完成，总共找到 {total_movies} 部电影")

            # 应用当前选择的排序方式
            current_sort = self.sort_combo.currentText()
            logger.info(f"应用排序方式: {current_sort}")
            self.sort_movies(current_sort)

            scan_time = time.time() - start_time
            logger.info(f"电影扫描完成，总耗时: {scan_time:.2f}秒")
            logger.info(f"平均每部电影扫描耗时: {scan_time / max(total_movies, 1):.3f}秒")

            # 更新状态栏
            if total_movies > 0:
                self.status_bar.showMessage(f"扫描完成：{total_movies} 部电影 - {scan_time:.1f}秒", 5000)
            else:
                self.status_bar.showMessage("未找到电影文件，请检查文件夹设置", 5000)

        except Exception as e:
            logger.exception(f"扫描电影文件夹失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'扫描文件夹失败：{str(e)}')
            self.status_bar.showMessage("扫描失败", 3000)


def main():
    """
    程序入口函数
    
    创建QApplication实例，设置应用程序样式，
    创建并显示主窗口，启动事件循环。
    """
    logger.info("=" * 50)
    logger.info("启动本地电影海报墙应用程序")
    start_time = time.time()

    try:
        # 创建应用程序实例
        app = QApplication(sys.argv)
        logger.info("QApplication 创建成功")

        # 设置应用程序样式
        app.setStyle('Fusion')
        logger.info("应用程序样式设置为 Fusion")

        # 创建主窗口
        window = MovieWallApp()
        logger.info("主窗口创建成功")

        # 显示主窗口
        window.show()
        logger.info("主窗口已显示")

        startup_time = time.time() - start_time
        logger.info(f"应用程序启动完成，总耗时: {startup_time:.2f}秒")
        logger.info("=" * 50)

        # 启动事件循环
        sys.exit(app.exec())

    except Exception as e:
        logger.exception(f"应用程序启动失败: {str(e)}")
        # 如果是在交互式环境中，显示错误对话框
        if hasattr(sys, 'ps1') or not sys.stderr.isatty():
            try:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(None, '启动错误', f'应用程序启动失败：\n{str(e)}')
            except:
                pass
        sys.exit(1)


if __name__ == '__main__':
    main()
