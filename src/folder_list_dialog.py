"""
文件夹列表管理对话框模块

本模块实现电影文件夹管理的对话框界面，允许用户添加、删除电影文件夹路径。
对话框提供直观的管理界面，支持文件夹验证、重复检查等功能。

主要功能：
- 展示当前已添加的电影文件夹列表
- 添加新的电影文件夹路径
- 删除选中的文件夹路径
- 文件夹路径有效性验证
- 防止重复添加相同文件夹
- 用户友好的界面和反馈

UI特性：
- 暗色主题界面设计
- 列表视图显示文件夹路径
- 添加/删除按钮操作
- 标准对话框按钮（确定/取消）
- 完整的错误处理和用户提示

Author: LocalPosterWall Team
Version: 0.0.1
"""

import os
import time
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QListWidget,
                               QDialog, QLabel, QDialogButtonBox, QMessageBox,
                               QComboBox, QStatusBar)

from loguru import logger


class FolderListDialog(QDialog):
    """
    文件夹列表管理对话框
    
    用于管理电影文件夹路径的对话框组件，提供：
    - 文件夹列表的显示和管理
    - 添加新文件夹的功能
    - 删除选中文件夹的功能
    - 文件夹路径的有效性验证
    - 防止重复添加的检查机制
    
    用户通过此对话框可以方便地管理多个电影文件夹。
    """
    
    def __init__(self, folders, parent=None):
        """
        初始化文件夹列表对话框
        
        Args:
            folders (list): 初始文件夹路径列表
            parent (QWidget, optional): 父窗口组件
        """
        logger.info("创建文件夹列表管理对话框")
        start_time = time.time()
        
        super().__init__(parent)
        
        # 保存文件夹列表（创建副本避免修改原始数据）
        self.folders = folders.copy() if folders else []
        logger.debug(f"初始文件夹列表: {self.folders}")
        
        # 设置对话框属性
        self._setup_dialog_properties()
        
        # 设置用户界面
        self.setup_ui()
        
        init_time = time.time() - start_time
        logger.debug(f"文件夹列表对话框初始化完成，耗时: {init_time:.3f}秒")
    
    def _setup_dialog_properties(self):
        """设置对话框基本属性"""
        logger.debug("设置文件夹管理对话框属性")
        
        # 设置窗口标题
        self.setWindowTitle('管理电影文件夹')
        logger.debug("对话框标题设置完成")
        
        # 设置最小尺寸
        self.setMinimumSize(500, 400)
        logger.debug("对话框最小尺寸设置: 500x400")
        
        # 设置为模态对话框
        self.setModal(True)
        logger.debug("设置为模态对话框")
    
    def setup_ui(self):
        """
        设置用户界面
        
        创建对话框的完整UI布局，包括：
        - 文件夹列表显示区域
        - 添加/删除按钮组
        - 确定/取消按钮
        - 样式设置
        """
        logger.debug("设置文件夹管理对话框UI")
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        logger.debug("主布局创建完成")
        
        # 创建文件夹列表
        self._create_folder_list(layout)
        
        # 创建按钮组
        self._create_button_group(layout)
        
        # 创建确认按钮
        self._create_confirm_buttons(layout)
        
        # 应用对话框样式
        self._apply_dialog_style()
        
        logger.debug("文件夹管理对话框UI设置完成")
    
    def _create_folder_list(self, layout):
        """
        创建文件夹列表显示区域
        
        Args:
            layout (QVBoxLayout): 父布局管理器
        """
        logger.debug("创建文件夹列表")
        
        # 添加说明标签
        label = QLabel('已添加的电影文件夹：')
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px 0px;
            }
        """)
        layout.addWidget(label)
        logger.debug("说明标签创建完成")
        
        # 创建文件夹列表组件
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.folders)
        logger.debug(f"文件夹列表创建完成，当前包含 {len(self.folders)} 个文件夹")
        
        layout.addWidget(self.list_widget)
        logger.debug("文件夹列表已添加到布局")
    
    def _create_button_group(self, layout):
        """
        创建操作按钮组
        
        Args:
            layout (QVBoxLayout): 父布局管理器
        """
        logger.debug("创建操作按钮组")
        
        # 创建按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # 添加文件夹按钮
        add_btn = QPushButton('添加文件夹')
        add_btn.clicked.connect(self.add_folder)
        add_btn.setToolTip("添加新的电影文件夹路径")
        btn_layout.addWidget(add_btn)
        logger.debug("添加文件夹按钮创建完成")
        
        # 删除选中按钮
        remove_btn = QPushButton('删除选中')
        remove_btn.clicked.connect(self.remove_folder)
        remove_btn.setToolTip("删除当前选中的文件夹")
        btn_layout.addWidget(remove_btn)
        logger.debug("删除文件夹按钮创建完成")
        
        # 添加按钮组到主布局
        layout.addLayout(btn_layout)
        logger.debug("操作按钮组已添加到布局")
    
    def _create_confirm_buttons(self, layout):
        """
        创建确认按钮组
        
        Args:
            layout (QVBoxLayout): 父布局管理器
        """
        logger.debug("创建确认按钮组")
        
        # 创建标准对话框按钮
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        
        # 连接信号
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # 设置按钮文本
        ok_btn = self.button_box.button(QDialogButtonBox.Ok)
        ok_btn.setText('确定')
        ok_btn.setToolTip("确认并保存文件夹列表")
        
        cancel_btn = self.button_box.button(QDialogButtonBox.Cancel)
        cancel_btn.setText('取消')
        cancel_btn.setToolTip("取消操作，不保存更改")
        
        layout.addWidget(self.button_box)
        logger.debug("确认按钮组创建完成")
    
    def _apply_dialog_style(self):
        """应用对话框样式"""
        logger.debug("应用文件夹管理对话框样式")
        
        style = """
            QDialog {
                background-color: #f5f5f5;
            }
            QListWidget {
                background-color: #222;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: #444;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 2px;
                margin: 1px 0px;
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
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """
        
        self.setStyleSheet(style)
        logger.debug("文件夹管理对话框样式应用完成")
    
    def add_folder(self):
        """
        添加新的文件夹
        
        打开文件夹选择对话框，验证所选文件夹的有效性，
        并将其添加到列表中（如果未重复）。
        """
        logger.info("开始添加新文件夹")
        start_time = time.time()
        
        try:
            # 打开文件夹选择对话框
            logger.debug("打开文件夹选择对话框")
            selected_folder = QFileDialog.getExistingDirectory(
                self,
                '选择电影文件夹',
                options=QFileDialog.ShowDirsOnly
            )
            
            if not selected_folder:
                logger.info("用户取消文件夹选择")
                return
            
            logger.debug(f"用户选择的文件夹: {selected_folder}")
            
            # 验证文件夹路径
            if not self._validate_folder(selected_folder):
                return
            
            # 检查是否已存在
            if self._is_duplicate_folder(selected_folder):
                return
            
            # 添加到列表
            self.folders.append(selected_folder)
            self.list_widget.addItem(selected_folder)
            
            logger.info(f"成功添加文件夹: {selected_folder}")
            logger.info(f"当前文件夹总数: {len(self.folders)}")
            
            # 显示成功提示
            QMessageBox.information(
                self,
                '成功',
                f'文件夹已添加：\n{selected_folder}'
            )
            
        except Exception as e:
            logger.exception(f"添加文件夹时发生错误: {str(e)}")
            QMessageBox.critical(
                self,
                '错误',
                f'添加文件夹失败：{str(e)}'
            )
    
    def _validate_folder(self, folder_path):
        """
        验证文件夹路径的有效性
        
        Args:
            folder_path (str): 要验证的文件夹路径
            
        Returns:
            bool: 如果文件夹有效返回True，否则返回False
        """
        logger.debug(f"验证文件夹路径: {folder_path}")
        
        try:
            # 检查路径是否为空
            if not folder_path or not folder_path.strip():
                logger.warning("文件夹路径为空")
                QMessageBox.warning(self, '提示', '文件夹路径不能为空！')
                return False
            
            # 转换为Path对象
            path = Path(folder_path)
            
            # 检查文件夹是否存在
            if not path.exists():
                logger.warning(f"文件夹不存在: {folder_path}")
                QMessageBox.warning(self, '提示', f'文件夹不存在：\n{folder_path}')
                return False
            
            # 检查是否为目录
            if not path.is_dir():
                logger.warning(f"路径不是文件夹: {folder_path}")
                QMessageBox.warning(self, '提示', f'不是有效的文件夹：\n{folder_path}')
                return False
            
            # 检查是否有读取权限
            if not os.access(path, os.R_OK):
                logger.warning(f"无法访问文件夹: {folder_path}")
                QMessageBox.warning(self, '提示', f'无法访问该文件夹：\n{folder_path}')
                return False
            
            logger.debug(f"文件夹验证通过: {folder_path}")
            return True
            
        except Exception as e:
            logger.exception(f"验证文件夹时发生错误: {str(e)}")
            QMessageBox.critical(
                self,
                '错误',
                f'验证文件夹失败：{str(e)}'
            )
            return False
    
    def _is_duplicate_folder(self, folder_path):
        """
        检查文件夹是否已存在
        
        Args:
            folder_path (str): 要检查的文件夹路径
            
        Returns:
            bool: 如果已存在返回True，否则返回False
        """
        logger.debug(f"检查重复文件夹: {folder_path}")
        
        # 规范化路径进行比较
        normalized_path = str(Path(folder_path).resolve())
        
        for existing_folder in self.folders:
            existing_normalized = str(Path(existing_folder).resolve())
            if normalized_path == existing_normalized:
                logger.warning(f"文件夹已存在: {folder_path}")
                QMessageBox.information(
                    self,
                    '提示',
                    f'该文件夹已添加：\n{folder_path}'
                )
                return True
        
        logger.debug(f"文件夹不重复: {folder_path}")
        return False
    
    def remove_folder(self):
        """
        删除选中的文件夹
        
        从列表中移除当前选中的文件夹路径。
        """
        logger.info("开始删除文件夹")
        
        try:
            # 获取当前选中的项目
            current_item = self.list_widget.currentItem()
            
            if not current_item:
                logger.debug("没有选中要删除的文件夹")
                QMessageBox.information(self, '提示', '请先选择要移除的文件夹！')
                return
            
            # 获取文件夹路径
            folder_path = current_item.text()
            logger.debug(f"选中的文件夹: {folder_path}")
            
            # 从内存列表中移除
            if folder_path in self.folders:
                self.folders.remove(folder_path)
                logger.debug(f"从内存列表中移除: {folder_path}")
            
            # 从UI列表中移除
            current_row = self.list_widget.row(current_item)
            self.list_widget.takeItem(current_row)
            logger.debug(f"从UI列表中移除第 {current_row} 项")
            
            logger.info(f"成功删除文件夹: {folder_path}")
            logger.info(f"当前文件夹总数: {len(self.folders)}")
            
        except Exception as e:
            logger.exception(f"删除文件夹时发生错误: {str(e)}")
            QMessageBox.critical(
                self,
                '错误',
                f'删除文件夹失败：{str(e)}'
            )
    
    def get_folders(self):
        """
        获取当前文件夹列表
        
        Returns:
            list: 当前管理的文件夹路径列表
        """
        logger.debug(f"获取文件夹列表，当前包含 {len(self.folders)} 个文件夹")
        return self.folders.copy()
    
    def accept(self):
        """
        确认操作
        
        用户点击确定按钮时调用，验证数据并关闭对话框。
        """
        logger.info("用户确认文件夹列表管理")
        
        try:
            # 检查是否有至少一个文件夹
            if len(self.folders) == 0:
                logger.warning("文件夹列表为空")
                reply = QMessageBox.question(
                    self,
                    '确认',
                    '当前没有添加任何文件夹，确定要保存吗？',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    logger.info("用户取消空列表保存")
                    return
            
            logger.info(f"确认保存文件夹列表，共 {len(self.folders)} 个文件夹")
            logger.debug(f"最终文件夹列表: {self.folders}")
            
            # 调用父类的accept方法关闭对话框
            super().accept()
            
        except Exception as e:
            logger.exception(f"确认操作时发生错误: {str(e)}")
            QMessageBox.critical(
                self,
                '错误',
                f'保存失败：{str(e)}'
            )
    
    def reject(self):
        """
        取消操作
        
        用户点击取消按钮时调用，不保存更改并关闭对话框。
        """
        logger.info("用户取消文件夹列表管理")
        
        try:
            # 调用父类的reject方法关闭对话框
            super().reject()
            
        except Exception as e:
            logger.exception(f"取消操作时发生错误: {str(e)}")
            # 即使出错也尝试关闭对话框
            super().reject()
