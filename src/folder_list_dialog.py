import os

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QListWidget,
                               QDialog, QLabel, QDialogButtonBox, QMessageBox,
                               QComboBox, QStatusBar)
from pathlib import Path


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
                color: black;
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
