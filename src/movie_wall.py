import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QListWidget,
                               QDialog, QLabel, QDialogButtonBox, QMessageBox,
                               QComboBox)
from PySide6.QtCore import Qt
from pathlib import Path
from config_manager import ConfigManager
from movie_scanner import MovieScanner
from poster_wall import PosterWall
import re
from pypinyin import lazy_pinyin


class FolderListDialog(QDialog):
    """文件夹列表对话框"""

    def __init__(self, folders, parent=None):
        super().__init__(parent)
        self.setWindowTitle('管理电影文件夹')
        self.setMinimumSize(500, 400)
        self.folders = folders.copy()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 文件夹列表
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.folders)

        # 按钮布局
        btn_layout = QHBoxLayout()
        add_btn = QPushButton('添加文件夹')
        remove_btn = QPushButton('删除选中')
        add_btn.clicked.connect(self.add_folder)
        remove_btn.clicked.connect(self.remove_folder)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)

        # 确认按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Ok).setText('确定')
        button_box.button(QDialogButtonBox.Cancel).setText('取消')

        # 添加所有组件
        layout.addWidget(QLabel('已添加的文件夹：'))
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)
        layout.addWidget(button_box)

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
                color: white;
            }
        """)

    def add_folder(self):
        """添加文件夹"""
        try:
            folders = QFileDialog.getExistingDirectory(
                self,
                '选择电影文件夹',
                options=QFileDialog.ShowDirsOnly
            )
            if folders:
                # 由于使用本地对话框，不再需要分割路径
                folder = folders  # 直接使用选择的路径
                if not folder.strip():
                    return

                # 检查文件夹是否存在且可访问
                path = Path(folder)
                if not path.exists():
                    QMessageBox.warning(self, '提示', f'文件夹不存在：{folder}')
                    return
                if not path.is_dir():
                    QMessageBox.warning(self, '提示', f'不是有效的文件夹：{folder}')
                    return
                if not os.access(path, os.R_OK):
                    QMessageBox.warning(self, '提示', f'无法访问该文件夹：{folder}')
                    return

                # 检查是否已添加
                if folder in self.folders:
                    QMessageBox.information(self, '提示', f'该文件夹已添加：{folder}')
                    return

                # 添加到列表
                self.folders.append(folder)
                self.list_widget.addItem(folder)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'添加文件夹失败：{str(e)}')

    def remove_folder(self):
        """移除文件夹"""
        current_item = self.list_widget.currentItem()
        if current_item:
            folder = current_item.text()
            self.folders.remove(folder)
            self.list_widget.takeItem(self.list_widget.row(current_item))
        else:
            QMessageBox.information(self, '提示', '请先选择要移除的文件夹！')


class MovieWallApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.movie_scanner = MovieScanner()
        self.current_movies = []  # 存储当前显示的电影列表
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('本地电影海报墙')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
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
                /* 使用Unicode三角形字符代替图片 */
                width: 12px;
                height: 12px;
                color: white;
                font-size: 12px;
            }
            QComboBox::down-arrow:on {
                /* 点击时的样式 */
                top: 1px;
                left: 1px;
            }
            QComboBox {
                padding-right: 20px; /* 为下拉箭头留出空间 */
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
        """)

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建顶部控制栏
        control_layout = QHBoxLayout()

        # 左侧按钮组
        left_buttons = QHBoxLayout()
        manage_folders_btn = QPushButton('管理文件夹')
        manage_folders_btn.clicked.connect(self.manage_folders)
        select_player_btn = QPushButton('选择播放器')
        select_player_btn.clicked.connect(self.configure_player)
        refresh_btn = QPushButton('刷新列表')
        refresh_btn.clicked.connect(self.refresh_movies)

        left_buttons.addWidget(manage_folders_btn)
        left_buttons.addWidget(select_player_btn)
        left_buttons.addWidget(refresh_btn)

        # 右侧排序选项
        right_controls = QHBoxLayout()
        sort_label = QLabel('排序方式：')
        sort_label.setStyleSheet('color: white;')
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['按年份降序', '按年份升序', '按标题升序', '按标题降序'])
        self.sort_combo.currentTextChanged.connect(self.sort_movies)

        right_controls.addWidget(sort_label)
        right_controls.addWidget(self.sort_combo)

        # 添加到控制栏
        control_layout.addLayout(left_buttons)
        control_layout.addStretch()
        control_layout.addLayout(right_controls)

        # 创建海报墙
        self.poster_wall = PosterWall(self.config_manager)

        # 添加到主布局
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.poster_wall)

        # 加载配置
        self.load_config()

    def load_config(self):
        """加载配置信息"""
        config = self.config_manager.load_config()
        if config.get('movie_folders'):
            # self.scan_movies(config['movie_folders'])
            self.current_movies = self.movie_scanner.cache_manager.get_cache()
            if len(self.current_movies) == 0:
                self.scan_movies(config['movie_folders'])
            else:
                self.sort_movies(self.sort_combo.currentText())

    def manage_folders(self):
        """管理电影文件夹"""
        try:
            config = self.config_manager.load_config()
            folders = config.get('movie_folders', [])
            dialog = FolderListDialog(folders, self)
            if dialog.exec() == QDialog.Accepted:
                self.config_manager.update_config({'movie_folders': dialog.folders})
                self.scan_movies(dialog.folders)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'管理文件夹失败：{str(e)}')

    def configure_player(self):
        """配置播放器"""
        try:
            player_path, _ = QFileDialog.getOpenFileName(
                self,
                '选择视频播放器程序',
                "",  # 起始目录为空，使用默认目录
                "可执行文件 (*.exe);;所有文件 (*.*)"
            )
            if player_path:
                # 检查文件是否存在且可执行
                path = Path(player_path)
                if not path.exists():
                    QMessageBox.warning(self, '提示', '所选播放器程序不存在！')
                    return
                if not os.access(path, os.X_OK):
                    QMessageBox.warning(self, '提示', '所选文件不是可执行程序！')
                    return

                self.config_manager.update_config({'player_path': player_path})
                QMessageBox.information(self, '提示', '播放器设置已更新！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'设置播放器失败：{str(e)}')

    def refresh_movies(self):
        """刷新电影列表"""
        self.poster_wall.clear_posters()
        try:
            config = self.config_manager.load_config()
            if config.get('movie_folders'):
                self.scan_movies(config['movie_folders'])
            else:
                QMessageBox.information(self, '提示', '请先添加电影文件夹！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'刷新失败：{str(e)}')

    def get_pinyin_key(self, title):
        """获取标题的拼音首字母"""
        # 移除括号内的内容
        title = re.sub(r'\([^)]*\)', '', title)
        # 获取拼音首字母
        pinyin_list = lazy_pinyin(title)
        return ''.join([p[0].lower() if p else '' for p in pinyin_list])

    def sort_movies(self, sort_method):
        """根据选择的方法对电影进行排序"""
        if not self.current_movies:
            return

        if sort_method == '按年份降序':
            self.current_movies.sort(
                key=lambda x: (x.get('year', '0000'), x.get('title')),
                reverse=True
            )
        elif sort_method == '按年份升序':
            self.current_movies.sort(
                key=lambda x: (x.get('year', '9999'), x.get('title'))
            )
        elif sort_method == '按标题升序':
            self.current_movies.sort(
                key=lambda x: self.get_pinyin_key(x['title'])
            )
        elif sort_method == '按标题降序':
            self.current_movies.sort(
                key=lambda x: self.get_pinyin_key(x['title']),
                reverse=True
            )

        # 更新显示
        self.poster_wall.update_posters(self.current_movies)

    def scan_movies(self, folders):
        """扫描多个电影文件夹"""
        try:
            all_movies = []
            for folder in folders:
                movies = self.movie_scanner.scan_folder(folder)
                all_movies.extend(movies)

            self.current_movies = all_movies
            # 应用当前选择的排序方式
            self.sort_movies(self.sort_combo.currentText())
        except Exception as e:
            QMessageBox.critical(self, '错误', f'扫描文件夹失败：{str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格
    window = MovieWallApp()
    window.show()
    sys.exit(app.exec())
